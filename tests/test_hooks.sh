#!/bin/sh
# sliceworks 0.2.0. Hook behaviour tests: inert without configuration; each guard denies its failure and allows the rest.
# Usage: sh tests/test_hooks.sh   (exit 1 on the first mismatch)
set -u
H="$(cd "$(dirname "$0")/.." && pwd)/hooks"
P="$(mktemp -d)"; trap 'rm -rf "$P"' EXIT
cd "$P" && git init -q . && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
export CLAUDE_PROJECT_DIR="$P"
fail=0; n=0; failures=0
expect() { # expect <label> <deny|allow> <hook> <json>
  n=$((n+1)); out="$(printf '%s' "$4" | sh "$H/$3.sh" 2>/dev/null)"; rc=$?
  dec="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // (if .decision == "block" then "deny" else empty end)' 2>/dev/null)"
  got=allow; [ "$dec" = "deny" ] && got=deny; [ "$rc" = 2 ] && got=deny
  if [ "$got" = "$2" ]; then printf 'ok   %s\n' "$1"; else printf 'FAIL %s: expected %s, got %s (%s)\n' "$1" "$2" "$got" "$(printf '%s' "$out" | head -c 120)"; fail=1; failures=$((failures+1)); fi
}
IMPL='"agent_type":"sliceworks:slice-implementer"'
# 1. no configuration: everything allowed
for h in kill-switch budget-guard role-guard money-guard implementer-stop coordinator-stop session-context; do
  expect "no config: $h inert" allow "$h" "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push\",\"subagent_type\":\"general-purpose\"},$IMPL,\"cwd\":\"$P\"}"
