# 5. Verification

## Tiers

| Tier | Who, where | What | Budget | Gate for |
|---|---|---|---|---|
| T0 pre-commit | implementer, Stop hook | build, static checks, unit tests of changed units | under 2 min | ending a turn |
| T1 slice gate | implementer, its worktree and environment | integration tests for changed units and their direct dependents, plus the slice's end-to-end test and its ledger rows' checks | under 10 min | returning `CANDIDATE` |
| T2 merge gate | coordinator, integration branch, background | the transitive closure of affected units, direct consumers, named invariants, the other stacks' checks for changed areas | under 15 min | the merge staying in; a failure reverts it |
| T3 milestone | coordinator, clean worktree, background | the full suite with every tag and the race detector where the language has one | under 30 min | `MILESTONE_GREEN` |
| T4 nightly | scheduled job on the integration head | same as T3 | not blocking | escaped regressions become a fix slice |

The tier *structure* is the method's; the *commands* behind each tier are the project's, declared in its configuration. Affected units are computed, never classified by hand: a project supplies a "changed paths to test targets" function (reverse-dependency closure for T2 and T3, direct importers for T1).

## Rules

- A check must actually run. A renamed or unwritten test never counts; the must-run check fails unless the named test ran and passed.
- Tests are never removed or weakened to pass. A changed oracle needs a positive control and a demonstrated rejection of the intended broken behavior.
- A skipped check is `NOT_RUN`, never a pass. Source or compile evidence never certifies unexecuted behavior against a real dependency.
- Isolation and access-control tests are never relaxed.
- Review never runs before T1 is green.
- Every run writes one log under the outputs directory and one row to `metrics/tiers.jsonl`, and prints `RESULT=pass|fail` and `LOG=<path>` as its last lines.
- A candidate rebases onto the integration head before review when the head changed a file the slice also changed; a merge checks pinned submodules or gitlinks against the head.

## Environments per worktree

One shared service instance (database, broker) per machine where possible; every worktree gets its own namespaces, ports derived from the slice number, and per-test resources created with a random suffix, so writers collide on nothing. The project's init command brings a checkout or worktree to the baseline and proves it with a smoke check.

## Making T3 fit

In order of gain: template fixtures (set up once per run, clone per test), package parallelism after one check that the shared service tolerates it, the race detector on unit packages only, sharding the fixture-heavy packages. The first T3 after adoption records the baseline.
