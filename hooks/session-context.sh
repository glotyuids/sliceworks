#!/bin/sh
# sliceworks 0.2.0. SessionStart: one short paragraph of context for a project that adopted the method.
# Plain stdout becomes session context. Nothing is printed for other projects.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
stop="absent"; [ -f "$SW_ROOT/$SW_STOP_FILE" ] && stop="PRESENT (the run is halted)"
reading="none"; f="$SW_ROOT/$SW_USAGE_FILE"
[ -s "$f" ] && reading="$(tail -n 1 "$f" | jq -r '"weekly \(.weekly_pct // "?")% at \(.at // "?")"' 2>/dev/null)"
cat <<TXT
This project runs under sliceworks (profile: ${SW_PROFILE:-full}). State files: $SW_STATE_DIR. To act as the coordinator read $SW_STATE_DIR/START.md first, then STATE.md, the tail of PROGRESS.md and NEEDS-HUMAN.md, and the recovery file $SW_RUN_DIR/coordinator-session.md if it exists. Kill switch $SW_STOP_FILE: $stop. Last usage reading: $reading. Dispatch holds: weekly ${SW_WEEKLY_DISPATCH_HOLD}%, five-hour ${SW_FIVE_HOUR_DISPATCH_HOLD}%; stop line ${SW_WEEKLY_STOP}%. Messages between coordinator and implementers: BRIEF, CANDIDATE, BLOCKED, FINDINGS, CONTRACT, HOLD only.
TXT
exit 0
