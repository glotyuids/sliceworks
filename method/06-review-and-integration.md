# 6. Review, integration, acceptance

## Review

Inputs: base SHA, head SHA, the brief, the T1 log. The reviewer works from the diff in a fresh context and reads surrounding code only to verify a finding.

Output, one message:

```text
REVIEW <slice> <head sha> VERDICT: pass | changes_required
[H1] <file>:<line> <requirement or invariant>; <evidence>; <impact>
[M1] ...
Scope: reviewed <n> files; reused T1 evidence for <units>; not reviewed: <explicit list>
```

Severity by product impact: High blocks the merge; Medium blocks unless the implementer states why it is out of scope; Low is advisory. Style, naming and abstraction preferences are not findings. The implementer decides which findings are in scope and says so in the next `CANDIDATE`.

Rounds: the same reviewer is resumed for the delta. A failing round names the concrete obstruction, preserves the failed result and issues one bounded correction to the same implementer (chapter 19). After two substantive rounds in one issue family, the coordinator diagnoses the requirement or the oracle before any further repair. A review pass approves source; it is not a prepared checkpoint and not runtime proof.

Named-risk review: triggered by the brief's material-boundary flag. One named question, separate verdict, the strongest model. Both verdicts must pass.

Budget: 30 minutes per round, two rounds.

## Integration

A candidate merges as soon as T1 is green and the review passes. One merge at a time, `git merge --no-ff <slice-sha>` onto the integration branch, T2 starts immediately in the background. No seals, no eligible sets, no whole-tree pre-checks, no cap on waiting candidates, no hash re-verification at intake (merge by SHA is byte identity). Budget from review pass to merged-and-green: 20 minutes.

A T2 failure reverts the merge commit and returns the slice to `repair` with the log. Behavior-changing merge resolutions get a delta review. Before merging, check every pinned submodule or gitlink in the candidate against the integration head; never re-pin the T2 worktree while a T2 runs; dispatch isolated agents from the repository root.

## Acceptance

At `green`, the coordinator flips the slice's ledger rows to `passes: true` with the test name and log path, records the merge SHA and timestamps in `STATE.md`, and re-dispatches the implementer.

Numbered artifacts (migrations, schema versions) come from a ledger the coordinator keeps; an executed one is never edited or renumbered. The integration branch is pushed to the project's remote once per milestone as a backup, through the one script that refuses anything but that branch and never forces.
