#!/bin/sh
# sliceworks 0.2.0. Stop hook for the main session: a turn may always end; when the kill switch is present
# the message says so, so a resumed coordinator does not re-dispatch until the owner removes STOP.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
if [ -f "$SW_ROOT/$SW_STOP_FILE" ]; then
  jq -n --arg f "$SW_STOP_FILE" '{systemMessage:("STOP kill switch is present (" + $f + "). The run stays halted until the owner removes the file.")}'
fi
exit 0
