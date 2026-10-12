# Lifecycle coverage: what the method misses, and how to widen it

Design note, 2026-10-12. Owner observation: the method covers the development window only, after a product vision exists and the scope is broken into slices. Two scenarios are not covered: "an idea becomes an MVP" and "a live product reaches its next milestone". The owner's framing is adopted here: **a milestone is a named goal made of increments; the MVP is one milestone name among others, not the only one.**

## 0. Summary

- Today the method covers one phase of one milestone: **Build**, with its verification, review, integration, demo and retrospective, plus a one-session **kickoff** that compresses Decide and Plan into an afternoon. Discover, Design, Accept, Release, Operate and Learn are either assumed done or declared "human acts" and left outside.
- The first run did all of those phases anyway, by hand and ad hoc: five analyses before the kickoff, a constitution and an acceptance contract with 54 user scenarios and 14 release-gate families, owner decision packets with 136 rows, reuse maps and a decoupling review before increment 1, a mid-run refocus that re-planned the increments, and a daily production review of real conversations. Eva did the same for its design phase with research rounds, a decisions-and-questions ledger, living architecture and specs, and a "Current" index with precedence rules. None of this is in the package. That is the gap.
- The fix is not to add a product-management suite. It is to extend the spine the method already has (state in files, a ledger with checkable rows, decisions with classes and veto windows, components that name their failure, a human only for human-only acts) across **nine phases** of a **milestone**, with one ledger whose rows have a `kind`, one decisions ledger, a milestone file, a user-scenario file, and skills that open and close each phase. Sections 4 and 6 list exactly what to add; section 8 phases it so that the schema changes land before the parser library is written.

## 1. The window the method covers today

| Phase | Covered | How |
|---|---|---|
| Spark, Discover | no | assumed: "the owner knows what to build" |
| Decide | kickoff only | one session; A2 defaults and class B decisions during Build |
| Design | no | binding documents (constitution, decision records, product contract) are inputs, never outputs |
| Plan | partly | increments and rows are written at kickoff; increment planning (surface maps, reuse, decoupling) was ad hoc |
| Build | yes | slices, tiers, review, merge, acceptance of rows, demo, retrospective |
| Accept (milestone) | partly | "engineering-complete" is defined; the owner's acceptance is a human act with no artifact |
| Release | no | "release is a human act by definition" |
| Operate | no | nightly T4 only |
| Learn | partly | the efficiency review learns about the process, never about the product |

Three assumptions underlie the window: the scope is decided and bounded; there is one run that ends; what happens after engineering-complete is someone else's problem. All three fail for a product that lives longer than one milestone, and the first assumption fails for an idea.

## 2. The wider model

```text
Product
  └── Milestone (named: Validated idea, MVP, Pilot, Launch, v2 ...; exit criteria; gate families)
        ├── Spark      one paragraph: who, what pain, why now
        ├── Discover   research rounds; claims with sources and verification; riskiest assumptions
        ├── Decide     the decisions ledger: product (A), method, technical (B); open questions with defaults
        ├── Design     invariants, architecture, specs with versions, the acceptance contract (user scenarios, gates)
        ├── Plan       the milestone plan: increments, exit demos, rows; increment planning; re-planning
        ├── Build      increments → slices → rows   (the method as it stands)
        ├── Accept     demo plus gate rows plus the owner's acceptance packet
        ├── Release    release checklist rows, environments, approvals, the one push
        ├── Operate    probes, incidents, hotfix lane, production review digests
        └── Learn      evaluations, metrics against the milestone's success metrics, feedback register
              └── feeds the next milestone's Discover
```

Definitions that the method needs and does not have:

- **Milestone.** A named goal with exit criteria: every engineering row passes or is parked on a human act, every gate family is closed by the owner or explicitly waived, and the success metrics the milestone promised are measured. "MVP" is the name of the first milestone with external users; "engineering-complete" is a state of a milestone, not the end of the method.
- **Release.** A deployment event to a named environment, with its own checklist rows. A milestone may contain zero releases (an internal milestone) or several (a live product).
- **Phase.** A set of artifacts, checks and skills with an entry and an exit. Phases of one milestone are not strictly sequential: Operate and Learn of milestone *n* overlap Discover and Decide of milestone *n+1*; a hotfix runs Build, Accept and Release in one day while the next milestone's Design is being written.
- **Row kind.** Today every ledger row is an acceptance scenario or a slice criterion with a test as its check. The other phases have rows too, with different checks: a claim verified against a source, a decision closed before a due date, a gate signed by the owner, a release step executed, a probe green in production, an evaluation verdict within its budget. One ledger, one schema, a `kind` field.

