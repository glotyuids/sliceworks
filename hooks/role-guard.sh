#!/bin/sh
# sliceworks 0.8.0. Role guard, keyed on the acting role (lib.sh sw_agent_type: the agent_type of the hook input, as
# plugin agents cannot carry their own hooks; under Codex, the role its launcher gave a worker process). The main
# session has no role and is never guarded here. A Codex patch naming several files is checked file by file.
#   slice-implementer : budget stop line; no push, merge, switch, history rewrite, worktree or infrastructure
#                       commands; no writes to protected files (Edit/Write path and Bash write targets in the
#                       main checkout); no secrets. Denials are logged to <main>/.run/guard-denials.jsonl.
#   contract-author   : writes only the contract surfaces (SW_CONTRACT_SURFACES).
#   efficiency-reviewer: writes only under the retros directory; Bash is read-only.
#   researcher        : writes only inside an open round (SW_ROUNDS_DIR/<round>/ without .closed); Bash is read-only.
#   architect         : writes only the design surfaces (SW_DESIGN_SURFACES).
#   business-analyst, system-analyst, code-reviewer, named-risk-reviewer, code-explorer: read-only; no Edit/Write, no Bash writes.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
type="$(sw_agent_type)"; [ -n "$type" ] || exit 0
tool="$(sw_field '.tool_name')"
path="$(sw_field '.tool_input.file_path // .tool_input.path')"
cmd="$(sw_field '.tool_input.command')"
if [ "$(sw_field '.tool_input.file_paths | length')" -gt 1 ] 2>/dev/null; then
  sw_field '.tool_input.file_paths[]' | while IFS= read -r p; do
    out="$(printf '%s' "$input" | jq -c --arg p "$p" '.tool_input.file_path = $p | .tool_input.file_paths = [$p]' | sh "$0")"
    [ -z "$out" ] || { printf '%s\n' "$out"; break; }
  done
  exit 0
fi

if sw_is_role "$type" efficiency-reviewer; then
  case "$tool" in
    Edit|Write|MultiEdit)
      case "$path" in */"$SW_RETROS_DIR"/*|"$SW_RETROS_DIR"/*) exit 0;; *) sw_deny "The efficiency reviewer writes only under $SW_RETROS_DIR (method 9).";; esac;;
    Bash)
      case "$cmd" in *">"*|*" tee "*|*"sed -i"*|*"rm "*|*"mv "*|*"git commit"*|*"git add"*|*"git checkout"*|*"git reset"*|*"git push"*|*"git merge"*|*"git rebase"*)
        sw_deny "The efficiency reviewer is read-only outside $SW_RETROS_DIR; use Write for proposal files.";; esac;;
  esac
  exit 0
fi

ro_bash() { case "$cmd" in *">"*|*" tee "*|*"sed -i"*|*"rm "*|*"mv "*|*"git commit"*|*"git add"*|*"git checkout"*|*"git reset"*|*"git push"*|*"git merge"*|*"git rebase"*) sw_deny "$1";; esac; }

for ro in business-analyst system-analyst code-reviewer named-risk-reviewer code-explorer; do
  if sw_is_role "$type" "$ro"; then
    case "$tool" in
      Edit|Write|MultiEdit) sw_deny "The $ro is read-only (method 2 and 17); it returns its analysis as a message.";;
      Bash) ro_bash "The $ro is read-only; no writes, commits or checkouts.";;
    esac
    exit 0
  fi
done

if sw_is_role "$type" researcher; then
  case "$tool" in
    Edit|Write|MultiEdit)
      rel="$(sw_rel "$path")"
      case "$rel" in "$SW_ROUNDS_DIR"/*/*)
        rdir="$SW_ROOT/$(printf '%s' "$rel" | awk -F/ -v n="$(printf '%s' "$SW_ROUNDS_DIR" | awk -F/ '{print NF}')" '{ s=$1; for (i=2;i<=n+1;i++) s=s"/"$i; print s }')"
        [ -f "$rdir/.closed" ] && sw_deny "Round $(basename "$rdir") is closed; open a new round (method 13)."
        exit 0;;
      *) sw_deny "The researcher writes only inside the open round under $SW_ROUNDS_DIR (method 13). Asked path: $path";; esac;;
    Bash) ro_bash "The researcher is read-only outside its round; use Write for register rows.";;
  esac
  exit 0
