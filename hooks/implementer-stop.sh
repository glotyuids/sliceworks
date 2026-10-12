#!/bin/sh
# sliceworks 0.2.0. SubagentStop gate for slice implementers (method 3, step 4; method 5, T0): a turn may end
# only when T0 is green in the implementer's worktree. Escapes: stop_hook_active (already blocked once this
# turn), a .blocked marker at the worktree root (BLOCKED/HOLD return), the budget stop line, the kill switch.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
type="$(sw_agent_type)"; sw_is_role "$type" slice-implementer || exit 0
[ "$(sw_field '.stop_hook_active')" = "true" ] && exit 0
cwd="$(sw_field '.cwd')"; [ -n "$cwd" ] || cwd="$(pwd)"
root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || echo "$cwd")"
[ -f "$root/.blocked" ] && exit 0
case "$(sw_budget_verdict)" in stop*) exit 0;; esac
[ -f "$SW_ROOT/$SW_STOP_FILE" ] && exit 0
script="$root/$SW_VERIFY_CMD"; [ -x "$script" ] || script="$SW_ROOT/$SW_VERIFY_CMD"
[ -x "$script" ] || { echo "sliceworks: T0 gate skipped, no executable at $SW_VERIFY_CMD (set SW_VERIFY_CMD in .sliceworks/config.env)" >&2; exit 0; }
# shellcheck disable=SC2086
out="$(cd "$root" && "$script" $SW_T0_ARGS 2>&1)"; status=$?
if [ "$status" -ne 0 ]; then
  log="$(printf '%s\n' "$out" | sed -n 's/^LOG=//p' | tail -n 1)"
  echo "T0 is red in $root; fix it before ending the turn. Log: ${log:-none}. Tail: $(printf '%s\n' "$out" | tail -n 25 | tr '\n' ' ' | head -c 2000)" >&2
  exit 2
fi
exit 0