done
# 2. configuration present
mkdir -p .sliceworks docs/process/metrics docs/process/rounds/1-market docs/process/rounds/0-old
printf 'SW_STATE_DIR=docs/process\nSW_PAID_CMDS="evals/run.sh|--paid"\nSW_CONTRACT_SURFACES="api/openapi.yaml specs/"\n' > .sliceworks/config.env
touch docs/process/rounds/0-old/.closed
expect "kill switch absent" allow kill-switch '{"tool_name":"Edit","tool_input":{"file_path":"x"}}'
touch docs/process/STOP
expect "kill switch present" deny kill-switch '{"tool_name":"Edit","tool_input":{"file_path":"x"}}'
rm docs/process/STOP
expect "budget: no reading" deny budget-guard '{"tool_name":"Agent","tool_input":{"subagent_type":"general-purpose"}}'
expect "budget: explorer exempt" allow budget-guard '{"tool_name":"Agent","tool_input":{"subagent_type":"Explore"}}'
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '{"at":"%s","event":"manual","runtime":"codex","weekly_pct":82,"weekly_reset":%s,"five_hour_pct":5}\n' "$now" "$(( $(date -u +%s) + 86400 ))" > docs/process/metrics/usage.jsonl
expect "budget: 82%% with epoch reset holds" deny budget-guard '{"tool_name":"Agent","tool_input":{"subagent_type":"general-purpose"}}'
printf '{"at":"%s","event":"manual","runtime":"claude","weekly_pct":40,"weekly_reset":"2027-01-01T00:00:00Z","five_hour_pct":5}\n' "$now" > docs/process/metrics/usage.jsonl
expect "budget: 40%% allows" allow budget-guard '{"tool_name":"Agent","tool_input":{"subagent_type":"general-purpose"}}'
expect "budget: message at 40%% allows" allow budget-guard '{"tool_name":"SendMessage","tool_input":{"to":"worker","message":"go"}}'
printf '{"at":"%s","event":"manual","runtime":"claude","weekly_pct":82,"weekly_reset":"2027-01-01T00:00:00Z","five_hour_pct":5}\n' "$now" > docs/process/metrics/usage.jsonl
expect "budget: message to a chat at 82%% is a dispatch" deny budget-guard '{"tool_name":"SendMessage","tool_input":{"to":"worker","message":"status?"}}'
expect "budget: cross-thread message at 82%% is a dispatch" deny budget-guard '{"tool_name":"mcp__codex__send_message_to_thread","tool_input":{"threadId":"x","prompt":"status?"}}'
expect "budget: unrelated tool at 82%% allowed" allow budget-guard '{"tool_name":"Read","tool_input":{"file_path":"x"}}'
printf '{"at":"%s","event":"manual","runtime":"claude","weekly_pct":40,"weekly_reset":"2027-01-01T00:00:00Z","five_hour_pct":5}\n' "$now" > docs/process/metrics/usage.jsonl
expect "role: main session unguarded" allow role-guard '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}'
expect "role: implementer git push" deny role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push origin main\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer git merge-base allowed" allow role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git merge-base HEAD main\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer kubectl" deny role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"kubectl get pods\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer edits STATE.md" deny role-guard "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$P/docs/process/STATE.md\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer edits product file" allow role-guard "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$P/src/a.go\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer redirect into main protected" deny role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"echo x >> $P/docs/process/FEATURES.json\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: implementer secrets" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/infra/prod.tfvars\"},$IMPL,\"cwd\":\"$P\"}"
expect "role: efficiency reviewer outside retros" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/src/a.go\"},\"agent_type\":\"sliceworks:efficiency-reviewer\"}"
expect "role: efficiency reviewer in retros" allow role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/docs/process/retros/x.md\"},\"agent_type\":\"sliceworks:efficiency-reviewer\"}"
expect "role: contract author on surface" allow role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/api/openapi.yaml\"},\"agent_type\":\"sliceworks:contract-author\"}"
expect "role: contract author off surface" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/internal/a.go\"},\"agent_type\":\"sliceworks:contract-author\"}"
expect "role: researcher in open round" allow role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/docs/process/rounds/1-market/register.md\"},\"agent_type\":\"sliceworks:researcher\"}"
expect "role: researcher in closed round" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/docs/process/rounds/0-old/register.md\"},\"agent_type\":\"sliceworks:researcher\"}"
expect "role: researcher outside rounds" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/docs/process/ARCHITECTURE.md\"},\"agent_type\":\"sliceworks:researcher\"}"
expect "role: researcher bash write" deny role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"echo x > a\"},\"agent_type\":\"sliceworks:researcher\"}"
expect "role: architect on design surface" allow role-guard "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$P/docs/process/ARCHITECTURE.md\"},\"agent_type\":\"sliceworks:architect\"}"
expect "role: architect on specs" allow role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/specs/events-1.md\"},\"agent_type\":\"sliceworks:architect\"}"
expect "role: architect on product code" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/src/a.go\"},\"agent_type\":\"sliceworks:architect\"}"
expect "role: business analyst write" deny role-guard "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$P/docs/process/intake/x.md\"},\"agent_type\":\"sliceworks:business-analyst\"}"
expect "role: system analyst bash write" deny role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git commit -am x\"},\"agent_type\":\"sliceworks:system-analyst\"}"
expect "role: system analyst bash read" allow role-guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git log --oneline -5\"},\"agent_type\":\"sliceworks:system-analyst\"}"
expect "role: code reviewer write" deny role-guard "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$P/src/a.go\"},\"agent_type\":\"sliceworks:code-reviewer\"}"
expect "money: unpaid command allowed" allow money-guard '{"tool_name":"Bash","tool_input":{"command":"go test ./..."}}'
expect "money: paid command, no cap" deny money-guard '{"tool_name":"Bash","tool_input":{"command":"evals/run.sh suite-a"}}'
printf 'SW_MONEY_CAP=10\n' >> .sliceworks/config.env
expect "money: paid command under cap" allow money-guard '{"tool_name":"Bash","tool_input":{"command":"evals/run.sh suite-a"}}'
printf '{"at":"%s","event":"eval","amount":6,"currency":"USD","authorization":"D-3"}\n{"at":"%s","event":"eval","amount":4.5,"currency":"USD","authorization":"D-3"}\n' "$now" "$now" > docs/process/metrics/money.jsonl
expect "money: cap reached" deny money-guard '{"tool_name":"Bash","tool_input":{"command":"evals/run.sh suite-a"}}'
printf '{"at":"%s","event":"eval","amount":50,"currency":"EUR","authorization":"D-4"}\n' "$now" > docs/process/metrics/money.jsonl
expect "money: other currency not counted" allow money-guard '{"tool_name":"Bash","tool_input":{"command":"evals/run.sh --paid"}}'
expect "implementer-stop: no verify script configured" allow implementer-stop "{$IMPL,\"cwd\":\"$P\"}"
# 3. Codex-shaped input: native tool names, no agent_type on PreToolUse; the role comes from the launcher
PATCH2='*** Begin Patch\n*** Update File: src/a.go\n@@\n-x\n+y\n*** Update File: docs/process/STATE.md\n@@\n-x\n+y\n*** End Patch'
expect "codex: main session push unguarded" allow role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":[\"bash\",\"-lc\",\"git push origin main\"]},\"cwd\":\"$P\"}"
export SW_ROLE=slice-implementer
expect "codex: SW_ROLE implementer push (argv command)" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":[\"bash\",\"-lc\",\"git push origin main\"]},\"cwd\":\"$P\"}"
expect "codex: SW_ROLE implementer exec_command cmd" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"exec_command\",\"tool_input\":{\"cmd\":\"git merge main\"},\"cwd\":\"$P\"}"
expect "codex: patch on a product file" allow role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"apply_patch\",\"tool_input\":{\"command\":\"*** Begin Patch\\n*** Add File: src/b.go\\n+x\\n*** End Patch\"},\"cwd\":\"$P\"}"
expect "codex: patch whose second file is protected" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"apply_patch\",\"tool_input\":{\"command\":\"$PATCH2\"},\"cwd\":\"$P\"}"
expect "codex: patch as input field" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"apply_patch\",\"tool_input\":{\"input\":\"$PATCH2\"},\"cwd\":\"$P\"}"
mkdir -p scripts/dev && printf '#!/bin/sh\necho RESULT=fail\necho LOG=/tmp/t0.log\nexit 1\n' > scripts/dev/verify-slice.sh && chmod +x scripts/dev/verify-slice.sh
expect "codex: Stop of a red implementer worker blocks" deny implementer-stop "{\"turn_id\":\"t1\",\"hook_event_name\":\"Stop\",\"stop_hook_active\":false,\"cwd\":\"$P\"}"
expect "codex: Stop already blocked once passes" allow implementer-stop "{\"turn_id\":\"t1\",\"hook_event_name\":\"Stop\",\"stop_hook_active\":true,\"cwd\":\"$P\"}"
unset SW_ROLE
expect "codex: Stop of the main session passes" allow implementer-stop "{\"turn_id\":\"t1\",\"hook_event_name\":\"Stop\",\"stop_hook_active\":false,\"cwd\":\"$P\"}"
rm -rf scripts
git worktree add -q -b slice/wt "$P/.claude/worktrees/wt" 2>/dev/null
printf 'slice-implementer\n' > "$(git -C "$P/.claude/worktrees/wt" rev-parse --absolute-git-dir)/sliceworks-role"
expect "codex: role marker of the worktree guards push" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push\"},\"cwd\":\"$P/.claude/worktrees/wt\"}"
expect "codex: role marker cannot be removed" deny role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"rm .git/worktrees/wt/sliceworks-role\"},\"cwd\":\"$P/.claude/worktrees/wt\"}"
expect "codex: a role-less native child of a worker keeps the worker's guard" deny role-guard "{\"turn_id\":\"t1\",\"agent_type\":\"default\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push\"},\"cwd\":\"$P/.claude/worktrees/wt\"}"
expect "codex: a role-less native child of the coordinator is the coordinator's" allow role-guard "{\"turn_id\":\"t1\",\"agent_type\":\"default\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push\"},\"cwd\":\"$P\"}"
out="$(printf '{"source":"startup"}' | SW_ROLE=slice-implementer SW_ALLOCATION=alloc-1 sh "$H/session-context.sh")"; n=$((n+1))
case "$out" in *"worker session"*"alloc-1"*) echo "ok   session context: a worker is told it is a worker";; *) echo "FAIL session context for a worker: $out"; fail=1; failures=$((failures+1));; esac
expect "codex: main checkout has no marker" allow role-guard "{\"turn_id\":\"t1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push\"},\"cwd\":\"$P\"}"
printf '{"at":"%s","event":"manual","runtime":"codex","weekly_pct":82,"weekly_reset":"2027-01-01T00:00:00Z","five_hour_pct":5}\n' "$now" > docs/process/metrics/usage.jsonl
expect "codex: spawn_agent at 82%% is a dispatch" deny budget-guard '{"turn_id":"t1","tool_name":"spawn_agent","tool_input":{"agent_type":"slice-implementer","message":"x"}}'
expect "codex: spawn_agent of an explorer is exempt" allow budget-guard '{"turn_id":"t1","tool_name":"spawn_agent","tool_input":{"agent_type":"code-explorer","message":"x"}}'
printf '{"at":"%s","event":"manual","runtime":"codex","weekly_pct":40,"weekly_reset":"2027-01-01T00:00:00Z","five_hour_pct":5}\n' "$now" > docs/process/metrics/usage.jsonl
# 4. the Codex coordinator's continue loop over worker processes
STOPIN='{"turn_id":"t9","hook_event_name":"Stop","stop_hook_active":false}'
mkdir -p .run/codex outputs/slices/slice-07/codex
expect "codex stop: no workers, the turn ends" allow coordinator-stop "$STOPIN"
printf 'CANDIDATE outputs/x.log\n' > outputs/slices/slice-07/codex/slice-implementer-1.last; echo "0 now" > outputs/slices/slice-07/codex/slice-implementer-1.done
expect "codex stop: a finished worker continues the turn" deny coordinator-stop "$STOPIN"
expect "codex stop: once read, the turn ends" allow coordinator-stop "$STOPIN"
sleep 30 & spid=$!; echo "$spid" > .run/codex/alloc-slice-08-r1.pid
SW_CODEX_WAIT=0; export SW_CODEX_WAIT
expect "codex stop: a running worker continues the turn" deny coordinator-stop "$STOPIN"
expect "claude stop: a running codex worker does not hold a Claude Code turn" allow coordinator-stop '{"hook_event_name":"Stop","stop_hook_active":false}'
printf 'SW_CODEX_CONTINUE=0\n' >> .sliceworks/config.env
expect "codex stop: SW_CODEX_CONTINUE=0 ends the turn" allow coordinator-stop "$STOPIN"
{ kill "$spid" && wait "$spid"; } 2>/dev/null; unset SW_CODEX_WAIT
out="$(printf '{"source":"startup"}' | sh "$H/session-context.sh")"; n=$((n+1))
case "$out" in *"runs under sliceworks"*) echo "ok   session context printed";; *) echo "FAIL session context"; fail=1; failures=$((failures+1));; esac
echo "tests: $n, failures: $failures"
exit $fail
