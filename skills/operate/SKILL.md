---
name: operate
description: Run a sliceworks product in production - install probe rows and their schedule, open incidents from red probes or reports, drive fix slices through the hotfix lane, run the production review digest over anonymized traces, keep INCIDENTS.md and the postmortems, and page the owner only for severity one or human-only acts. Use when the user says "operate", "on call", "incident", "production review", "daily digest", "what happened in prod", or after a release is verified.
license: Apache-2.0
metadata:
  source: sudo-sane/sliceworks
  version: 0.5.0
---

# Operate

Method: `method/16-operate-and-learn.md`. Templates: `INCIDENTS.md`, the skills library's postmortem template.

1. **Probes.** One `probe` row per health, error-rate, latency and cost signal, each a command against a named environment; install the schedule with the package's schedule script.
2. **Incidents.** A red probe or a report opens an `INCIDENTS.md` row with severity; severity one is the `incident` notification to the owner. Open a `fix` slice (brief under 50 lines, expedited review); ship through the hotfix path of `release`.
3. **Postmortem.** On close, write the postmortem with the library's `documentation-standards` template where installed, following its `incident-response` procedure during the incident; its actions become retro items or rows.
4. **Digest.** On the configured cadence: the gathering script writes an anonymized bundle; a bounded reviewer writes one digest (verdicts per case against the product's quality bar, incidents, user reactions, fleet health); candidates go to `FEEDBACK.md`. Real-data access is a human-only approval recorded once per environment as a D entry.
5. **Record.** Probe results feed the dashboard; incidents feed the retrospective and `learn`.
