# Changelog

## 0.4.1

- Design reasoning (review of 2026-10-13, `docs/design/2026-10-13-anthropic-engineering-plugins-review.md`): the architect profile gains a six-step procedure before the artifacts (requirements, map, options with a dimension table, deep dive, scale and reliability, trade-offs); class A2 and B decisions carry an Options considered table; the release checklist gains the notice and canary rows; briefs name the test type per component; debt candidates in the feedback register carry a priority; chapter 18 lists two optional bindings to official-catalog plugins (`feature-dev:code-architect`, `system-design-skills`).

## 0.4.0

- Binding with the `engineering-skills` library (method chapter 18): `sliceworks` is listed in the library's marketplace and installed from this repository; the survey detects the library skills a project has installed, by pack and version, recommends packs for the stack and phases, and reports per phase which library skills the phase skills will call; `adopt` offers the recommended packs through the library's own install procedure; `design`, `release`, `operate` and `learn` name the library skills they rely on and their fallbacks.
- The architect profile runs on `fable` at the highest effort.

## 0.3.0

- Entry and intake (method chapter 17): the entry sequence adopt → survey → prepare → start; `scripts/survey.py`, a deterministic inventory of a project (stack and commands, Spec Kit, OpenSpec, decision records, plans, architecture documents, boards, agent configuration, project memory, phase coverage) with `--next`, the dispatcher that names the next skill from the ledgers; importers in the `prepare` skill for Spec Kit, OpenSpec, decision records, plans, architecture documents, tests and boards; the `intake` pipeline for requests typed in chat (capture, business analysis, system analysis, scenario adaptation, decisions, placement) with `intake/<id>.md`.
- Skills: `start`, `survey`, `prepare`, `intake`; `adopt` runs the survey first and ends by running `start`.
- Agents: `business-analyst` and `system-analyst`, read-only; the role guard now enforces read-only for both analysts, both reviewers and the explorer.
- Tests: `tests/test_survey.py` (7 cases) and four more hook cases.
- The architect profile runs on the smartest available model (`fable`) at the highest effort; the routing table in method chapter 8 says why.

## 0.2.0 (unreleased)

- Lifecycle breadth (design note `docs/design/2026-10-12-lifecycle-coverage.md`): a product moves through named milestones with ten phases (spark, discover, decide, design, plan, build, accept, release, operate, learn); MVP is a milestone name. Method chapter 0 and chapters 13 to 16.
- Ledger: `kind` and `milestone` on every row (scenario, criterion, claim, experiment, decision, spec, gate, release, probe, eval), each kind with its own check. Schemas for user scenarios and money-ledger entries.
- Ledgers and templates: `SPARK.md`, research rounds, one `DECISIONS.md` (D and Q entries with classes, defaults and due dates; `OWNER-DECISIONS.md` becomes a rendered view), `ARCHITECTURE.md`, specs, `SCENARIOS.json`, `MILESTONES.md` with gate families, threat models, the acceptance packet, the release checklist, `INCIDENTS.md`, `FEEDBACK.md`, evaluation suites, `INDEX.md`.
- Skills: `discover`, `decide`, `design`, `plan-increment`, `refocus`, `accept`, `release`, `operate`, `learn`; `kickoff` composes the first four; `adopt` writes the new files.
- Agents: `researcher` (read-only, one question, writes only inside an open round) and `architect` (writes only the design surfaces); role guard extended.
- Hooks: the money guard refuses paid commands without an authorization cap or past it. A fifth notification, `incident`.
- Scripts: `check-design-docs.py` (architecture changes cite a decision; INDEX.md review limit; frozen specs without TODO) with tests. `tests/test_hooks.sh` covers every guard.

## 0.1.0

- Phase 0: repository skeleton, plugin manifest, method book, rationale, six agent profiles,
  plugin-level hooks keyed on agent type, six skills, templates and schemas.
