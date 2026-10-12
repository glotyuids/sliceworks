# 16. Operate and Learn

## Operate

- **Probes** (`kind: probe`): health, error rate, latency, cost per day, each a command that runs against a named environment on a schedule and exits 0 or not. A red probe opens an incident. Prevents: learning about an outage from a user.
- **Incidents**: `INCIDENTS.md` with id, opened, severity, environment, what, status, the fix slice, the postmortem. Severity one pages the owner (the fifth notification, `incident`); everything else the coordinator handles. An incident opens a `fix` slice on the expedited path and, when it is closed, a postmortem in the project's format whose actions become retro items or rows. Prevents: fixes without a record; records without a fix.
- **The hotfix lane**: a `fix` slice runs T0 and T1, gets one expedited review, merges, runs T2, and ships through a release slice reduced to the steps the change touches. Nothing skips the tiers; the ceremony shrinks, the checks do not.
- **Production review digests**: a script gathers the period's traces into a bundle with personal data removed; a bounded reviewer writes one digest (verdicts per case against the product's own quality bar, incidents, user reactions, fleet health); candidates go to the feedback register. Access to real data is a human-only approval recorded once per environment as a decision. Prevents: a live product nobody reads.
- The coordinator is on call. The owner is paged only for human-only acts and severity one.

## Learn

- **Evaluation suites**: `evals/<suite>/` with a pinned corpus, graders, a threshold, and a budget in tokens and money; every run writes a verdict file; an `eval` row's check is that the latest verdict exists, is within budget and at or above the threshold. Prevents: quality claims without a corpus; paid runs without a cap.
- **The money ledger**: `metrics/money.jsonl`, one entry per paid run (`at, event, amount, currency, authorization, run, note`), against an authorization recorded as a D entry. The money guard refuses a command the configuration marks as paid when the ledger's sum for the authorization has reached the cap. Prevents: an autonomous run spending money it was not given.
- **Metrics review** against the milestone's success metrics, once per increment or per release: by script where the metric is a number, by a bounded reviewer where it is a judgment. The result is recorded in `MILESTONES.md`; the milestone closes when its metrics are measured, whatever they say.
- **The feedback register**: `FEEDBACK.md`, candidates with evidence (a digest, a metric, an incident, an owner note), not yet features. A debt candidate carries a priority, (impact + risk) × (6 − effort) with each term scored 1 to 5, so the retrospective can thin by number rather than by mood. The next milestone's Discover reads it first. Prevents: feedback that becomes a feature with no evidence, or evaporates.

## Learning about the process

Chapter 9 remains the process's own loop: friction notes, the efficiency review, the retrospective. The two loops meet at the retrospective, which reads both the process telemetry and the product's incidents and evaluations.
