# sliceworks 0.2.0: shared helpers for the hooks. POSIX sh, needs jq.
# Sourced after `input="$(cat)"`. Every hook calls sw_load_config and exits 0 when it returns 1.

sw_root() {
  # The main checkout root: CLAUDE_PROJECT_DIR, or the git common dir (a worktree's common dir is <main>/.git).
  local d="${CLAUDE_PROJECT_DIR:-$(pwd)}" c
  c="$(git -C "$d" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
  case "$c" in */.git) printf '%s' "${c%/.git}"; return;; esac
  printf '%s' "$d" | sed -E 's#/\.claude/worktrees/.*$##'
}

sw_load_config() {
  SW_ROOT="$(sw_root)"
  SW_CONFIG="$SW_ROOT/.sliceworks/config.env"
  [ -f "$SW_CONFIG" ] || return 1
  # defaults, then the project's values
  SW_STATE_DIR="docs/process"; SW_OUTPUTS_DIR="outputs"; SW_RUN_DIR=".run"
  SW_INTEGRATION_BRANCH="main"; SW_SLICE_BRANCH_PREFIX="slice/"; SW_WORKTREE_ROOT=".claude/worktrees"
  SW_VERIFY_CMD="scripts/dev/verify-slice.sh"; SW_T0_ARGS="t0"
  SW_WEEKLY_DISPATCH_HOLD=80; SW_WEEKLY_STOP=85; SW_FIVE_HOUR_DISPATCH_HOLD=90; SW_FIVE_HOUR_STOP=100
  SW_READING_MAX_AGE=5400; SW_OWNER_SHARE_PCT=15
  SW_EXPLORER_AGENTS="Explore Plan claude-code-guide code-explorer sliceworks:code-explorer"
  SW_INFRA_DENY="kubectl| helm |terraform| yc |ansible|docker push|docker rm|docker stop"
  SW_CONTRACT_SURFACES=""
  SW_PROTECTED_EXTRA=""
  SW_DESIGN_SURFACES=""
  SW_MONEY_CAP=0; SW_MONEY_CURRENCY=USD; SW_PAID_CMDS=""
  # shellcheck disable=SC1090
  . "$SW_CONFIG"
  SW_STOP_FILE="${SW_STOP_FILE:-$SW_STATE_DIR/STOP}"
  SW_USAGE_FILE="${SW_USAGE_FILE:-$SW_STATE_DIR/metrics/usage.jsonl}"
  SW_RETROS_DIR="${SW_RETROS_DIR:-$SW_STATE_DIR/retros}"
  SW_PROGRESS_FILE="${SW_PROGRESS_FILE:-$SW_STATE_DIR/PROGRESS.md}"
  SW_ROUNDS_DIR="${SW_ROUNDS_DIR:-$SW_STATE_DIR/rounds}"
  SW_MONEY_FILE="${SW_MONEY_FILE:-$SW_STATE_DIR/metrics/money.jsonl}"
  [ -n "$SW_DESIGN_SURFACES" ] || SW_DESIGN_SURFACES="$SW_STATE_DIR/ARCHITECTURE.md $SW_STATE_DIR/INVARIANTS.md $SW_STATE_DIR/SCENARIOS.json $SW_STATE_DIR/MILESTONES.md $SW_STATE_DIR/threat-models/ $SW_STATE_DIR/INDEX.md specs/"
  SW_PROTECTED="${SW_PROTECTED:-$SW_STATE_DIR/FEATURES.json $SW_STATE_DIR/STATE.md $SW_STATE_DIR/OWNER-DECISIONS.md $SW_STATE_DIR/NEEDS-HUMAN.md $SW_STATE_DIR/BACKLOG.md $SW_STATE_DIR/STATUS.md CLAUDE.md AGENTS.md .claude/ .sliceworks/ $SW_PROTECTED_EXTRA}"
  return 0
}

sw_deny() { # sw_deny <reason>: PreToolUse deny, then exit 0
  jq -n --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

sw_epoch() { # ISO 8601 (Z or offset) or an integer epoch -> epoch seconds; 0 when unreadable
  case "$1" in
    '') echo 0; return;;
    *[!0-9]*) ;;
    *) printf '%s\n' "$1"; return;;
  esac
  local s; s="$(printf '%s' "$1" | cut -c1-19)Z"
  date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$s" +%s 2>/dev/null \
    || date -u -d "$1" +%s 2>/dev/null \
    || python3 -c 'import sys,datetime as d; print(int(d.datetime.fromisoformat(sys.argv[1].replace("Z","+00:00")).timestamp()))' "$1" 2>/dev/null \
    || echo 0
}

sw_field() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null; }

# The main checkout may be named by its canonical path (git resolves symlinks: /private/var/...) or by the
# path the host passed (/var/...). Every path or command comparison considers both spellings.
sw_roots() {
  printf '%s\n' "$SW_ROOT"
  [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ "$CLAUDE_PROJECT_DIR" != "$SW_ROOT" ] && printf '%s\n' "$CLAUDE_PROJECT_DIR"
  local c; c="$(sw_field '.cwd')"
  if [ -n "$c" ]; then local t; t="$(git -C "$c" rev-parse --show-toplevel 2>/dev/null || true)"; [ -n "$t" ] && [ "$t" != "$SW_ROOT" ] && [ "$t" != "${CLAUDE_PROJECT_DIR:-}" ] && printf '%s\n' "$t"; fi
  return 0
}

sw_rel() { # sw_rel <path>: the path relative to the main checkout, whichever spelling of the root it uses
  local p="$1" r
  for r in $(sw_roots); do case "$p" in "$r"/*) printf '%s' "${p#"$r"/}"; return;; esac; done
  printf '%s' "$p"
}

sw_agent_type() { sw_field '.agent_type'; }

sw_is_role() { # sw_is_role <agent_type> <role>: matches "<role>" or "<anything>:<role>"
  case "$1" in "$2"|*":$2") return 0;; *) return 1;; esac
}

sw_budget_verdict() { # prints "stop <reason>" or "ok"
  local f="$SW_ROOT/$SW_USAGE_FILE" last weekly five w v
  [ -s "$f" ] || { echo ok; return; }
  last="$(tail -n 1 "$f")"
  weekly="$(printf '%s' "$last" | jq -r '.weekly_pct // 0' 2>/dev/null)"; five="$(printf '%s' "$last" | jq -r '.five_hour_pct // 0' 2>/dev/null)"
  w=${weekly%.*}; v=${five%.*}
  if [ "${w:-0}" -ge "$SW_WEEKLY_STOP" ]; then echo "stop weekly ${weekly}% is at or above the ${SW_WEEKLY_STOP}% stop line (the owner keeps ${SW_OWNER_SHARE_PCT}%)"; return; fi
  if [ "${v:-0}" -ge "$SW_FIVE_HOUR_STOP" ]; then echo "stop five-hour ${five}% is at the limit"; return; fi
  echo ok
}