Autonomy differs by phase, and this is where the owner's time goes:

| Phase | Who leads | Owner involvement | Human-only acts |
|---|---|---|---|
| Spark | owner | writes the paragraph | none |
| Discover | research subagents, read-only | reads rounds; answers nothing | none |
| Decide | owner and coordinator | **highest**: answers open questions, or lets defaults apply with veto windows | scope, money, legal, real data |
| Design | architect session, reviewers | vetoes within windows; approves the acceptance contract once | approvals that bind real people (consent texts) |
| Plan | coordinator | reads the milestone plan | none |
| Build | coordinator and implementers | reads the dashboard | credentials for shared environments |
| Accept | coordinator prepares, owner accepts | **reads one packet, signs gate rows** | acceptance itself |
| Release | coordinator prepares, owner performs | **performs the deploy acts** | deploy outside the isolated environment, DNS, secrets |
| Operate | scripts and coordinator | notified on incidents | real-data access, external communications |
| Learn | evaluation subagents under caps | reads the verdicts | raising a money cap |

## 3. Raw material already produced, outside the window

| Phase | First run (CoverLetterBot) | Eva | Elsewhere in the owner's ecosystem |
|---|---|---|---|
| Discover | five dated analyses before the kickoff (process, multi-agent research, preparation, SDLC, agile and scope), each with sources | `docs/rounds/vN-slug/` frozen research-and-verification runs: `design.md`, `sources.md`, and in earlier rounds `register.md` (claims) and `verification.md`; a round is never appended to | the deep-research skill |
| Decide | owner decision packets (5 files, 136 rows, mostly unanswered), later `OWNER-DECISIONS.md` with classes and veto windows, class B lines in `STATE.md`, `decisions-archive.md` | `docs/decisions.md`: `D-NNN · title` entries with date, origin, status (proposed, active, superseded), relations (refines, supersedes), consequences to verify; `Q-NNN` open questions; "an owner answer arrives" workflow | Spec Kit `clarify` |
| Design | constitution v2 (invariants), ADRs 0071 to 0074, the MVP contract (roles, data scope, vocabularies, DDL plan, gates and lifecycle invariants, acceptance coverage), `scenarios.json` (54 user scenarios: id, title, journey stage A to H, roles, customer segments, release MVP/Next/Final, increment, `proves[]` row ids) | `docs/architecture.md` living design edited in place; `docs/specs/*.md` with format versions in names (`emf-1`); methodology bundles; the "Current" table in `docs/README.md` with status, last-reviewed date and the precedence rule (active decisions, then accepted specs, then the architecture) | `engineering-skills`: `documentation-standards` (ADR, runbook, postmortem templates), `review-plan`; Spec Kit `constitution`, `specify`, `plan` |
| Plan | the agile-and-scope plan (five increments, exit demos, scenario mapping, 14 release-gate families of which 8 are owner, legal, provider or operations acts), `reuse/` maps and the increment-1 decoupling review (seams, cores versus wires, lanes, hot files), the 2026-10-11 **refocus** that re-planned increments 0 to 7 mid-run, `BACKLOG.md` "Thinning candidates" | `docs/plans/*.md` with milestones V1 to V6, work packages, dependencies, exit criteria and scenario families; status rows in the Current table | `kanban-md` board |
| Accept | "engineering-complete" definition; `NEEDS-HUMAN.md` rows for the owner's acts; the "independent method acceptance" and "named pilot decision" gates | plan rows record "independent review, full gate passed; G1 not accepted" as separate verdicts: mechanism verified, quality not accepted | |
| Release | milestone push script gated on an owner decision; the isolated-environment rehearsal as a row; image mirror, DNS, secrets as human items | release builds outside the working tree, LaunchDaemons, signed releases (V3) | `engineering-skills` infra pack: CI/CD, Terraform, Helm, secrets |
| Operate | nightly T4; `daily-conversation-review` (reads real production traces, writes one PII-free digest with verdicts, incidents and fleet health), `gather-conversation-infra-data`, `inspect-pipeline-runs` | the pilot guide (`docs/pilot.md`): operator commands, health, restore rehearsal | `engineering-skills`: `incident-response`, runbook and postmortem templates |
| Learn | `eval/rank-v1.md`; `review-bot-conversation` (one biggest problem, where to fix it); scenario coverage on the dashboard | evaluation plans with scenario families, pinned corpora and a **cumulative money cap** ledger (every paid run recorded against a $15 authorization); "mechanism verified" kept separate from "quality accepted" | product-management plugin: `metrics-review`, `synthesize-research` |