fi

if sw_is_role "$type" architect; then
  case "$tool" in Edit|Write|MultiEdit) ;; *) exit 0;; esac
  rel="$(sw_rel "$path")"
  for s in $SW_DESIGN_SURFACES; do case "$rel" in "$s"*|*"/$s"*) exit 0;; esac; done
  sw_deny "The architect writes only the design surfaces ($SW_DESIGN_SURFACES). Asked path: $path"
fi

if sw_is_role "$type" contract-author; then
  case "$tool" in Edit|Write|MultiEdit) ;; *) exit 0;; esac
  for s in $SW_CONTRACT_SURFACES; do case "$path" in */"$s"*|"$s"*) exit 0;; esac; done
  sw_deny "The contract author writes only the contract surfaces (${SW_CONTRACT_SURFACES:-none configured: set SW_CONTRACT_SURFACES in .sliceworks/config.env}). Asked path: $path"
fi

sw_is_role "$type" slice-implementer || exit 0

log_deny() { # log_deny <rule> <reason>
  {
    cwd="$(sw_field '.cwd')"; slice=""
    for d in "$cwd" "${CLAUDE_PROJECT_DIR:-}"; do
      [ -n "$d" ] || continue
      r="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" || continue
      [ -f "$r/.slice" ] && { slice="$(head -n 1 "$r/.slice" | tr -d '\r\n')"; break; }
    done
    what="${cmd:-$path}"
    mkdir -p "$SW_ROOT/$SW_RUN_DIR" && jq -cn --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg slice "$slice" --arg tool "$tool" --arg rule "$1" --arg cmd "$what" \
      '{at:$at, slice:(if $slice == "" then null else $slice end), tool:$tool, rule:$rule, cmd:$cmd[0:120]}' >>"$SW_ROOT/$SW_RUN_DIR/guard-denials.jsonl"
  } 2>/dev/null || true
  sw_deny "$2"
}

verdict="$(sw_budget_verdict)"
case "$verdict" in stop*) case "$tool" in Bash|Edit|Write|MultiEdit)
  case "$cmd" in *"git commit"*|*"git add"*|*".blocked"*) ;; *) log_deny budget-stop "Budget stop: ${verdict#stop }. Commit what passes, create .blocked at your worktree root, append a dated note to $SW_PROGRESS_FILE and return HOLD budget-stop." ;; esac ;; esac ;; esac

wt_re="$(printf '%s' "$SW_WORKTREE_ROOT" | sed -e 's#[][\.*^$+?(){}|#/]#\\&#g')"
unwt() { sed -E "s#/${wt_re}/[^/ ]+/#/#g"; }
ere() { printf '%s' "$1" | sed -e 's/[][\.*^$+?(){}|#]/\\&/g'; }

