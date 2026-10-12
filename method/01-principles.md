# 1. Purpose and principles

The method exists to deliver an accepted scope with a small number of AI sessions, within the owner's usage window, with independent review where risk is material, and without a human in the loop except for the acts only a human can perform.

Design rule: every component of the harness encodes an assumption about what the model cannot do alone. Each rule names the failure it prevents ([components](11-components.md)). A rule whose failure stops occurring for a whole increment is removed at the retrospective.

Eight principles:

1. **One writer per slice.** Parallelism runs across independent vertical slices with a frozen contract between them, never across the layers of one feature. A writer cap bounds concurrency.
2. **Reads fan out, writes do not.** Exploration, review, contract drafting and verification run in clean-context subagents and return summaries. Only a slice implementer writes product code.
3. **Executable truth before model judgment.** A deterministic check decides whether a candidate is reviewable. A reviewer sees the diff, the brief and the check log. Pull requests exist for the owner's asynchronous reading; they do not block.
4. **State lives in files the host enforces.** A feature ledger with pass flags, a state file, a progress file, briefs, hooks. No receipts, proofs, grants, leases or acknowledgements.
5. **Steer by connected outcomes.** Progress is the count of acceptance scenarios passing end to end on the integration branch. Task identifiers are traceability.
6. **Context is the budget.** The always-on instruction file stays short, no polling by a model (scripts may poll freely), subagents for anything verbose, one worker per unit of work.
7. **Measure, then change, then measure.** Three outcome numbers and four tax numbers, a bounded efficiency review per increment, at most three process changes per retrospective, each with a success metric and a sunset.
8. **Autonomous by default, human by exception.** Every decision has a recorded default and an owner who may veto it asynchronously. Only the human-only acts wait for a person, and the run never idles on them: other work proceeds.

Agile, as applied: Kanban for flow, XP for engineering, Lean for waste, and from Scrum a product owner, a Definition of Ready and Done, a demonstrable increment, a review and a retrospective. No sprints, standups, story points or velocity charts.