Two conclusions follow. The material exists, so the phases are real work the owner already pays for; and it exists as prose in dated files that no script reads, so none of it shows on a dashboard, none of it has a check, and each project reinvents the shape.

## 4. Gaps and proposals, phase by phase

Each proposal names the failure it prevents, in the style of the component table. Artifacts live under the state directory unless said otherwise.

### 4.1 Spark and Discover

Missing: a place for the idea, and a disciplined research run that ends in verified claims rather than a plan written from memory.

- **`SPARK.md`** (one page): who, what pain, why now, what "done for the first milestone" would look like, what must be true for this to be worth building (the riskiest assumptions). Prevents: a backlog built on an unstated premise.
- **Rounds**, Eva's shape, generalized: `rounds/<n>-<slug>/` with `questions.md` (what this round must answer), `sources.md`, `register.md` (one claim per line: id, claim, source, confidence, verification verdict), `design.md` (the synthesis), frozen on close and never appended to. A new question opens a new round. Prevents: analyses that cannot be audited; the same question researched twice.
- **Claim rows** in the ledger (`kind: claim`): check = the register lint (every claim has a source and a verdict; no verdict older than its source). Prevents: a design resting on an unverified claim.
- **Experiments** for riskiest assumptions: a row (`kind: experiment`) with a measurable outcome and a budget; the check is the recorded measurement. Prevents: building the MVP to learn what a two-day experiment would have told.
- Skill **`discover`**: opens a round from `SPARK.md` or from a Learn output, dispatches read-only researchers (one question each), writes the register, runs the lint, closes the round, and lists the questions that became decisions. Hook: closed rounds join the protected list.

### 4.2 Decide

