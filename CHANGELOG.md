# Changelog

## Unreleased

- The GitHub account was renamed from `glotyuids` to `sudo-sane`. The plugin manifest (author, homepage, repository), the install commands and Codex marketplace source in the README, the schema `$id`s, the method links and every skill's `metadata.source` now name `sudo-sane`. Skill versions are unchanged except `update`. The frozen design notes in `docs/design/` keep the old name; GitHub redirects it.
- Former stamps stay recognised: `update` (0.5.0 → 0.5.1) treats `metadata.source: glotyuids/sliceworks` as the same source and a copy that differs only in that line as in sync, rewriting the stamp; the survey detects library skills stamped `glotyuids/engineering-skills` as well as `sudo-sane/engineering-skills`, with a test.

## 0.7.0

- Dashboard: the package now ships the generator (`dashboard/`, standard library only, collect → compute → render), ported from the first run's page with its tokens, CSS and components unchanged: progress, scenario, budget and money tiles, hold banners, one fold per increment with a segmented bar, a timeline and slice cards with a six-step stepper, the owner's inbox, veto clocks, open questions and milestones. Until now an adopting project had to write its own page, so every project looked different and a published copy was restyled. Everything project-specific moved into configuration (`SW_PROJECT_NAME`, `SW_DASHBOARD_OUT`, `SW_DASHBOARD_PUBLISH_CMD`, `SW_DASHBOARD_PUBLISH_EVERY`; `SW_TIMEZONE` now accepts offsets); the first run's legacy block, code-size baseline and budget-card variants were dropped.
- The slice-state vocabulary is defined once, in `dashboard/compute.py` (stage, colour and progress credit per state, including `paused`, `stopped`, `hold`, `waiting`, `green`, `cut`). A state outside it renders `UNKNOWN <state>` with a banner. Cut slices leave the progress total. Increments that `MILESTONES.md` lists as closed before adoption show as closed folds and a separate "before adoption" segment, and are not counted. Tables with empty cells (`| |`) parse, and slice ids may carry a name (`slice-01 land-inflight-set`).
- `scripts/dashboard-loop.sh` rebuilds the page every 30 seconds, stops on the kill switch and runs the project's publish command. `scripts/install.sh <project> --dashboard` copies both into `scripts/sliceworks/`. `adopt` installs and renders it and forbids project-written or restyled dashboards. `resume` and the START template name the loop command. Method chapter 9 describes the page and its rules, including that a shared copy is the generated file byte for byte.
- Thirty-two dashboard tests on two fixture projects (one mid-run, one freshly adopted with money and named slices) check the parsed page structure and the computed numbers.

## 0.6.1

- From the second Codex report (analysis of 2026-10-13): the allocation record distinguishes the responsible chat from the execution session, carries a queue marker, the base commit's gate health (`baseline` with known debt assigned), a `mode` (`full`, `prepare-only`, `review`) and `unblocks` for non-product work; the handoff classifies every failure as introduced, inherited, setup or unproven; the tier-run record gains the full commit, the base, the command, the exit code and the proof state.
- Collector: `QUEUED` from the queue marker; `DONE` only when the named log ends in `RESULT=pass` and the tiers row matches the handoff head, otherwise `CANDIDATE-UNVERIFIED`; `UNREGISTERED` lines for linked worktrees, live pid files and result-less logs no allocation owns; chat and session ids printed. Fourteen collector tests.
- Budget guard: every message that wakes a worker is a dispatch (`SendMessage`, cross-thread messaging tools, configurable through `SW_DISPATCH_TOOLS`); 47 hook cases.
- Method: chapter 19 (two actors, evidence-checked completion, failure classes, dependencies name what they block, `RUNTIME.md` for host restrictions), chapter 4 (the writer cap bounded by verification slots; prepare-only allocations), chapter 14 (`unblocks` on non-product slices), chapter 11 rows. Templates: `RUNTIME.md`, handoff failure table, brief `Unblocks` and `Baseline` lines. `adopt` registers a running project's live work; `collect` acts on the new states.

## 0.6.0

- Pivot and refocus (method chapter 14, with chapters 13 and 17): the **trigger** that separates a feature from a pivot (a change to the milestone promise, a riskiest assumption, an invariant, or a scenario of the current milestone), answered by the business analysis in one line (`Pivot: yes | no`) and branched on by intake; the **refocus audit**, in which the two read-only analysts walk every document, scenario, row, contract, spec and threat model against the pivot decision and the coordinator records keep, amend or archive per item in `refocus/<D-id>.md` (template `refocus.md`); **archiving** for living documents (`git mv` to `archive/<date>-<name>`, the `INDEX.md` row kept with status `archived (D-n)`, specs superseded in place, scenarios thinned, contracts retired); `refocus` re-runs `design` for every surface marked amend, citing the pivot D, before re-mapping and re-planning; the `pivot` marker on a D entry's metadata line.
- Lint: `check-design-docs.py` gains two checks: after the newest pivot decision every current `INDEX.md` row carries a review date at or after it (archived rows exempt), and no brief or contract references an archived document. Four tests.
- Agents: `business-analyst` and `system-analyst` gain an audit mode and the analyst answers whether a request is a pivot. Skills: `refocus` (eight steps), `intake`, `design`, `adopt` (`refocus/` and `archive/`). Templates: `refocus.md` new; `INDEX.md`, `DECISIONS.md`, `intake.md`, `specs-README.md`, `rules.md`. Components table: two rows. Glossary: pivot, refocus audit, archived.

## 0.5.1

- README: install, update and other-runtime sections under their own headers (Claude Code, Update, Codex, Other runtimes); the CLI form is documented because the desktop app's `/plugin` slash form opens the panel instead of running the subcommand.
- `scripts/release.sh`: one command bumps the manifest and README version, runs the hook and Python tests and the strict validator, commits, tags `v<version>` and pushes; `--marketplace <path>` also bumps the entry in the library's marketplace.

## 0.5.0

- Allocation and completion (method chapter 19, from the first run's Codex coordinator findings): actors with separate lifetimes (coordinator, worker as subagent, chat or CLI session, execution, verification run); the committed **allocation record** (worker, handles, worktree, branch, full base commit, allowed paths, completion condition, required artifacts) as the unit of dispatch and of recovery after a compaction; the **handoff** a worker commits on its branch as the record of completion, with CANDIDATE, BLOCKED and HOLD as pointers to it; the **collector** (`scripts/collect.py`) that reads completion from pids, logs, branch heads and handoffs; no acknowledgement or status request is ever a prerequisite; messages to workers count as dispatches for the budget holds; execution identity rules (full commits, assigned bases, verified pins, snapshot preflight before worktrees); compiled, executed and runtime-verified as separate states with `NOT_RUN` for launch and cache failures; configuration loading never owns execution; approval, preparation and proof kept apart; bounded repair with a stated reason for every repeat. Chapters 6, 7, 8 and 10 reconciled.
- Schema `allocation.schema.json`; templates `allocation.json`, `handoff.md`; skill `collect`; `resume` collects before anything else; `brief` writes the allocation record; `retro` adds the coordination numbers. Eight collector tests.

## 0.4.2

- Codex: the repository carries `.agents/plugins/marketplace.json`, so Codex can install it as a plugin from `~/.codex/config.toml` (`[marketplaces.sliceworks]` with a git source, `[plugins."sliceworks@sliceworks"]`); `scripts/install.sh` copy-installs the skills (and agents, for Claude Code without the plugin) into a project or user scope for Codex, Cursor and others. README documents both paths and what Codex gets today.

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