case "$tool" in
  Bash)
    [ -n "$cmd" ] || exit 0
    raw="$cmd"; c="$(printf '%s' "$cmd" | unwt)"
    case "$c" in *sliceworks-role*) log_deny role-marker "The role marker is the launcher's; implementers never touch it.";; esac
    case "$c" in *pkill*|*killall*) log_deny process-ban "Implementers do not use pkill or killall (they match other slices' and the coordinator's runs). Stop only your own process with kill <pid>.";; esac
    case "$(printf '%s' "$c" | sed 's/git merge-base//g')" in *"git merge"*) log_deny git-ban "Implementers do not push, merge, switch branches, rewrite history or manage worktrees (method 2). Commit on your slice branch and return CANDIDATE or BLOCKED.";; esac
    case "$c" in
      *"git push"*|*"git switch"*|*"git reset --hard"*|*"git worktree"*|*"git branch -D"*|*"git branch -d"*|*"git rebase -i"*|*"gh pr"*|*"git checkout -b"*|*"git checkout $SW_INTEGRATION_BRANCH"*)
        log_deny git-ban "Implementers do not push, merge, switch branches, rewrite history or manage worktrees (method 2). Commit on your slice branch and return CANDIDATE or BLOCKED.";;
    esac
    old_ifs="$IFS"; IFS='|'; for pat in $SW_INFRA_DENY; do case "$c" in *"$pat"*) IFS="$old_ifs"; log_deny infra "Implementers never contact cloud, cluster or provider infrastructure, and never remove shared containers (method 10).";; esac; done; IFS="$old_ifs"
    # Writes inside the worktree are caught by the T0/T1 diff gate. A write target naming <main>/<protected path>,
    # or reaching one by a ../ climb, is invisible to that gate and is refused here; so is an interpreter command
    # naming <main>/<protected path>, and any command that enters the main checkout and names a protected path.
    mr=""; for r in $(sw_roots); do mr="${mr:+$mr|}$(ere "$r")"; done; mr="($mr)"
    t="$(printf '%s\n' "$raw" | sed -e "s#~/#${HOME:-/nonexistent}/#g" -e 's#\${HOME}/#'"${HOME:-/nonexistent}"'/#g' -e 's#\$HOME/#'"${HOME:-/nonexistent}"'/#g' -e "s#${wt_re}/#<worktree>/#g")"
    segs="$(printf '%s\n' "$t" | sed -E 's/(&&|\|\||;|\|)/\n/g')"
    inmain=0
    printf '%s\n' "$t" | grep -Eq "(^|[[:space:];&|(])(cd|pushd|git[[:space:]]+-C)[[:space:]]+[\"']?${mr}(/?[\"']?([[:space:];&|)]|$)|/[^<])" && inmain=1
    for p in $SW_PROTECTED; do
      rp="$(ere "$p")"; rx="(${mr}/${rp}|(\.\./)+${rp})"
      if printf '%s\n' "$segs" | grep -Eq ">>?[[:space:]]*[\"']?[^[:space:];|&]*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])tee([[:space:]]+-[a-z]+)*[[:space:]]+([^;|&]*[[:space:]])?[\"']?[^[:space:];|&]*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])sed[[:space:]]+(-[a-zA-Z]+[[:space:]]+)*-i.*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])perl[[:space:]].*-[a-zA-Z]*i.*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])dd[[:space:]].*of=[\"']?[^[:space:]]*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])(rm|mv|ln|truncate|install)[[:space:]].*${rx}" \
        || printf '%s\n' "$segs" | grep -Eq "(^|[[:space:]])cp[[:space:]].*[[:space:]][\"']?[^[:space:]]*${rx}[^[:space:]]*[\"']?[[:space:]]*$" \
        || { printf '%s\n' "$t" | grep -Eq "(^|[[:space:]/])(python[0-9.]*|perl|ruby|node)([[:space:]]|$)" && printf '%s\n' "$t" | grep -Eq "${mr}/${rp}"; } \
        || { [ "$inmain" = 1 ] && printf '%s\n' "$t" | grep -Eq "${rp}"; }; then
        log_deny main-protected-write "Only the coordinator writes $p, and the main checkout is not yours: work in your worktree (T0 fails on any protected path in your diff). Implementers append to $SW_PROGRESS_FILE only."
      fi
    done;;
  Edit|Write|MultiEdit)
    [ -n "$path" ] || exit 0
    p2="$(printf '%s' "$path" | unwt)"
    for p in $SW_PROTECTED; do case "$p2" in *"/$p"*|"$p"*) log_deny protected-path "Only the coordinator writes $p; implementers append to $SW_PROGRESS_FILE only.";; esac; done
    case "$p2" in *.tfvars|*/.secrets/*|*.secret*|*/.env|*.pem|*.key) log_deny secrets "Secrets are never written or read by implementers.";; esac;;
esac
exit 0