Missing: one decisions ledger that spans phases. Today there are three shapes (owner decision rows with veto windows, class B lines in `STATE.md`, and the project's own ADRs) and no open-question register, so questions wait in chat or in a 136-row packet.

- **`DECISIONS.md`**, one file, Eva's entry shape with the method's classes: `### D-NNN · title`, then date, origin (round, review, owner answer), **class** (A1 human-only, A2 product default with veto window, M method, B technical), status (`open`, `recommended`, `defaulted`, `decided`, `vetoed`, `superseded`), relations (refines, supersedes), the applied default and the consequence of reversing, consequences to verify. `### Q-NNN · question` entries with owner, due date, the default that applies at the due date, and the decision that closed them. `OWNER-DECISIONS.md` becomes a view the dashboard renders (A2 rows with open veto clocks), not a second file. ADRs stay the project's long-form record for class B decisions that deserve one; a D entry links to its ADR. Prevents: silent defaults; the same question answered twice differently; a decision without its evidence.
- **Decision rows** in the ledger (`kind: decision`): check = no `Q` past due without a default applied; every `D` cites a round, a review or an owner message. Prevents: a ready slice blocked on an unanswered question.
- Skill **`decide`**: turns a round's open questions into `Q` entries with recommended defaults, announces veto windows, applies defaults at the due date, records owner answers from chat into `D` entries, and keeps the Current index's precedence rule (active decisions over accepted specs over the architecture).
- The kickoff becomes the Decide-to-Plan boundary of the first milestone, not a separate thing.

### 4.3 Design

Missing: the phase that produces the binding documents the method consumes.

- **`INVARIANTS.md`** already exists as a template; it is the constitution in short form. Add the pointer to the long form (a constitution or the project's own document) and the rule that an invariant changes only through a decision.
- **`ARCHITECTURE.md`**, a living document edited in place, with the rule from Eva: a change must cite the `D` that caused it; sections that adopt a proposal are labelled. Prevents: design drift nobody can trace.
- **Specs with format versions** in `specs/`: formats and protocols, a version number in the name when the format is one. Prevents: silent format changes.
- **The acceptance contract**, two files the first run had as one prose document and one JSON file:
  - `SCENARIOS.json`: user scenarios, the layer above ledger rows: `id, title, stage (journey stage), roles, segments, milestone, proves[] (row ids)`. The dashboard already models this. Prevents: increments closing on rows that no user journey needs; a milestone whose scenarios nobody listed.
  - `MILESTONES.md`: per milestone its name, the promise, success metrics, exit criteria, and the **gate families** (owner, legal, provider, operations, security, data) each with its rows. Prevents: "MVP" meaning different things to the owner and the coordinator.
- **Threat model** for the material surfaces listed in the configuration: one page per surface, written at Design, used by the named-risk reviewer at Build. Prevents: named-risk reviews that reconstruct the threat model each time.
- **Design review** before Plan: the `review-plan` skill of the skills library, read-only, four dimensions, findings ranked. Prevents: a plan built on a design error that costs a slice to fix.
- Skill **`design`**: writes or updates the four artifacts from the decisions and rounds, calls Spec Kit `constitution` and `specify` where the project uses them, runs the design review, and registers `kind: spec` rows whose check is the spec lint (schema valid, no `TODO` in a frozen spec, every decision link resolves).

### 4.4 Plan

Missing: the milestone plan as a first-class file, the increment planning that was done by explorers ad hoc, and the re-planning event.

- **`MILESTONES.md`** (above) carries the ordered increments of each milestone; `BACKLOG.md` keeps the slices per increment as today.
- Skill **`plan-increment`**: the explorer-driven planning the first run did in `reuse/`: a surface map (what exists, what is missing per planned slice), a reuse audit (reuse instead of rebuild, one line per slice), a decoupling review (seams, cores that can start now versus wires that wait, lanes per writer, hot files to serialize by rebase), and the dependency columns filled. Prevents: slices rebuilt from scratch; three writers colliding on one file; idle slots.
- Skill **`refocus`**: the mid-milestone re-plan. Pause active slices at a safe point (candidate or commit), record the pivot as a `D` with the evidence, re-derive increments and scenarios, re-map rows, mark paused slices with the increment they resume in, and put a visible re-plan marker on the dashboard timeline. Prevents: a pivot done in chat that leaves the ledger describing the old product.
- **Thinning** as a standing section with rules: a row is thinned only by a decision; thinned rows keep their ids. Prevents: silent scope loss.

### 4.5 Build

Covered. Two additions the wider model needs:

- **Slice types**: `feature` (today), `fix` (from T3, nightly or an incident; brief under 50 lines; expedited review), `process` (an adopted retro proposal), `release` (section 4.7). The type sets the brief template and the review depth. Prevents: a hotfix waiting behind a feature's full ceremony, or skipping review because nobody said what the minimum is.
- **The run ends at the milestone**, not at "the MVP": the resume routine's goal is the current milestone's engineering-complete state.

### 4.6 Accept

Missing: the owner's acceptance as an artifact and a procedure.

- **Gate rows** (`kind: gate`): one row per gate family item, `human_act` set, check = the row's `done` date in `NEEDS-HUMAN.md` or a recorded decision. Prevents: a milestone declared done with gates nobody listed.
- **The acceptance packet**, one file per milestone: what to read (demo artifact, scenario coverage, open findings, metrics measured), what to decide (gate rows), what is parked. Written by the coordinator, read once by the owner. Prevents: acceptance by scrolling a dashboard.
- **Two verdicts, kept apart** (Eva's rule): mechanism verified (tests, demo) and quality accepted (the owner's or an evaluator's judgment on real or synthetic outcomes). Prevents: green tests read as product acceptance.
- Skill **`accept`**: runs the demo, assembles the packet, lists the gate rows, notifies the owner (one of the notifications), and on acceptance records the milestone as accepted with its evidence.

### 4.7 Release

Missing entirely, and it is where most human-only acts live.

- **Release slice** type with a checklist from `templates/release.md`: version and changelog, migrations plan and rollback, feature flags, runbook updated, isolated-environment rehearsal passed (a tier, call it T5: deploy to the isolated environment and run the smoke and the scenario subset there), approvals recorded as `D` entries, the push through the one script, post-release verification, the announcement (human act). Each item a `kind: release` row; checks are scripts where possible (rehearsal passed, tag exists, changelog mentions every merged slice), human acts otherwise.
- **Environments** named in the configuration (`isolated`, `staging`, `production`) with who may deploy where: agents deploy only to `isolated`; everything else is a human act with the exact command prepared. Prevents: an agent one `apply` away from production.
- Borrow, do not rewrite: the skills library's infra pack for pipelines, Terraform, Helm and secrets; its runbook template.
- Skill **`release`**: opens the release slice, drives the checklist, prepares the human acts with exact commands and verification by name, and records the release in `MILESTONES.md`.

### 4.8 Operate

Missing entirely except the nightly suite.

- **Probe rows** (`kind: probe`): health, error rate, latency, cost per day, each with a check that runs against the environment on a schedule; a red probe opens an incident. Prevents: learning about an outage from a user.
- **Incidents**: `INCIDENTS.md` (id, opened, severity, what, status, fix slice, postmortem link) and the postmortem template from the skills library; an incident opens a `fix` slice with an expedited path; a fifth notification type, `incident`. Prevents: fixes without a record; records without a fix.
- **Production review digest**: the daily-conversation-review pattern made generic: a script gathers the day's traces into a PII-free bundle, a bounded reviewer writes one digest (verdicts per case, incidents, user reactions, fleet health), candidates go to the feedback register. Real-data access is a human-only approval recorded once per environment. Prevents: a live product nobody reads.
- Skill **`operate`**: installs the probe schedule, runs the daily digest, opens incidents and fix slices, keeps the on-call rules (the coordinator is on call; the owner is paged only for human-only acts and severity one).

### 4.9 Learn

Missing: learning about the product, not only about the process.

- **Evaluation suites**: `evals/<suite>/` with a pinned corpus, graders, a budget in tokens **and money**, and verdict files per run (`kind: eval` rows; check = verdict present, within budget, above threshold). The package's own `claude plugin eval` is one instance. Prevents: quality claims without a corpus; paid runs without a cap.
- **The money ledger**: a second budget dimension next to the usage window, Eva's cumulative cap: every paid run records its cost against an authorization the owner granted (`D` entry); a guard refuses a paid run past the cap. Prevents: an autonomous run spending real money it was not given.
- **Metrics review** against the milestone's success metrics, once per increment or per release, by script where the metric is a number and by a bounded reviewer where it is a judgment.
- **Feedback register**: `FEEDBACK.md`, candidates with evidence (digest, metric, incident, owner note), not yet features; the next milestone's Discover reads it. Prevents: feedback that becomes a feature with no evidence, or evaporates.
- Skill **`learn`**: runs evaluations under caps, writes the metrics review, maintains the register, and proposes the next milestone's questions.

### 4.10 Cross-cutting

- **The documentation index**: Eva's "Current" table as `docs/README.md` or `<state-dir>/INDEX.md`: every living document with what it governs, status, last-reviewed date, translation state; the precedence rule; "anything outside this table is evidence or history". A check: no living document unreviewed for longer than the project's limit. Prevents: an agent treating a frozen note as current.
- **Security across phases**: threat model at Design, named-risk review at Build, a security review row in the release checklist, incident severity rules at Operate.
- **Compliance and legal as artifacts, approval as acts**: policy drafts, consent texts, processor and egress registers are Design outputs written by agents; their approval is a gate row. Prevents: legal work discovered at release.
- **Project kinds**: a product (all phases), a library or tool such as this package (rows are tests and evals; Release is a tag and a marketplace entry; Operate is issue triage), a research project (rounds dominate; Build is small), an infrastructure project (Release and Operate dominate). The profile chooses phases; the ledger's `kind` field makes the dashboard the same for all.

## 5. The two scenarios, end to end

### 5.1 An idea becomes an MVP

1. **Spark** (owner, an hour): `SPARK.md`, the riskiest assumptions, a name for the first milestone and what it promises.
2. **Discover** (autonomous, one to three days): one round per assumption; researchers read, the register fills, the lint passes, the round freezes. Open questions become `Q` entries with recommended defaults.
3. **Decide** (owner asynchronous, two days of veto windows): the owner answers what only they can (scope, money, real data) and lets defaults apply elsewhere. The decisions ledger is the record.
4. **Design** (architect session, autonomous with veto windows): invariants, architecture, specs, `SCENARIOS.json` with the MVP's scenarios, `MILESTONES.md` with the MVP's gate families and success metrics, threat models for the material surfaces, a design review.
5. **Plan** (coordinator): increments with exit demos, rows per scenario, first contracts, `plan-increment` for increment 0, one ready brief per writer. This is today's kickoff, now with its inputs on file.
6. **Build** (autonomous): the method as it stands, increment by increment, until the MVP is engineering-complete.
7. **Accept** (coordinator prepares, owner reads one packet): demo, coverage, gate rows; the owner signs the gates that are theirs.
8. **Release** (release slice; the owner performs the acts): rehearsal in the isolated environment, approvals, the push, production deploy by the owner with the prepared commands, post-release verification.
9. **Operate and Learn** begin: probes, the daily digest, the first evaluation runs under caps, the feedback register. The MVP milestone closes when its success metrics are measured, whatever they say.

### 5.2 A live product reaches its next milestone

1. **Learn** produces the inputs: the feedback register, the metrics review, the incident history, the evaluation verdicts. The owner names the next milestone and its promise in `MILESTONES.md` (an A2 default if they do not).
2. **Discover, light**: one round on what changed since the last milestone's rounds; most claims carry over, some are re-verified.
3. **Decide**: new `Q` entries; the ones that reopen old `D` entries supersede them explicitly. If the evidence contradicts the current increments, this is a **refocus**: pause, record, re-plan.
4. **Design, delta**: architecture sections cite the new decisions; specs bump their versions; new scenarios join `SCENARIOS.json` under the new milestone; gate families are copied and edited.
5. **Plan and Build** as before. In parallel, **Operate** continues on the live product: a red probe opens an incident, a `fix` slice runs the expedited path, a release slice ships it, the postmortem becomes a retro item. The dashboard shows both lanes: the next milestone's increments and the live product's incidents and releases.
6. **Accept and Release** of the new milestone; **Learn** feeds the one after.

### 5.3 Two other kinds, briefly

A **library or tool** (this package): Spark and Discover are the design notes; Design is the manifest and the schemas; rows are schema tests, hook red-team cases and plugin evals; Release is a version bump, a tag and the marketplace entry; Operate is issue triage; Learn is the eval report over releases. A **research-first project** (Eva before its first executable core): rounds dominate for months, Decide and Design are the product, Build is a thin spine; the ledger's rows are claims, decisions and specs, and the dashboard shows rounds and open questions, not slices.

## 6. What changes in the package

**Method.** A new chapter `00-lifecycle.md` (product, milestones, phases, row kinds, autonomy by phase) before the existing twelve; new chapters for Discover and Decide, Design and Plan, Accept and Release, Operate and Learn; the component table gains one row per new component; the glossary gains milestone, release, phase, round, gate family, row kind.

**Ledger schema.** `kind` on the feature row, default `scenario`, values `scenario | criterion | claim | experiment | decision | spec | gate | release | probe | eval`; `milestone` next to `increment`. The check semantics per kind are documented in the schema. This is a breaking change for the schema and must land before the parser library (plan phase 1) is written.

**New files and templates.** `SPARK.md`, `rounds/<n>-<slug>/` (questions, sources, register, design), `DECISIONS.md` (D and Q entries; `OWNER-DECISIONS.md` becomes a rendered view), `ARCHITECTURE.md` skeleton, `specs/README.md`, `SCENARIOS.json` with its schema, `MILESTONES.md`, `threat-models/<surface>.md`, the acceptance packet, `release.md` checklist, `INCIDENTS.md`, `FEEDBACK.md`, `evals/README.md`, the money ledger `metrics/money.jsonl` with its schema, `INDEX.md` (the Current table).

**New skills.** `discover`, `decide`, `design`, `plan-increment`, `refocus`, `accept`, `release`, `operate`, `learn`. `kickoff` becomes the composition `discover` (light) → `decide` → `design` → first `plan-increment` for a project that starts with a known scope.

**Hooks and checks.** Closed rounds and frozen specs join the protected list (configuration, not code). A money guard on `PreToolUse` for the commands the configuration marks as paid (`SW_PAID_CMDS`), refusing past the cap. The T0 of a project with living design documents gains two lints: a change to `ARCHITECTURE.md` cites a `D`; no `INDEX.md` row is past its review limit. A fifth notification, `incident`.

**Dashboard.** The top level becomes milestones with phase chips; the Build view is today's page; new panels for rounds and open questions, decisions with veto clocks, scenarios by milestone, gates, releases and environments, probes and incidents, evaluations and the money ledger. The snapshot schema gains `milestone`, `round`, `claim`, `release`, `probe`, `incident`, `eval` entities.

**Agents.** Two profiles: `researcher` (read-only, one question, writes a register section) and `architect` (writes only the design surfaces, as the contract author writes only contract surfaces). Both enforced by the role guard on `agent_type`.

## 7. Boundaries, so the package does not become everything

`sliceworks` owns the life cycle, the ledgers, the gates, the coordination and the dashboard. It does not own how to do engineering (the skills library's packs: Go, database, infra, incident response, documentation standards), how to write a product spec or a metrics review (the product-management plugins), or legal content. Each phase skill calls those where they exist and otherwise leaves a `TODO` row, never a half-written how-to. The test for a new file in this repository is the one the method already applies to itself: it names the failure it prevents, and it is removed when that failure stops occurring.

## 8. Phasing, relative to the existing plan

The current plan (extraction analysis, section 10) has phases 0 to 7 on depth: schemas and parser library, harness, skills, dashboard, Eva, dashboard v2, back-port. Breadth is a second track; its first step must precede depth phase 1 because it changes the schema.

| Version | Breadth step | Why here |
|---|---|---|
| 0.2 | the lifecycle chapter; `kind` and `milestone` on the row; `SCENARIOS.json`, `MILESTONES.md`, unified `DECISIONS.md`; `refocus` | the parser library (depth phase 1) must implement the final shapes once |
| 0.3 | Discover and Decide: rounds, `SPARK.md`, `discover`, `decide`, the `researcher` agent, the Current index | Eva's next design round can run on it |
| 0.4 | Design and Plan: `ARCHITECTURE.md`, specs, threat models, `design`, `plan-increment`, the `architect` agent | before the first new project adopts |
| 0.5 | Accept and Release: gate rows, acceptance packet, release slice and checklist, environments, T5 rehearsal | before any adopted project ships |
| 0.6 | Operate and Learn: probes, incidents, digests, evaluations, the money ledger and guard, `FEEDBACK.md` | before any adopted project has users |

## 9. Decisions for the owner

1. **One ledger with `kind`, or one file per kind.** Recommendation: one ledger; the dashboard and the scripts stay simple, and a scenario row and its gate rows sit together.
2. **Adopt Eva's `D-NNN · title` entry shape as the unified decisions ledger**, with the method's classes added. Recommendation: yes; it is the better-tested of the two and already carries status, relations and consequences.
3. **Phase names.** Spark, Discover, Decide, Design, Plan, Build, Accept, Release, Operate, Learn. Alternatives welcome; the model does not depend on the words.
4. **Scope of the first public version.** Recommendation: 0.2 and 0.3 before any adoption beyond Eva; 0.4 to 0.6 as the first adopted product approaches release.
5. **Money as a first-class budget.** Recommendation: yes, from 0.2 in the schema and from 0.6 as a guard; the first run never spent money autonomously, Eva already does under a cap.
