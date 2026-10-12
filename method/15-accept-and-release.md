# 15. Accept and Release

## Accept

A milestone is **engineering-complete** when every row of the milestone passes or is `blocked_on_human` (chapter 3). It is **accepted** when the owner has read the acceptance packet and closed the gate rows that are theirs.

- **Gate rows** (`kind: gate`), one per item of each gate family in `MILESTONES.md`, with `human_act` set. Check: the inbox row has a done date, or a decision waived it. Prevents: a milestone declared done with gates nobody listed.
- **The acceptance packet**, `accept/<milestone>.md`, written by the coordinator and read once by the owner: what to read (the demo artifact, scenario coverage, the open findings, the success metrics measured so far), what to decide (the gate rows, each with the exact ask), what is parked. Prevents: acceptance by scrolling a dashboard.
- **Two verdicts, kept apart**: *mechanism verified* (tests, demo, probes) and *quality accepted* (an owner's or an evaluator's judgment on outcomes). A green suite is never recorded as acceptance. Prevents: green tests read as a product working.
- Acceptance is one of the owner notifications. On acceptance the milestone moves to `releasing` (or to `closed` for an internal milestone with no release).

## Release

A release is a deployment event to a named **environment**. Environments are declared in the configuration with who may deploy where: agents deploy only to the `isolated` environment the owner provisioned; every other deployment is a human act with the exact command prepared and the verification named. Prevents: an agent one command away from production.

The **release slice** carries the checklist, each item a `kind: release` row:

| Step | Check |
|---|---|
| version and changelog | the tag exists; the changelog names every merged slice since the last release |
| migrations and rollback | the migration plan lists every numbered artifact since the last release; the rollback was rehearsed in the isolated environment |
| feature flags and configuration | every flag has a default and an owner |
| runbook | the runbook covers the new surfaces; the incident path is named |
| **T5 rehearsal** | deploy to the isolated environment, run the smoke and the milestone's scenario subset there, record the log |
| security review | the threat models of touched surfaces are current; the named-risk findings are closed |
| approvals | each approval is a D entry (money, legal, data) |
| notice | on-call, or the owner in the lite profile, knows the window and the rollback trigger before the deploy |
| the push | through the one script that refuses anything but the integration branch and never forces |
| deploy | human act per environment, prepared command, verification by name; canary first where the environment offers one |
| post-release verification | the probes are green for the agreed window; the release is recorded in `MILESTONES.md` |
| announcement | human act |

The method does not say how to build a pipeline, write a chart or rotate a secret; the project's engineering skills do. The release slice is the order of the steps and the record that each ran.
