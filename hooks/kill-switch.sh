#!/bin/sh
# sliceworks 0.2.0. Kill switch (method 10): while the STOP file exists, every Agent, Bash, Edit and Write
# call in the project is refused, so dispatch and edits halt mechanically. Remove the file to resume.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
stop="$SW_ROOT/$SW_STOP_FILE"
if [ -f "$stop" ]; then
  note="$(head -c 200 "$stop" 2>/dev/null | tr '\n' ' ')"
  sw_deny "STOP kill switch present at $stop ($note). Dispatch and edits are halted; remove the file to resume."
fi
exit 0
