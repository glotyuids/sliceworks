# 11. Components and the failures they prevent

Each component names the failure it prevents; the retrospective removes components whose failure stopped occurring, security invariants excepted.

| Component | Prevents |
|---|---|
| `FEATURES.json` with pass flags, evidence and `human_act` | premature completion; counting components as outcomes; idling on a human |
| `STATE.md` under 50 KB | registry bloat; stale pointers |
| `PROGRESS.md` | lost run memory |
| `OWNER-DECISIONS.md` with veto windows | silent defaults; unanswered rows blocking work |
| `NEEDS-HUMAN.md` | human asks scattered across chats; waiting on a human for anything but the act itself |
| `.run/coordinator-session.md` | running slices that cannot be resumed after a compaction |
| briefs capped at 150 lines | vague delegation; invented interfaces; oversize slices |
| the init command | each run rediscovering how to run the project |
| the tier runner and the T0 Stop hook | model output as a gate; red discovered hours later |
| the must-run check | renamed or unwritten tests counted as passing |
| affected-set computation | running unaffected tests; incomplete manifests |
| continuous merge with T2 | batching; lane waits |
| six message shapes | status traffic; full-context turns |
| decision classes A1, A2, B, C | technical questions waiting for a human; human acts hidden in agent defaults |
| the demo runner and the demo artifact | increments closing on green tests that no user path exercised |
| stall rule, turn limit, stall and stale detectors | runaway or hung implementers |
| ready detector with dependency columns | idle writer slots while slices could start |
| `STOP` file and veto windows | an unattended run the owner cannot stop or correct |
| protected files enforced at the diff | an implementer rewriting the coordinator's state |
| efficiency review bounded to one run and three logged proposals | a process-management role consuming a sizeable share of budget; proposals lost or repeated |
| named-risk reviewer at material boundaries | silent security failures that pass tests (never removed) |
| plan review for material-boundary slices | defect classes found in code review that a plan review finds cheaper |
| runtime parity check | two hosts drifting apart |
| harness self-check in the wake timer | a broken hook or settings file silently disabling the rails |
| `SPARK.md` and riskiest assumptions | a backlog built on an unstated premise |
| rounds with a claim register and verdicts | analyses nobody can audit; a design resting on an unverified claim |
| one decisions ledger with classes, defaults and due dates | silent defaults; questions waiting in chat; a ready slice blocked on an unowned question |
| `SCENARIOS.json` above the rows | increments closing on rows no user journey needs |
| `MILESTONES.md` with gate families | "MVP" meaning different things to the owner and the coordinator; gates discovered at release |
| `ARCHITECTURE.md` citing decisions; `INDEX.md` with review dates | design drift nobody can trace; a frozen note treated as current |
| threat models per material surface | named-risk reviews that reconstruct the threat model each time |
| increment planning (surface map, reuse audit, decoupling) | slices rebuilt from scratch; writers colliding on one file |
| `refocus` with a recorded pivot | a pivot made in chat that leaves the ledger describing the old product |
| gate rows and the acceptance packet | acceptance by scrolling a dashboard; green tests read as acceptance |
| the release checklist and named environments | an agent one command away from production; a release with no rollback |
| probes and `INCIDENTS.md` | learning about an outage from a user; fixes without a record |
| evaluation suites with verdicts; the money ledger and guard | quality claims without a corpus; money spent without authorization |
| `FEEDBACK.md` | feedback that becomes a feature without evidence, or evaporates |
| `survey.py` and `SURVEY.md` | adopting blind; asking the owner what the repository already says |
| importers (`prepare`) | re-authoring specifications, decisions and scenarios the project already has in another format |
| the `start` dispatcher | starting the wrong phase; an owner who must know the method to begin |
| the intake pipeline and `intake/<id>.md` | features entering by chat without analysis; analysis without a record |
