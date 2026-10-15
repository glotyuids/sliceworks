#!/bin/sh
# sliceworks 0.8.1. Stop hook for the main session. When the kill switch is present the message says so, so a resumed
# coordinator does not re-dispatch until the owner removes STOP. Otherwise a Claude Code turn may always end: the host
# delivers background completions itself.
# Codex delivers none, so there (SW_CODEX_CONTINUE=1) the hook keeps the run going: while worker processes of
# scripts/runtimes/codex/dispatch.sh have finished unread, it blocks the stop and hands their return lines to the
# coordinator as its next prompt; while some still run, it waits up to SW_CODEX_WAIT seconds for one to finish and
# then blocks either way, so the coordinator wakes about once per window. Nothing running and nothing unread, the
# budget stop line, or the kill switch: the turn ends.
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
sw_plugin_hooks_enabled || exit 0
[ -z "$(sw_agent_type)" ] || exit 0
if [ -f "$SW_ROOT/$SW_STOP_FILE" ]; then
  jq -n --arg f "$SW_STOP_FILE" '{systemMessage:("STOP kill switch is present (" + $f + "). The run stays halted until the owner removes the file.")}'
  exit 0
fi
[ "$(sw_runtime)" = codex ] && [ "${SW_CODEX_CONTINUE:-1}" = 1 ] || exit 0
case "$(sw_budget_verdict)" in stop*) exit 0;; esac
reg="$SW_ROOT/$SW_RUN_DIR/codex"; [ -d "$reg" ] || exit 0
seen="$reg/seen"; touch "$seen"
unread() { for d in "$SW_ROOT/$SW_OUTPUTS_DIR"/slices/*/codex/*.done; do [ -f "$d" ] && ! grep -qxF "$d" "$seen" && printf '%s\n' "$d"; done; return 0; }
running() { for f in "$reg"/*.pid; do [ -f "$f" ] && kill -0 "$(cat "$f")" 2>/dev/null && basename "$f" .pid; done; return 0; }
new="$(unread)"
if [ -z "$new" ] && [ -n "$(running)" ]; then
  waited=0; limit="${SW_CODEX_WAIT:-540}"
  while [ "$waited" -lt "$limit" ] && [ -z "$new" ] && [ -n "$(running)" ] && [ ! -f "$SW_ROOT/$SW_STOP_FILE" ]; do
    sleep 10; waited=$((waited + 10)); new="$(unread)"
  done
fi
live="$(running | tr '\n' ' ')"
if [ -n "$new" ]; then
  lines="$(printf '%s\n' "$new" | while IFS= read -r d; do
    b="${d%.done}"; printf '%s: %s; ' "${b#"$SW_ROOT"/}" "$(head -n 1 "$b.last" 2>/dev/null || echo "no final message, exit $(cut -d' ' -f1 "$d")")"
  done)"
  printf '%s\n' "$new" >>"$seen"
  jq -n --arg r "Codex workers finished: ${lines}Collect them (scripts/collect.py), then review, repair or merge as the method says, dispatch what is ready, and continue the run.${live:+ Still running: $live}" '{decision:"block", reason:$r}'
elif [ -n "$live" ]; then
  jq -n --arg r "Codex workers still running: $live. Nothing has finished yet. Do any other ready coordinator work (collect, brief, review), or end the turn again to keep waiting." '{decision:"block", reason:$r}'
fi
exit 0
