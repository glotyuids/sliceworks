# Rules for every agent in this project

<!-- sliceworks 0.6.0. Written to .claude/rules/sliceworks.md by the adopt skill. The method is the sliceworks package; the values are in .sliceworks/config.env. -->

- One writer per worktree. Implementers never push, merge, switch branches, rewrite history, manage worktrees, run the full suite, or contact cloud, cluster or provider infrastructure. Only the coordinator edits the state files and merges. Hooks enforce this.
- Tests are never removed, skipped or weakened to pass; a changed oracle needs a positive control. Numbered artifacts come from the ledger; an executed one is never edited or renumbered.
- Secrets: never read or print a secret, a credential file or a connection string with a real password. Local values are synthetic.
- Kill switch: the STOP file in the state directory halts dispatch and edits mechanically.
- Messages between coordinator and implementer: BRIEF, CANDIDATE, BLOCKED, FINDINGS, CONTRACT, HOLD only; at most eight per slice. No progress reports or acknowledgements.
- Context is the budget: subagents for anything verbose, one explorer question at a time, no polling by a model. Use absolute paths; the working directory does not persist between tool calls.
- Decisions: class C (layout, fixtures, naming) are the implementer's; contracts and technical defaults are the coordinator's class B; product defaults are class A2 with a 48-hour owner veto; credentials, money, legal, real data and irreversible outside actions are human-only (NEEDS-HUMAN.md). Every decision is a D entry in DECISIONS.md; a change to ARCHITECTURE.md cites one.
- Rounds are frozen on close; frozen specs have no TODO; nothing is deployed beyond the isolated environment by an agent; no paid run without an authorization decision and a cap.
- A pivot is a D entry with the pivot marker (refocus, method chapter 14): the product is audited against it, the documents it retires are moved to archive/ and never edited or referenced by a brief, and every surface it amends cites it.
