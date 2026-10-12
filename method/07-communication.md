# 7. Communication

State lives in files both sides read. A message is sent only when the receiver must act now. Six shapes:

| Direction | Message | Content |
|---|---|---|
| coordinator → implementer | `BRIEF <slice>` | path to the brief; the goal condition |
| implementer → coordinator | `CANDIDATE <slice> <sha> <t1 log path> [in-scope findings decided: ...]` | |
| implementer → coordinator | `BLOCKED <slice>: <question> / default I would apply: <default> / can continue with: <what>` | |
| coordinator → implementer | `FINDINGS <slice> <sha>` followed by the review output | one per review round, as the resume prompt |
| coordinator → implementer | `CONTRACT <file> <new sha>: <one-line reason>` | on an amended contract the slice pins |
| either | `HOLD <reason> / resume when <condition>` | budget hold, kill switch |

Never sent: progress, acknowledgements, receipts, "no action required", status requests. The coordinator receives implementer completions as notifications and reads the worktree's log and `PROGRESS.md` when it needs more. Reviewers and explorers never communicate across a session boundary.

Budget: eight messages per slice. A slice needing more was under-prepared; fix the contract or the decision, not the messaging.

Owner channel, all asynchronous: `NEEDS-HUMAN.md` for human-only acts; `OWNER-DECISIONS.md` for defaults and veto windows; `STATUS.md` hourly and the dashboard continuously, both written by scripts without a model turn; the demo artifact and the retrospective at each increment end; the milestone pull request. A notification accompanies exactly five events: a new inbox item (including an acceptance packet), an increment or milestone close, a kill-switch stop, a budget hold, and a severity-one incident. Nothing else reaches the owner.
