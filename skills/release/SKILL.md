---
name: release
description: Ship a sliceworks milestone or hotfix through the release checklist - open a release slice, drive the steps (version and changelog, migrations and rollback, flags, runbook, the isolated-environment T5 rehearsal, security review, approvals as decisions, the one push), prepare every human deploy act with its exact command and verification, record post-release probes and the release in MILESTONES.md. Use when the user says "release", "ship it", "deploy", "cut a release", "hotfix to production", or after a milestone is accepted.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Release

Method: `method/15-accept-and-release.md`. Template: `release.md`. Environments: `SW_ENVIRONMENTS`; agents deploy only to the first.

1. **Open** a `release` slice with the checklist; one `release` row per step.
2. **Script steps.** Tag and changelog (every merged slice since the last release), migration plan and rollback rehearsal, flags with owners, runbook, **T5**: deploy to the isolated environment, run the smoke and the milestone's scenario subset there, record the log.
3. **Reviews and approvals.** Security review of the touched threat models; approvals as `D` entries (money, legal, data).
4. **Push** through the one push script.
5. **Human acts.** For each environment beyond isolated: the exact command, the expected verification by name, the rollback command; as `NEEDS-HUMAN.md` rows. Never run them.
6. **Verify.** Probes green for the agreed window; record the release in `MILESTONES.md`; the announcement is a human act.
7. **Library skills.** The pipeline steps follow the library's `cicd-build-deploy`, secrets follow `secrets-management`, the runbook follows the `documentation-standards` runbook template, all where installed (method chapter 18). A step no installed skill covers is a `TODO` row the owner performs with the prepared command.
8. **Hotfix path.** A `fix` slice reduces the checklist to the steps the change touches; nothing skips the tiers.
