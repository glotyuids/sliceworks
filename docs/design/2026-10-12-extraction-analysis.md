# Extracting the development process into a reusable package

Analysis, 2026-10-12. Requested by the owner; written by the owner-level session. Scope: what of the Assessment Lab development process can leave this repository, in what form, how a person interacts with it, how the dashboard becomes generic, and how the result is delivered into Claude Code and Codex, with Eva as the first consumer. This note proposes; it creates nothing outside this repository.

## 0. Summary

- **What travels.** The method (principles, roles, lifecycles, decision classes, message protocol, tiers, review and merge rules, budget holds, the improvement loop, autonomous operation), its harness (eight state-file formats, eight hooks, seven agent profiles, about thirty scripts, the prompts and templates), the dashboard, and the Codex adapter. About two thirds of the files are generic in shape and need their hard-coded values lifted into one configuration file; the rest is the Assessment Lab instance and stays.
- **Form.** One new repository that is at once a Claude Code plugin (agents, skills, hooks), an Agent Skills pack (so Codex and Cursor read the skills), a scaffold (templates and schemas written into a project by an `adopt` skill, stamped and drift-checked exactly as your `engineering-skills` library does), a Python package (parser library, schemas, telemetry, dashboard generator, tests) and a method book. Registered as one more plugin in the `engineering-skills` marketplace so installation is one `/plugin install`.
- **Interaction.** Twelve scenarios, ten touchpoints. Chat is for kickoff and exceptions; everything else is a file plus one of four notifications. The owner needs two skills (`adopt`, `resume`) and a dashboard; a lite profile serves a solo project such as Eva today.
- **Dashboard.** Keep the look and the rules (one file, tokens, eight components, detail on demand, honest unknowns). Split the 1,490-line script into collect, compute and render with a snapshot schema between them; add adapters so any project, with or without this method, gets the page; build the multi-page, tabbed version on the older generator's template-plus-payload pattern.
- **Delivery.** A hybrid: the Claude plugin for discovery, agents, skills, hooks and behaviour evals; installed stamped copies for the executable harness and templates, because launchd jobs, Codex and CI must run without Claude; the same copy-install for Codex in v1, with a shared plugin for both runtimes as the second milestone (Codex reads the same manifest); an MCP server over the state files is a later option, not a first step. One verified constraint shapes the design: plugin agents ignore frontmatter hooks, so role enforcement moves to plugin-level hooks keyed on the agent type.
- **Name.** "AI-DLC" is AWS's methodology name since 2025. Recommended: `slicewright`, tagline "an autonomous development life cycle for AI coding agents".
- **Found on the way.** Two live bugs in the harness (the stall detector crashes silently; the budget hooks ignore Codex reset timestamps), both flagged as separate tasks.

## 1. The process, stripped of the product

Everything below is what remains of `docs/assessment-lab/PROCESS.md` once Assessment Lab, Go, PostgreSQL and the CoverLetterBot repository are removed. This is the method; the next section says which files carry it.

### 1.1 Eight principles (unchanged, already generic)

1. One writer per slice; parallelism across independent vertical slices behind frozen contracts, never across the layers of one feature.
2. Reads fan out, writes do not: exploration, review, contract drafting and verification run in clean-context subagents that return summaries.
3. Executable truth before model judgment: a deterministic check decides whether a candidate is reviewable; a reviewer sees diff, brief and check log.
4. State lives in files the host enforces: a feature list with pass flags, a state file, a progress file, briefs, hooks. No receipts, grants or acknowledgements.
5. Steer by connected outcomes: progress is the count of acceptance scenarios passing end to end on the integration branch.
6. Context is the budget: a short always-on file, no polling by a model, subagents for anything verbose.
7. Measure, then change, then measure: a bounded efficiency review per increment, at most three process changes per retrospective, each with a metric and a sunset.
8. Autonomous by default, human by exception: every decision has a recorded default and a veto window; only human-only acts wait for a person, and the run never idles on them.

The design rule above the principles also travels: every harness component names the failure it prevents, and a component whose failure stops occurring is removed at the retrospective.

### 1.2 Roles and topology

| Role | Generic definition | Project-specific today |
|---|---|---|
| Owner | One kickoff session, then asynchronous: performs human-only acts, may veto defaults, may stop the run, reads status and demos | the owner's 15% budget share |
| Coordinator | One long-lived session on the integration branch; keeps the state files, freezes contracts, writes briefs, dispatches and resumes implementers, reviews through subagents, merges by SHA, runs the merge gate, records usage, runs demo and retrospective; writes no product code | model and effort choice, branch name |
| Slice implementer | One subagent, one worktree, one branch, one slice; plans its own work, tests first, T0 every turn, T1 before `CANDIDATE`; returns only `CANDIDATE`, `BLOCKED`, `HOLD` | the database-per-worktree bring-up, Go and npm commands |
| Reviewer | Fresh context, read-only, diff plus brief plus check log; correctness and stated requirements only; resumed for the delta | none |
| Named-risk reviewer | Second verdict, one named question, at the first implementation of a material boundary | which surfaces count as material (access, RLS, erasure, private media, grounding) |
| Contract author | Drafts the frozen interface for one slice: paths, DTOs, state transitions, error codes, decisive examples, golden fixtures | OpenAPI, Spec Kit |
| Explorer | Read-only map of code; returns paths, symbols, a short summary | graph MCP profiles |
| Efficiency reviewer | Reads telemetry and friction notes once per increment, writes at most three proposals to a dated file and an append-only log | none |

The topology is generic: level 0 owner, level 1 coordinator, level 2 implementers (worktree isolation) plus short-lived helper subagents, spawn depth two.

### 1.3 Lifecycles and state machines

- Product: increments, each ending in an automated demo and a retrospective; the run ends at the engineering-complete state (every feature row passes or is `blocked_on_human`).
- Increment: `planned → started → running → demo → retro → closed`, with explicit entry conditions per state.
- Slice: `proposed → ready → active → candidate → in_review → repair → merged → green → accepted`, plus `blocked`, `blocked_on_human`, `waiting`, `stopped`.
- Decision: `open → recommended → decided | defaulted | vetoed → applied`; classes A1 (human-only), A2 (product default with veto window), B (technical contract, coordinator), C (local, implementer).
- Contract: `draft → frozen → amended → retired`; an implementer that needs something a contract does not give returns `BLOCKED`, never invents a field.
- Defect: where found decides what happens (fix in slice; finding and delta review; T2 revert; a fix slice; a retro item with a new named check).

### 1.4 Preparation: Definition of Ready, three stages, one artifact each

Six readiness conditions (outcome and scenarios named; contract frozen with fixtures; decisions recorded; reuse map written; verification named; workspace allocated). Stage 1 contract, stage 2 brief of at most 150 lines in eight sections plus material-boundary flag and goal condition, stage 3 the implementer's own fifteen-minute plan. Preparation runs one slice ahead per writer; that is the pull signal.

### 1.5 Verification tiers

The tier *structure* is generic: T0 pre-commit under two minutes enforced by a Stop hook; T1 slice gate before a candidate; T2 merge gate in the background, a failure reverts the merge; T3 milestone full suite; T4 nightly. The *commands* behind each tier are the project's. The two non-negotiable rules travel with the structure: a check must actually run (a renamed or unwritten test never counts), and tests are never removed or weakened to pass; a skipped check is `NOT_RUN`, never a pass.

### 1.6 Review, integration, acceptance

Review output format (`REVIEW <slice> <sha> VERDICT`, findings with severity, file, line, evidence, impact, and an explicit not-reviewed list); severity by product impact; the implementer decides scope; two substantive rounds in one family stop the slice for diagnosis. Merge by SHA with `--no-ff`, one at a time, T2 in the background, revert on red. Acceptance flips feature rows with test name and log path and records timestamps.

### 1.7 Communication: six message shapes, eight per slice

`BRIEF`, `CANDIDATE`, `BLOCKED`, `FINDINGS`, `CONTRACT`, `HOLD`. Never progress, acknowledgements or status requests. The owner channel is files plus a notification on four events (new human-only item, increment close, kill-switch stop, budget hold).

### 1.8 Budget and models

Generic: read usage at dispatch, merge and hourly; a dispatch hold and a stop line as percentages of the provider window; a per-slice budget box; concurrency caps; model routing by role (cheap read-only explorers, mid-tier implementers and ordinary review, top-tier coordinator, named-risk review and contract authoring). Project-specific: the percentages, the model identifiers, the writer cap formula.

### 1.9 Metrics and the improvement loop

Three outcome numbers (scenarios passing, cycle times, usage percent), four tax numbers (messages, coordinator turns, documentation-only commit share, stale human-only items), quality numbers (review rounds, T2 revert rate, red rate, escaped defects). Telemetry comes from scripts, never a model turn. Friction notes at the source (`FRICTION:` lines). One bounded efficiency review per increment, proposals in a fixed shape with observed, cause, first-ask-can-it-be-removed, change, expected effect, cost, verify-by, sunset, prior art. The retrospective adopts at most three, revisits last time's, and walks the component table.

### 1.10 Autonomous operation

The human-only list (credentials, money, legal and consent, real personal data, irreversible acts outside the repository, external communications in the owner's name, changes to the list itself, holds, scope or binding documents); veto windows; mechanical boundaries (worktree isolation, deny lists, protected files, no merge authority for implementers); stall and runaway control (`maxTurns`, no-commit stall rule, two-round stop, budget box); the kill-switch file; audit through dated files in git.

### 1.11 What the three retrospectives added that the manual does not yet state

These are lessons from running the process for three increments; they belong in the extracted method as rules or checks, not as history:

- A session-recovery file outside git (`.run/coordinator-session.md`) with agent ids, background task ids and next actions, updated at every dispatch and merge, read first after a compaction. Without it running slices cannot be resumed.
- Stall detection and ready-slice detection as scripts (`stall-check.py`, `next-ready.py`) that wake the coordinator with `STALL` and `READY` lines; dependency columns (`depends_hard`, `depends_soft`, `touches`) on the slice table.
- Stale bases are the main rework cost: a candidate rebases onto the integration head before review, and a merge checks any pinned submodule or gitlink against the head.
- Turn limits are hit by long waits, not by long work; a slice's budget must count wall time of gates separately.
- A plan review before code for material-boundary slices (adopted proposal EP-1-3) catches classes of defects cheaper than code review.
- Harness self-check: a broken settings file or hook must be visible within fifteen minutes (adopted EP-1-1, a preflight in the wake timer).
- Protected files are enforced at the diff, not by matching command text (proposal EP-0-2).
- Named-risk review has found a behaviour-changing defect in every media slice; it is a security invariant, never pruned.

## 2. What can be extracted, file by file

The process lives in three layers. The first two leave with the package; the third is what every adopting project writes for itself.

### 2.1 Layer A, the method (documents)

| Source today | Becomes | Sanitizing needed |
|---|---|---|
| `PROCESS.md` sections 1, 3 to 12, 15 (withdrawn list), 17, 18 | `method/*.md`: principles, roles, lifecycles, preparation, verification, review, integration, communication, budget, metrics, improvement loop, autonomy, glossary | Remove Assessment Lab, Go, PostgreSQL, the 85/15 split, model names, branch names; keep the numbers only as worked defaults |
| `PROCESS.md` 13.4 component table | `method/components.md`, the "every component names its failure" table | None; it is already generic |
| `PROCESS.md` 2 (product frame), 16 (transition record), 14 (as implemented) | Stay in the project | They are the instance, not the method |
| The five rationale analyses in `docs/plans/*-2026-10-09.md` and the v2 design note | `rationale/`: the eight research findings, the measured waterfall, the agile selection, the preparation design; evidence summaries with sources | Strip project measurements and names; keep the findings and the citations |
| Retrospectives `retros/increment-0..2.md`, `PROPOSALS.md` | `rationale/lessons.md`: the eight lessons in section 1.11, each as a rule or a check | Replace slice numbers and media specifics with the generic failure |
| `START.md` | `method/start-and-recover.md` plus the prompt templates | Parameterize paths, models, writer cap |
| `RUNTIMES.md` 1 to 8 | `runtimes/codex.md`, the two-host adapter rules | Sections 9 to 11 (verified facts, incident log, handoff snapshot) stay in the project |
| `CLAUDE.md`, `AGENTS.md` | `templates/AGENTS.fragment.md`: the "rules for every agent" block and the roles block, to be included by the project's `AGENTS.md` | Commands and invariants become the project's own lines |

### 2.2 Layer B, the harness (mechanics)

Classification by the inventory: G generic as is, P generic shape with hard-coded values to lift into configuration, PS project-specific.

**State files.** All eight formats are generic once the paths are configurable; today they are documented only in prose (PROCESS.md 13.2) and parsed by four different scripts with three different table parsers. The package should carry a schema for each and one parser library.

| File | Generic schema | Notes from the inventory |
|---|---|---|
| `FEATURES.json` | row `{id, increment, slice, title, cwd, check, passes, evidence, human_act, tasks}` | `check` runs with `sh -c` from `cwd`; agents may change only `passes` and `evidence`. Rows for increments 3 and up are hash-pinned by `mvp_scope.py`, a project-specific policy that does not travel |
| `STATE.md` | sections Integration, Increment, Contracts, Slices, Milestones, Holds, Blocker, Queued, Decisions (class B); the Slices table now carries `depends_hard`, `depends_soft`, `touches` | State vocabulary has drifted: `green`, `paused`, `stopped`, `HOLD`, `source_hold` appear in the file but not in the dashboard's or `status.py`'s vocabularies. The package defines the vocabulary once |
| `BACKLOG.md` | `## Increment N: title`, exit demo, scenarios, slice table | Parsed from prose by regex today; the package should give it a table-only shape |
| `PROGRESS.md` | `## <ts>, <role> (<model>)` entries with Done, Next, Blocked and `FRICTION:` lines | Append-only; 595 KB today, so the dashboard reads only the tail |
| `OWNER-DECISIONS.md` | `id, class, increment, question, applied default, consequence of reversing, veto by, status, owner note` | `A2-PUSH` and the hold rows are read by scripts; those ids become configuration |
| `NEEDS-HUMAN.md` | `id, increment, act, unblocks, urgency, added, done` | Generic |
| `STATUS.md`, `STOP`, `.run/coordinator-session.md` | script output; kill switch; session recovery file | The recovery file is not in PROCESS.md; it should be a first-class artifact |
| `metrics/usage.jsonl`, `tiers.jsonl`, `slices.jsonl` | usage reading; tier run; per-slice telemetry | `slices.jsonl` is expected by `status.py` and the efficiency reviewer but does not exist. `weekly_reset` is an ISO string in Claude rows and an epoch integer in Codex rows; the schema must fix one |

**Hooks** (`.claude/hooks/`, eight files, all POSIX sh with jq):

| Hook | Class | Lift into configuration |
|---|---|---|
| `stop-guard.sh` kill switch | G | the STOP path |
| `coordinator-stop.sh` | G | the STOP path |
| `budget-guard.sh` dispatch holds | P | usage file path, the explorer allowlist, the thresholds now embedded in the message text, the macOS-only `date -j` |
| `budget-stop.sh` stop line | P | thresholds via `budget.conf` |
| `implementer-guard.sh` | P | the protected-path list (must equal `protected-diff.sh`'s), the worktree layout, the integration-branch prefix, the infrastructure command deny list |
| `implementer-stop.sh` T0 gate | P | the verify command and tier name; `.blocked` escape stays |
| `contract-write-guard.sh` | P | the list of contract surfaces (OpenAPI file, specs dir, fixtures) |
| `retros-write-guard.sh` | P | the retros path |

Roles are identified by which agent definition is running (hooks attached in agent frontmatter), never by branch or environment; the coordinator is "the session with no role hooks". Under Codex the launcher sets a role variable. In the package the attachment changes: a plugin's agents cannot carry frontmatter hooks, so the role hooks become plugin-level hooks that read the `agent_type` field of their input (section 6.2). The rule itself, role by agent definition, travels.

**Agent profiles** (`.claude/agents/`, nine):

| Profile | Class | Keep as | Parameters |
|---|---|---|---|
| `slice-implementer` | P | core | integration branch, state file paths, init and verify commands, explorer names, `maxTurns`, message cap |
| `code-reviewer` | P | core | the project's invariant list, injected from configuration |
| `security-reviewer` (named risk) | P | core | material-boundary surfaces, binding documents |
| `contract-author` | P | core, optional | contract surfaces; the OpenAPI and Spec Kit specifics become an adapter |
| `efficiency-reviewer` | P | core | metrics paths, retros path |
| `code-explorer` | P | core | drop the Go and RabbitMQ wording |
| `codebase-memory`, `codebase-memory-scout` | G | optional pack, needs the graph MCP | none |
| `go-build-resolver` | P | language pack (`go`), not core | the Go conventions skill path |

**Scripts** (`scripts/dev/`, 45 files):

| Group | Files | Class | What travels |
|---|---|---|---|
| Verification harness | `verify-slice.sh` | P | the skeleton: slice id resolution, `outputs/slices/<slice>/<tier>-<ts>.log`, `run()` that records every step and never aborts, `RESULT=`/`LOG=`/`FAILED:` protocol, `tiers.jsonl` row, slot queue for a shared resource, self-pinning to the harness commit. The tier bodies (gofmt, go vet, golangci-lint, npm, OpenAPI compare, `mvp_scope.py` scope checks that run in every tier) are the project's and move to a per-project tier definition |
| Must-run check | `gotest-must-run.sh` | PS as built, G as an idea | "a named test must actually run and pass" per language: Go `-json` events, pytest `-rA`, vitest or Playwright `--grep` with a report. Today it is welded to the `mvp_scope.py` bundle and even reads the harness commit from git |
| Affected set | `affected.sh`, `test_scope.py` | P (Go) | an interface "changed paths to test targets" with a Go implementation; other stacks plug their own |
| Budget | `record-usage.sh`, `budget.conf`, `hold-wait.sh`, `wake.sh` | P | all four; fix the usage window label regexes and the ISO-only timestamp parser (see the two bugs below) |
| Flow telemetry | `stall-check.py`, `stale-procs.py`, `next-ready.py`, `status.py` | P | all four, after the shared parser library replaces their private parsers; `stale-procs.py` keeps a project adapter for what "a hung process" looks like |
| Dashboard | `dashboard.py`, `dashboard-loop.sh`, `publish-dashboard.sh` | P, P, PS | section 5 |
| Protected files | `protected-diff.sh`, `redteam-protected.sh` | G with a list | both, with the list in configuration; the red-team corpus becomes a self-test of the package |
| Worktrees and merge | `new-worktree.sh`, `pin-t2.sh`, `milestone-push.sh` | P | branch prefix, worktree root, submodule handling, the decision id that authorizes a push |
| Codex runtime | `codex-dispatch.sh`, `codex-hook.sh`, `codex-session-guard.sh`, `codex-implementer.rules`, `codex-status.sh`, `sync-runtime.py` | G, G, P, G, G, P | all; `sync-runtime.py`'s model map becomes configuration, and its drift check (byte-identical rendered agents) is the parity test |
| Logging helpers | `run_logged_check.py`, `summarize_check.py`, `automation_errors.py` | G | all three |
| Scheduling | `install-schedules.sh` | P (macOS launchd) | a launchd adapter plus a cron adapter |
| Environment and demo | `init.sh`, `run-api.sh`, `dev-idp.mjs`, `demo.sh`, `reap-test-dbs.sh`, `check-migration-source.py`, `mirror-images.sh`, `devstatus-finish.sh` | PS | stay; the package defines the *contract* (`init` with `--smoke` and `--app`, `demo <n>` that runs an increment's rows and writes `demo.md`) and a database pack may later carry the per-worktree database pattern and the migration preflight |
| Acceptance scope policy | `mvp_scope.py`, `mvp_scope_ast.go`, `mvp-test-scope.json` | PS | stay; a generic "pinned acceptance scope" is a candidate for a later version, not for v1 |

**Templates and prompts.** Brief (eight sections, 150 lines, material-boundary flag, goal condition, Dependencies section), contract document, retrospective page, proposal block, demo summary, `settings.json`, `.worktreeinclude`, the coordinator resume prompt, the implementer dispatch prompt, the reviewer prompt, the `FINDINGS` relay, the named-risk prompt. All P: placeholders for paths, branch, commands and models.

### 2.3 Layer C, the project adapter

What an adopting project supplies, and nothing else:

- Paths: state directory, outputs directory, worktree root, protected files, contract surfaces, retros directory.
- Branches: integration branch, slice branch prefix, submodules or gitlinks to check at merge.
- Tier commands: `t0`, `t1`, `t2`, `t3`, each a list of named steps; the affected-set computation; the must-run implementation for its test runner.
- Environment: how to bring up a checkout or worktree (`init`), how to prove the baseline (`smoke`), how to run an increment demo.
- Policy values: budget thresholds and window labels, model routing, writer cap, stall minutes, turn limit, veto windows, time zone.
- Lists: the invariants reviewers must check, the material-boundary surfaces, additions to the human-only list, the infrastructure commands implementers may never run.
- Instance documents: constitution or equivalent, ADRs, the product contract, the backlog content.

### 2.4 What stays behind entirely

The constitution and ADRs, the MVP contract, the Spec Kit tree (`.specify/`, including the three templates modified for this project), the briefs, contracts, findings, reuse maps, demos and retros as content, `settings.local.json`, the devstatus hosting scripts, the acceptance-scope policy and its 2,600-line test file, `init.sh`, `demo.sh` and the dev identity provider. They are the Assessment Lab instance of the method.

### 2.5 Two bugs found on the way (already flagged as separate tasks)

- `stall-check.py` iterates over the tuple returned by `dashboard.agent_usage()` and crashes on the first active slice; `wake.sh` discards its stderr, so no `STALL` line has ever been printed and the dashboard's idle chip never renders.
- `budget-guard.sh` and `hold-wait.sh` parse reset times as ISO strings only; Codex rows store an epoch integer, so the reset check is skipped and the hold timer reports "no hold active" at 82% weekly.

Both are evidence for the extraction: a single parser library and a schema with one timestamp format would have prevented them.

## 3. The form of the new project

### 3.1 What already exists on this machine, and why it matters

You already run a public, tool-agnostic skills library, `engineering-skills` (`engineering-skills`, github.com/glotyuids/engineering-skills, Apache-2.0). It settled four rules that the new package must respect rather than reinvent:

- Skills are strict Agent Skills `SKILL.md` directories; `AGENTS.md` is the always-on file and `CLAUDE.md` is `@AGENTS.md`.
- Install by copying with a provenance stamp (`metadata.source`, `metadata.version`); drift is detected by `scripts/check-drift.sh`; fixes go upstream first; project specifics live in `<skill>-project` delta skills.
- Packs are installable three ways: the agent follows a procedure in the README, a Claude Code marketplace (`.claude-plugin/marketplace.json` with one plugin per pack, `plugins/<pack>/skills` symlinked to `skills/<pack>`), or `scripts/install.sh`.
- Public content policy: English, no hostnames, no local paths, no personal data.

Eva (`jarvis`, README title "Eva") already consumes it: 18 skills from the `go`, `database`, `llm` and `process` packs in both `.claude/skills` and `.agents/skills`, plus ten `*-project` deltas, four Go agents, and `@AGENTS.md`. The `process` pack has `kanban-md` (a file-based board), `review-plan`, `git-workflow`, `documentation-standards`, `integration-testing`, `incident-response`, `deslop` and `security-guidelines`.

The method extracted here is a different kind of thing from a skill: it has executable parts (hooks, scripts, a dashboard generator, schemas, tests), state-file templates that are written into the project, and runtime wiring (`settings.json`, agent profiles, Codex config). The skills library has no slot for hooks, scripts or templates in its manifest, and its release cadence is that of documentation. Hence the recommendation below.

### 3.2 Recommendation: a separate repository, published through the same marketplace

One new repository under `<name>` (your folder policy; the name is section 8). It is at once:

1. **A Claude Code plugin** (`.claude-plugin/plugin.json`, `agents/`, `skills/`, `hooks/hooks.json`, scripts under the plugin root): the parts that can run from the plugin cache without being copied into the project.
2. **An Agent Skills pack**: its skills are plain `SKILL.md` directories, so Codex, Cursor and Copilot read them through `.agents/skills` exactly as the library's packs do.
3. **A scaffold**: templates and schemas that the `adopt` skill writes into the project, stamped with source and version like a skill, checked by the same drift procedure.
4. **A Python package** for the harness library (parsers, schemas, compute) and the dashboard generator, with tests, versioned with the repository.
5. **A method book**: the generic process and its rationale, in `method/` and `rationale/`.

It is registered as one more plugin in `engineering-skills/.claude-plugin/marketplace.json` pointing at the new repository, so installation is `/plugin install <name>@engineering-skills`, next to `go` or `process`. The library's README gains one row and one install line; the library itself does not change shape. If later the package stabilizes into documentation plus a few scripts, folding it in as a pack is a mechanical move.

### 3.3 Layout

```text
<name>/
  README.md                      what it is, install, the three profiles (full, lite, dual-runtime)
  AGENTS.md / CLAUDE.md          contributor guide (the library's pattern)
  .claude-plugin/plugin.json     Claude Code plugin manifest
  agents/                        coordinator-facing profiles: slice-implementer, code-reviewer,
                                 named-risk-reviewer, contract-author, efficiency-reviewer, code-explorer
  skills/
    adopt/                       S1: scaffold a project (asks once, writes templates, runs the self-test)
    resume/                      S7: the coordinator start and recovery routine
    kickoff/                     S2: scope, increments, feature rows, first contracts, kickoff decisions
    brief/                       write a slice brief from FEATURES.json rows and the reuse map
    retro/                       increment close: demo, efficiency review, retrospective, pruning
    update/                      S12: drift check and reinstall
    status/                      owner conveniences: status, veto, done (optional, later)
  hooks/
    hooks.json                   plugin-level: kill switch and budget guard on PreToolUse, role guards keyed on
                                 agent_type, T0 gate on SubagentStop, coordinator Stop, SessionStart context,
                                 WorktreeCreate bring-up
    *.sh                         the hook bodies, reading paths and lists from the project configuration
  bin/                           the harness and dashboard CLIs, on the session PATH while the plugin is enabled
  evals/                         claude plugin eval cases for adopt, resume, brief
  harness/                       Python package: schemas (JSON Schema), parsers, compute, telemetry
    schemas/                     FEATURES row, STATE sections, usage reading, tier run, snapshot
  dashboard/                     Python package: collect (adapters), compute, render (components, themes), site
  scripts/                       verify-slice skeleton, record-usage, wake, hold-wait, stall-check,
                                 next-ready, status, protected-diff, redteam, new-worktree, milestone-push,
                                 run-logged-check, summarize-check; runtimes/codex/* (dispatch, hook shim,
                                 session guard, rules, sync)
  templates/                     state files, brief, contract, retro, proposal, demo, settings.json,
                                 .worktreeinclude, AGENTS fragment, START page, project config
  method/                        the process, generic (section 1 of this analysis, expanded)
  rationale/                     the eight findings, lessons, sources
  tests/                         schema tests, parser tests, hook red-team corpus, dashboard model tests,
                                 an end-to-end "adopt a fixture repo, run T0, render" test
```

The project adapter is one file in the adopting repository, `<state-dir>/config.yaml` (name open): paths, branches, tier steps, policy values, lists (section 2.3). Hooks and scripts read it; nothing else is hard-coded.

### 3.4 Versioning and content

- Semantic versions; the stamp travels into every installed file. `CHANGELOG.md` entries name the component, as the library does.
- English. No hostnames, bucket names, cluster contexts, model prices or people. The Assessment Lab appears only as "the first project" in the rationale, with its numbers rounded.
- The red-team corpus for protected files and the hook contract tests are the package's own gate; the T0 of the package is "schemas validate, hooks pass the corpus, the fixture repo adopts and renders".


## 4. How a person uses it: scenarios and interaction points

The method's premise is that the human is interrupted only for acts a machine may not perform. Every other touch is asynchronous and optional. The interaction surface is therefore small and should be designed deliberately; here it is, as scenarios first and as a table of touchpoints after.

### 4.1 Scenarios

**S1. Adopt the package in a project (once).** The owner opens the project and says "set this project up with the delivery process" (or runs the adopt skill). The skill reads what exists (language, test runner, `AGENTS.md`, `Makefile`, CI), asks the remaining questions in one message with guesses pre-filled (integration branch, tier commands, protected paths, state directory), writes the state files from templates, the project adapter configuration, the hooks wiring, the agent profiles, the `AGENTS.md` fragment and the dashboard configuration, and runs the harness self-test (the red-team corpus against the protected-file gate, a dry T0, a dashboard render). Output: a report of what was created and the fields still marked `TODO`. Nothing else happens; no slice starts.

**S2. Kickoff (one session).** Owner and coordinator together: scope in, scope out, the human-only list extended for this product, the increments and their exit demos, the acceptance scenarios as `FEATURES.json` rows with their checks, the first contracts, the budget share, the model routing, the kickoff decisions recorded in `OWNER-DECISIONS.md`. The owner answers questions in this session only; after it, the coordinator runs alone. Output: a populated backlog, a `STATE.md` with increment 0 `started`, the first briefs ready.

**S3. Unattended run (days to weeks).** The coordinator dispatches, reviews, merges, demos and retrospects. The owner's involvement is reading: the dashboard (refreshed every 30 seconds locally, published every 15 minutes), the hourly status file, the notification on four events. A typical owner day is zero actions.

**S4. A human-only act appears.** A row lands in `NEEDS-HUMAN.md` with the exact ask ("place the key at `path`; the agent verifies presence, never reads it"), a notification fires, and the dashboard shows it under "Needs you". The owner performs the act whenever convenient and marks the row done (or tells the coordinator). Work that depended on it was parked as `blocked_on_human`; everything else continued.

**S5. A default the owner dislikes.** An A2 default is applied and announced with a 48-hour veto window. The owner writes a veto note in `OWNER-DECISIONS.md` (or says it in chat, and the coordinator records it). Only the affected slices reopen.

**S6. Budget hold.** Usage reaches the dispatch hold: the hook refuses new dispatches; at the stop line implementers commit what passes and return `HOLD`; the coordinator starts the hold timer and ends its turn. The owner sees a hold banner on the dashboard and keeps the reserved share of the window for their own work. After the reset the coordinator wakes and continues without anyone's help.

**S7. Stop, restart, recover.** The owner creates the `STOP` file (or closes the app); every hook refuses edits and dispatches. To resume: delete the file, open a session, paste the resume prompt from the start page (or run the resume skill). The coordinator reads the recovery file, the state and the progress tail, restarts the background timers, re-dispatches slices whose branch is ahead of their recorded state. A context compaction follows the same path.

**S8. Increment close.** The demo runner produces the demo artifact, the efficiency reviewer writes at most three proposals, the coordinator runs the retrospective, adopts at most three changes with metrics and sunsets, notifies the owner with two links. The owner may read the demo and the retro; reading is optional.

**S9. A process change.** Any agent repeating a manual step appends a `FRICTION:` line. The efficiency review turns friction into proposals; the retrospective adopts or rejects each, logged forever. A change that touches the human-only list, the holds, the scope or the binding documents is not adopted by the machine; it goes to `NEEDS-HUMAN.md` as a decision. Changes to the package itself (a hook, a schema, a script) are made upstream in the package repository and reinstalled, never patched in the project (the upstream-first rule your skills library already enforces with provenance stamps and a drift check).

**S10. A small project or a solo developer.** Not every project needs a coordinator and three writers. A "lite" profile keeps the state files, the tiers, the brief shape, the kill switch and the dashboard, and runs one session that is both coordinator and implementer with the Stop hook as the only gate. The package should ship both profiles; Eva would start lite.

**S11. Second runtime.** The same project run under Codex: the agent profiles are rendered to the runtime's format by the sync script, hooks go through the shim, roles are set by the launcher, the parity check runs in T0. The owner's interface is unchanged: the same files, the same dashboard.

**S12. Update the package in a project.** "Bring the delivery process up to date": the drift check compares installed copies with the library by version stamp, replaces stale ones wholesale, refuses to touch hand-modified ones, and reports new configuration fields the project must fill. This is the exact procedure the skills library README already specifies for skills; the package extends it to hooks, scripts and templates.

### 4.2 Touchpoints

| Touchpoint | Artifact or channel | Who starts it | When | What the person does |
|---|---|---|---|---|
| Adoption | adopt skill, its report | owner | once per project | confirms pre-filled answers, fills `TODO`s |
| Kickoff | one chat session, `OWNER-DECISIONS.md`, `NEEDS-HUMAN.md`, `BACKLOG.md`, `FEATURES.json` | owner | once per run | decides scope, increments, human-only list, budget share |
| Human-only ask | `NEEDS-HUMAN.md` row, notification, dashboard "Needs you" | coordinator | when a slice needs it | performs the act, marks done |
| Default and veto | `OWNER-DECISIONS.md` row, dashboard clock | coordinator | at increment start and as needed | nothing, or a veto within the window |
| Budget | hold banner, status line | hooks and timers | at thresholds | nothing; keeps the reserved share |
| Stop and resume | `STOP` file, resume prompt or skill | owner | rarely | creates or deletes the file, pastes the prompt |
| Progress reading | dashboard, `STATUS.md` | scripts | every 30 s, hourly | reads, optionally |
| Increment close | demo artifact, retrospective, notification | coordinator | per increment | reads, optionally |
| Process change | `FRICTION:` lines, proposals log, retrospective | any agent, efficiency reviewer | per increment | reads; decides the items escalated to the human-only inbox |
| Package update | drift check, update skill | owner | when the package releases | confirms replacements, fills new fields |

Three design consequences for the package:

1. **Chat is for kickoff and exceptions.** Every other interaction has a file and a notification. The package should make the files good: schemas, a parser library, a dashboard that renders them, a status script that summarizes them.
2. **The owner needs two skills, not twenty.** `adopt` and `resume` cover S1, S7 and S12; everything else is the coordinator's job. Owner-facing commands beyond that (`status`, `veto`, `done`) are conveniences over file edits and can come later.
3. **The notification set is fixed and small.** New human item, increment close, kill-switch stop, budget hold. The dashboard carries everything else.

## 5. The dashboard: from one project's page to a generator

### 5.1 What exists

`scripts/dev/dashboard.py` is 1,490 lines in one file with an 824-line `main()` holding about twenty closures. It reads twelve inputs (the state files, the metrics, git, the briefs, two legacy plan files, `CONTINUE.md` prose, agent usage events) with its own regex parsers, computes progress credit per slice state, and writes one self-contained HTML page of 237 KB: inline CSS, six lines of vanilla JavaScript, no CDN, no fonts, no SVG, a 30-second meta refresh, light and dark tokens, and `<details>` folds whose open state survives the refresh through localStorage. A loop script re-renders every 30 seconds and publishes every 15 minutes to an S3 bucket behind basic auth; an hourly launchd job re-renders through `status.py`.

What makes it good, concretely, and what the generic version must keep:

- **One file, no runtime dependencies.** Opens from disk, from a bucket, from a mail attachment. Survives a dead network.
- **Design tokens, not ad hoc colours.** Six surface tokens and six status kinds (`ok`, `work`, `warn`, `bad`, `idle`, `ready`) as foreground and background pairs; dark mode by redefining tokens. System font stack, 14 px body, 12 px monospace, uppercase 13 px section labels.
- **A small component vocabulary used everywhere.** Tile (label, big value, unit), chip (pill with a kind), stepper (six dots for a slice's life), segmented bar (flex-weighted segments with an inner fill), timeline (Gantt rows on a percent axis with adaptive ticks), feature list (✓ ⏸ ○ rows), fold (`<details>` with a one-line summary), two-column footer.
- **Detail on demand.** Everything secondary is a tooltip or a collapsed fold; the page reads as a summary first.
- **Honest unknowns.** `UNKNOWN`, `PARTIAL` and `BOUNDED` are rendered states, never silently zero.
- **Live signals.** Pulsing on work in progress, an idle chip on a stalled slice, holds as banners, "could start now: N".

What blocks reuse, from the code reading:

- No split between data and rendering: parsing, computing and HTML live in one function, so nothing is testable without monkeypatching ten module globals, and the tests assert HTML fragments.
- Hard-coded project: paths, "Assessment Lab", UTC+3, the v1 commit range, the "increment 3 and up, not 9xx" proof rule, the slice-id regexes (three different ones), BACKLOG prose patterns, the stall-check import.
- Vocabulary drift: five slice states present in `STATE.md` have no stage, kind or credit, so those slices render as idle with zero progress.
- Side effects inside rendering: caches and history are written, git is shelled out about six ways, `next-ready.py` and `stall-check.py` are executed per render, and the output is not written atomically.
- Three table parsers, two key-value parsers and three timestamp parsers across `dashboard.py`, `status.py` and `next-ready.py`.
- Dead code and dead CSS (five unused helpers, a computed sparkline never inserted, a dozen unused classes), the legacy process-v1 block (a third of the file), and a disable flag (`.run/dashboard-disabled.json`) that nothing reads.
- Single-page assumptions: one output path, one published object, global fold ids, 183 KB on one line.

The older generator in `outputs/assessment-mvp-execution/build-progress-dashboard.py` already had the right shape for the next version: snapshot the inputs, compute one payload, validate invariants and refuse to publish on inconsistency, inject the JSON into an editable template, render client-side, write atomically. It also had a left navigation with five pages, search, filters and print styles. The two generations should merge.

### 5.2 The generic design

Three stages with a file between each, so every stage is testable alone and replaceable alone.

```text
collect  →  snapshot.json  →  compute  →  model.json  →  render  →  site/
(adapters)                   (metrics)                  (templates, components)
```

**Collect.** One adapter per source, each returning typed records. v1 adapters: the state files of this method (`STATE.md`, `FEATURES.json`, `BACKLOG.md`, `NEEDS-HUMAN.md`, `OWNER-DECISIONS.md`, `PROGRESS.md` tail, `metrics/*.jsonl`), git (head, merges, commits per day), agent usage events, a `kanban-md` board (your skills library already defines that format), and a `generic-json` adapter for a project that writes its own snapshot. That last one is what makes the dashboard usable "for any kind of project at any stage": a project with no process at all writes a JSON file by hand or from CI and gets the page.

**Snapshot schema (the entities the current page already implies).**

| Entity | Fields |
|---|---|
| project | name, root, time zone, head, generated at |
| phase (increment, milestone, sprint, release) | id, title, state, started, exit criterion, retro link |
| unit of work (slice, task, ticket) | id, phase, title, state, owner, branch, head, timestamps per state, rounds, messages, dependencies hard and soft, touches, tags |
| check (feature row, scenario, acceptance criterion) | id, phase, unit, title, command, passes, evidence, blocked on |
| run (tier run, CI job) | at, tier, unit, head, result, seconds, failed steps, log |
| decision | id, class, question, default, veto by, status |
| human item | id, phase, act, unblocks, urgency, added, done |
| hold | reason, owner, resume when, since |
| usage reading | at, event, runtime, windows[] {label, percent, resets at}, extra usage |
| agent event | runtime, session, turn, unit, role, start, end, tokens in, cached, out |
| event (progress point, log entry) | at, kind, text |

**Compute.** Pure functions from snapshot to model: progress credit from a configurable state → credit table, cycle times, headroom against thresholds, readiness (what could start now), stalls (last activity per unit), per-phase roll-ups, forecasts only when calibrated, otherwise `UNKNOWN`. This is where `status.py`, `next-ready.py` and `stall-check.py` collapse into one library that each script and the dashboard call.

**Render.** A component library (the eight components above) over the token theme, page templates, and a site builder that writes one self-contained HTML file per page plus `model.json` next to them, atomically. Pages share the same inline CSS so each stays a single file. Tabs inside a page render client-side from the embedded model, which is the pattern the older generator used; that keeps offline viewing and gives the multi-page, multi-tab version you want without a server.

**Configuration** (`dashboard.yaml` in the project): title, time zone, which adapters, the state vocabulary (state → stage, kind, credit), which pages and sections, the publish target (local path, S3, GitHub Pages, scp), refresh interval. The Assessment Lab page becomes one configuration of the generic builder; the first regression test is that it renders the same information it does today.

**Pages for the second version**, each a file: Overview (today's tiles and holds), Phases (today's increments with timelines and cards), Checks (the scenario and feature tables with filters and search), Flow (cycle times, tier durations, review rounds, reverts over time), People and agents (usage, tokens, writer capacity, stalls), Decisions and asks (owner decisions with veto clocks, human items), Log (progress entries, friction notes), Process (the component table, proposals and their status). Navigation and print styles from the older template; search and filters client-side.

### 5.3 Rules the generator must keep

- A number the data cannot support is `UNKNOWN`; a partial coverage is `PARTIAL`; never a silent zero.
- The page is one file with no network dependencies; dark mode through tokens; reduced motion respected.
- Rendering never writes anywhere but the output directory; history and caches are the collect stage's job.
- The build refuses to publish when the model fails its invariants (weights sum, every state known, every referenced unit exists), as the older generator did.
- Tests assert the model, and the page's structure (parsed HTML), not substrings.

### 5.4 Steps

1. Extract the parser library and the snapshot schema from the three scripts; make `status.py`, `next-ready.py` and `stall-check.py` use it (this also fixes the stall-check crash).
2. Split `dashboard.py` into collect, compute and render; move the process-v1 block into an Assessment Lab adapter or delete it; load the vocabulary and paths from configuration. Same page, same look.
3. Add the `generic-json` and `kanban-md` adapters and a second configuration to prove it on another project (Eva).
4. Second version: site builder, pages, tabs, search, print; merge in the older template's navigation.

## 6. Delivering it into Claude Code and Codex

### 6.1 What a Claude Code plugin is (verified against the live documentation on 2026-10-12)

- **Anatomy.** `.claude-plugin/plugin.json` is the only file under `.claude-plugin/`; `name` is its only required field (kebab-case; names starting with `claude-`, `anthropic-` or `cc-plugin-` are refused). Auto-discovered at the plugin root: `skills/<name>/SKILL.md`, `agents/*.md` (recursive, subfolders add name segments), `commands/*.md` (legacy), `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `output-styles/`, `themes/`, `workflows/*.js`, `evals/`, and `bin/`, whose executables are on the Bash tool's `PATH` while the plugin is enabled. A root `CLAUDE.md` is not loaded. Variables: `${CLAUDE_PLUGIN_ROOT}` (the install directory, which changes on update), `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`, survives updates), `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SKILL_DIR}`, `${user_config.KEY}`.
- **Namespacing.** `skills/review/SKILL.md` in plugin `x` is `/x:review`; `agents/reviewer.md` is `x:reviewer`; an MCP server `db` is `plugin:x:db`. Hooks carry no prefix, and a handler present in both the project settings and the plugin runs twice.
- **Hooks.** Thirty-odd events, among them `SessionStart` (startup, resume, clear, compact, fork), `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStart` and `SubagentStop` (matched on the agent type), `Stop`, `PreCompact`, `WorktreeCreate`, `WorktreeRemove`, `TaskCompleted`, `FileChanged`, `Setup` (`claude --init-only`). Handler types: command, http, mcp_tool, prompt, agent. Exit 2 blocks with stderr as the reason; JSON on exit 0 controls `permissionDecision` (allow, deny, ask, defer; a hook allow never bypasses a settings deny), `updatedInput`, `additionalContext` (10,000 characters per field at `SessionStart`), and `decision: block` for `Stop` and `SubagentStop`. Hooks receive `agent_id` and `agent_type` on stdin when they run inside a subagent. **Plugin hooks run inside subagents; subagent frontmatter hooks are ignored for plugin agents.** Interactive sessions withhold all project hooks until the folder trust dialog is accepted; `-p` trusts the folder.
- **Agents from a plugin.** Supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation: worktree`, `color`. Ignored: `hooks`, `permissionMode`, `mcpServers`, `initialPrompt`. Plugin agents have the lowest priority after managed, `--agents`, project and user agents. There is no path-scoped tool syntax in an agent; path limits come from `permissions.deny` rules in settings or from a `PreToolUse` hook.
- **Skills.** Frontmatter: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork` (runs the body as a subagent prompt with no conversation history), `agent`, `background`, `hooks`, `paths`. Bodies may bundle `scripts/`, `reference.md`, `examples.md`; `!`cmd`` output is inlined before the skill is sent; bundled scripts are pre-approved with `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)`.
- **Marketplaces and install.** `.claude-plugin/marketplace.json` with `name`, `owner.name`, `plugins[]`; a plugin `source` is a relative path or `{"source": "github", "repo", "ref", "sha"}`, `url`, `git-subdir` (url plus path), `npm`, `archive`, or `command`. Commands: `/plugin marketplace add <owner/repo | url | path>`, `/plugin install <p>@<mkt>`, `claude plugin validate --strict <path>`, `claude plugin install|update|list|details`, `/reload-plugins`; local development with `claude --plugin-dir <path>`. Scopes write `enabledPlugins` to user, project (`.claude/settings.json`, committed) or local settings; a project can also commit `extraKnownMarketplaces` so a teammate's session registers the marketplace after the trust dialog. A plugin whose source is another repository is not auto-installed from project settings; each teammate runs `claude plugin install <p>@<mkt> --scope project` once. Auto-update is off for non-official marketplaces unless `autoUpdate` is set on the entry; pin versions and bump on release.
- **What a plugin cannot do.** Write into the project at install time (installs land read-only and versioned under `~/.claude/plugins/cache/`); ship `CLAUDE.md`, `.claude/rules/*.md`, permission rules or `defaultMode` (a plugin `settings.json` applies only `agent` and `subagentStatusLine`). The documented per-project plugin setting is `.claude/<plugin>.local.md` with YAML frontmatter, gitignored. Context injection is a `SessionStart` hook's output.
- **Instructions files.** `.claude/rules/**/*.md` exist, loaded at launch or, with a `paths:` frontmatter, when a matching file is touched. Claude Code reads `AGENTS.md` natively when no `CLAUDE.md` exists; `CLAUDE.md` containing `@AGENTS.md` works in every session, so the library's pattern stands.
- **Evals.** `claude plugin eval` runs `evals/<case>/prompt.md` cases with graders (regex, tool_used, tool_order, file_exists, llm, baseline) in an isolated home, optionally with and without the plugin, and writes `aggregate-result.json` and a self-contained HTML report. It is the right home for the package's behaviour tests ("does `adopt` write every template and nothing else", "does `resume` re-dispatch a slice whose branch is ahead").

### 6.2 Where each artifact goes

| Artifact | Mechanism | Reason |
|---|---|---|
| Agent profiles (implementer, reviewer, named-risk, contract author, efficiency reviewer, explorer) | plugin `agents/`, with `tools`, `model`, `effort`, `maxTurns`, `isolation: worktree`, `memory` only | versioned, namespaced, updated by the plugin. **Their frontmatter hooks today (implementer stop and guard, contract write guard, retros write guard) will be ignored as plugin agents and must move to the next row** |
| Role enforcement (T0 gate on implementer stop; implementer, contract author and efficiency reviewer write guards) | plugin `hooks/hooks.json`: `SubagentStop` matched on the agent type for the T0 gate; `PreToolUse` on `Bash\|Edit\|Write\|MultiEdit` reading `agent_type` from stdin and applying the role's rules | plugin hooks run inside subagents and are the only enforcement a plugin can ship; `permissionMode: plan` on the explorer profiles is likewise replaced by `tools` allowlists |
| Kill switch, budget guard, coordinator `Stop`, `SessionStart` context | plugin `hooks/hooks.json` | each hook exits 0 at once when the project has no configuration file, so the plugin is inert elsewhere; `SessionStart` prints one paragraph pointing at the state directory and the resume page |
| Worktree bring-up for implementers | `WorktreeCreate` hook calling the project's `init --app` | removes the "write `.slice` then run init" step from the dispatch prompt |
| Owner and coordinator skills (`adopt`, `resume`, `kickoff`, `brief`, `retro`, `update`) | plugin `skills/`, bodies bundled with `scripts/` and pre-approved through `allowed-tools`; written to the Agent Skills spec | discoverable in Claude, copyable to `.agents/skills` for Codex and Cursor; `adopt` and `update` are `disable-model-invocation: true` |
| Executable harness (tier runner, status, wake, hold, stall, ready, protected-diff, dashboard build) | **installed copies** in the project, stamped with source and version; the same binaries also exposed through the plugin's `bin/` for sessions | launchd, cron, Codex, CI and a human in a terminal must run them with Claude closed; `${CLAUDE_PLUGIN_ROOT}` exists only inside a Claude hook, and the cache path changes on every update |
| Python library and dashboard package | installed copy in v1; a `pipx`-installable package with the project pinning its version in v2 | the copy needs no packaging and matches the library's update procedure |
| State-file templates, brief and contract templates, `START.md`, project configuration, `.claude/rules/<name>.md` with the rules for every agent | written by `adopt`, stamped; the rules file replaces the long block in `CLAUDE.md` | plugins cannot scaffold or ship rules |
| `settings.json` fragment (permissions allow and deny, subagent model, spawn depth, cache TTL, auto-continue, worktree base, `extraKnownMarketplaces`, `enabledPlugins`) | merged into the project's `.claude/settings.json` by `adopt`, with a diff shown first; hooks are **not** copied there, to avoid double execution | plugins cannot ship settings |
| `AGENTS.md` block, `CLAUDE.md` as `@AGENTS.md` | inserted by `adopt` | the library's always-on pattern; Claude also reads `AGENTS.md` natively when no `CLAUDE.md` exists |
| Behaviour tests | plugin `evals/` | run in CI on each release with `claude plugin eval`; `claude plugin validate --strict` as the lint |
| Codex layer | see 6.3 | |

### 6.3 Codex: verified from the Codex source, not yet from its documentation

- Codex reads `AGENTS.md` (and `AGENTS.override.md`), never `CLAUDE.md`; skills from `.agents/skills`, `~/.agents/skills` and `.codex/skills` with `name` and `description` as the only required frontmatter; hooks from `hooks.json` in `~/.codex` or `<project>/.codex`, inline in `config.toml`, or from a plugin's `hooks/hooks.json`, with the same `{"hooks": {Event: [{matcher, hooks}]}}` shape and `permissionDecision` deny on `PreToolUse`. Events in common with Claude: `PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `PostCompact`.
- Codex has plugins: it looks for `.codex-plugin/plugin.json` and falls back to **`.claude-plugin/plugin.json`**; default components are `skills/`, `.mcp.json` and `hooks/hooks.json`; plugin hooks receive `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility; marketplaces are `.agents/plugins/marketplace.json`; enabling is `[plugins."name@marketplace"]` in `config.toml`. Its manifest has no `agents` key, so subagents stay as generated `.codex/agents/*.toml`, which is what `sync-runtime.py` already produces.
- Consequence: one package can plausibly serve both runtimes from one repository (skills, hooks, MCP shared; agents duplicated by generation). This is untested end to end, so v1 keeps the copy-install path for Codex that already works here, and the package's second milestone tries the shared-plugin path with the parity check as the gate.

### 6.4 Alternatives weighed

| Mechanism | Strength | Weakness | Verdict |
|---|---|---|---|
| Template repository or cookiecutter | one command to start | no update path; every project forks | no; the `adopt` skill is the same idea with stamps and a drift check |
| Git submodule or subtree for the scripts | updates by pull | agents and hooks struggle with submodule paths; subtrees make merge noise; nothing for agents or skills | no |
| Copy-install with provenance (your library's pattern) | works in every runtime, offline, in CI; proven update procedure | needs the `update` skill to stay in sync | yes, for the executable harness and templates |
| Claude Code plugin | discovery, namespacing, versioned agents, skills and hooks, hooks that run inside subagents, `bin/` on the session PATH, evals, one-line install, local dev mode | cannot scaffold, ship settings, rules or permissions; agent frontmatter hooks ignored | yes, for the Claude layer |
| MCP server over the state files (read rows, flip rows, record usage, serve the dashboard model) | runtime-neutral API; live dashboard data; Codex parity for state edits | one more process; the files already are the API | later; natural once the parser library exists |
| `pipx` Python package | one install per machine, version pinned per project | packaging work; offline bootstrap | v2 for the library and the dashboard |

### 6.5 What the user types

Claude Code, in a project:

```text
/plugin marketplace add glotyuids/engineering-skills
/plugin install slicewright@engineering-skills
/slicewright:adopt
```

Codex, same project, from a clone of the package:

```bash
./scripts/install.sh /path/to/project --tools codex
```

Package development: `claude --plugin-dir slicewright` in a test project; `claude plugin validate --strict .` and `claude plugin eval` as the release gate; `/reload-plugins` after an edit.

## 7. Applying it to Eva

Eva today: a Go module with `make check` as the gate (fmt, build, vet, lint, race tests, methodology lint, mutants), a doc discipline of numbered decisions and questions (`docs/decisions.md`, 290 KB), frozen research rounds, a `docs/README.md` "Current" table that carries status as long prose rows, 28 agent worktrees under `.claude/worktrees` (so worktree-isolated subagents are already in use), and the skills library installed with project deltas. There is no `.claude/settings.json`, no hooks, no feature list with pass flags, no budget guard.

What adoption adds, mapped to Eva's own words:

| Method artifact | Eva instance |
|---|---|
| Integration branch | the current default branch; slice branches `slice/<n>` |
| `FEATURES.json` rows | the work packages and exit criteria of `docs/plans/product-evolution-plan.md` §16 (V1 to V6) and the SD test scenarios, each with a `make`-based or `go test`-based check and a must-run test name |
| Increments | V-milestones; each exit demo becomes a `demo` target |
| T0 | `make fmt build vet lint` plus unit tests of changed packages, under two minutes (today `make check` is one block and includes mutants, which belongs in T2 or T3) |
| T1 | `make test` with the race detector on affected packages, `emf-lint`, the slice's scenario test |
| T2 | `make check` in full, in the background, revert on red |
| T3 | `make check` plus `host-test`, at milestones |
| Decisions | class B lines in `STATE.md` keep pointing at `D-NNN`; A2 defaults get a `D-` entry with the veto date; `Q-` entries that block a slice become `NEEDS-HUMAN.md` rows |
| Human-only list | plus Eva's own: paid model runs above the recorded budget, real channel activation, private data, signing methodologies |
| Material boundaries | authority and grants (Cedar), state and recovery, privacy journal, model operations ledger |
| Protected files | `docs/decisions.md`, `docs/architecture.md`, `methodologies/`, `api/emf/core-catalogue.yaml` |
| Dashboard | the Current table of `docs/README.md` becomes a rendered page; the decision and question counts, the budget ledger (cumulative dollar cap) and the gate results get tiles |

Order: run `adopt` with the lite profile (one session, hooks, tiers, state files, dashboard); convert one plan into `FEATURES.json` rows and run a single slice end to end; then enable the full profile with a coordinator and two writers once the tiers are stable. Eva's decision discipline stays as it is; the method only adds the pass-flag ledger and the gates around it.

## 8. The name

"AI-DLC" is taken. AWS announced the "AI-Driven Development Life Cycle (AI-DLC)" in 2025 as its own methodology (inception, construction, operations; "bolts" instead of sprints; "units of work" instead of epics) and ships it as an open-source workflow for Kiro and other agents ([AWS announcement](https://www.aboutamazon.in/news/aws/aws-launches-new-ai-methodology-devsphere), [methodology summary](https://ttpsc.com/en/blog/how-aws-ai-dlc-defines-an-ai-native-methodology/), [overview](https://jellyfish.co/library/ai-driven-development-lifecycle/)); Harness also markets an "AI-DLC" product page. Using the same acronym for a public repository would read as a derivative of theirs and would be hard to find.

Candidates, all free of that collision as far as a search shows:

| Name | For | Against |
|---|---|---|
| `slicewright` | names the central idea (vertical slices behind frozen contracts, built by one writer); distinctive; verbs well ("slicewright adopt") | invented word |
| `autodlc` | says "autonomous development life cycle", keeps your SSDLC analogy | generic; close to the AWS term |
| `harness-dlc` | "harness" is the word the method and Anthropic's research already use for this layer | Harness is a company in the same space |
| `coordinated-delivery` | descriptive, boring, searchable | long for a command |

Recommendation: `slicewright` for the repository, plugin and command; "an autonomous development life cycle for AI coding agents" as the one-line description so the SSDLC analogy survives in the tagline. If you prefer the analogy in the name itself, `autodlc` is the fallback.

## 9. Open decisions for the owner

| Decision | Options | Recommendation |
|---|---|---|
| Name | `slicewright`, `autodlc`, `harness-dlc`, `coordinated-delivery`, plus the ten checked candidates the owner asked for on 2026-10-12 (`sliceworks`, `sliceyard`, `tiergate`, `passflag`, `keelwright`, `briefwright`, `slicecraft`, `coxswain`, `millwright`, `pawl`) | `sliceworks` or `slicewright` (section 8); pending |
| Where it lives | own repository at `<name>`; a pack inside `engineering-skills` | own repository, registered in the library's marketplace (section 3.2). **Agreed by the owner 2026-10-12.** |
| Public or private | public under Apache-2.0 like the library; private | public, with the library's content policy; the Assessment Lab stays out of it except as rounded figures in the rationale. **Agreed by the owner 2026-10-12.** |
| First consumer | Eva lite profile; a fixture repository only | both: the fixture repository is the package's own test, Eva is the first real adoption |
| Dashboard scope of v1 | same page as today, generic; multi-page at once | same page first, multi-page as the second version (section 5.4). **Agreed by the owner 2026-10-12.** |
| Codex in v1 | ship the Codex layer in the first release; defer | ship it, since the shim, the dispatch script and the parity check already exist and Eva may run under either |
| Python as the harness language | Python 3 standard library only (today's scripts); add dependencies (schema validation, templating) | standard library plus one optional dependency for JSON Schema validation; no web framework |

## 10. Plan

Each phase ends with something that runs. Estimates are coordinator sessions of a few hours; implementation itself can run through the method it describes, with the package repository as the project.

| Phase | Delivers | Done when |
|---|---|---|
| 0. Skeleton | repository, plugin manifest, layout of section 3.3, `method/` as the sanitized process, `rationale/` as the findings and lessons, this analysis as the first design note | `claude --plugin-dir` loads it, `claude plugin validate --strict` passes, the skills appear |
| 1. Schemas and library | JSON Schemas for the state files, the snapshot and the telemetry rows; the parser library; `status.py`, `next-ready.py`, `stall-check.py` ported onto it; the templates with the project configuration file | the library parses this repository's live state files; the two bugs of section 2.5 cannot recur |
| 2. Harness | the eight hooks reading configuration; `verify-slice` skeleton with pluggable tier steps; must-run for Go, pytest and Playwright; budget, wake, hold, protected-diff and red team; Codex layer | the fixture repository adopts, runs T0 and T1, passes the red-team corpus |
| 3. Adopt and resume skills | `adopt` (S1), `resume` (S7), `update` (S12), `kickoff` (S2) with the prompts as templates | a blank repository becomes a running lite project in one session |
| 4. Dashboard v1 | collect, compute, render split; the Assessment Lab page as one configuration; `generic-json` and `kanban-md` adapters | this repository's dashboard renders from the package with the same information; Eva renders a page from its plans |
| 5. Eva | adoption in lite profile, one slice end to end, then full profile | a slice merges through the tiers with the dashboard showing it |
| 6. Dashboard v2 | site builder, pages, tabs, search, print, publish adapters | the eight pages of section 5.2 render offline from one model |
| 7. Back-port | this repository switches to the package (plugin plus installed templates), its local scripts deleted | T0 to T3 here run through the package; drift check clean |

Phase 7 is what makes the extraction real: until this repository consumes the package, there are two copies and they will fork, which is the failure the skills library was created to end.

## 11. Risks

- **Over-generalizing before a second consumer exists.** The guard is Eva plus the fixture repository in the first release; a third project decides what else becomes configurable.
- **The hooks are POSIX sh with jq and macOS `date`.** Portability to Linux is cheap now and expensive later; do it in phase 2.
- **The plugin cache is read-only and versioned per install.** Scripts that the project must run from its own tree (tiers, hooks referenced by `settings.json`) are installed copies with stamps, never references into the cache; the drift check covers them.
- **Public exposure.** Every file goes through the library's `private-patterns` check; the method is public, the instance never is.
- **Two runtimes drift.** The parity check in T0 and a generated, never hand-edited, runtime configuration are the only known cure; keep both.

## 12. Sources

Claude Code documentation read on 2026-10-12: [plugins](https://code.claude.com/docs/en/plugins.md), [components](https://code.claude.com/docs/en/plugins/components.md), [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), [creating plugins](https://code.claude.com/docs/en/plugins/create.md), [install](https://code.claude.com/docs/en/plugins/install.md), [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md), [loading](https://code.claude.com/docs/en/plugins/loading.md), [CLI reference](https://code.claude.com/docs/en/plugins/cli-reference.md), [security](https://code.claude.com/docs/en/plugins/security.md), [publish](https://code.claude.com/docs/en/plugins/publish.md), [organizations](https://code.claude.com/docs/en/plugins/org.md), [plugin evals](https://code.claude.com/docs/en/plugin-evals.md), [hooks](https://code.claude.com/docs/en/hooks.md), [skills](https://code.claude.com/docs/en/skills.md), [subagents](https://code.claude.com/docs/en/sub-agents.md), [memory](https://code.claude.com/docs/en/memory.md), [permissions](https://code.claude.com/docs/en/permissions.md), [settings reference](https://code.claude.com/docs/en/settings-reference.md). Local cross-checks: the official `plugin-dev` reference plugin and the installed `ralph-loop`, `hookify`, `claude-security` and `example-plugin` plugins under `~/.claude/plugins/`.

Codex, read from source on the default branch of [openai/codex](https://github.com/openai/codex) (`codex-rs/core/config.schema.json`, `core-plugins/src/manifest.rs` and `loader.rs`, `hooks/src/engine/discovery.rs`, `hooks/src/events/pre_tool_use.rs`, `hooks/src/schema.rs`, `config/src/hook_config.rs`, `ext/skills/src/host_roots.rs`, `skills/src/parser.rs`, `core/src/agents_md.rs`, `docs/config.md`, `docs/skills.md`) and [openai/plugins](https://github.com/openai/plugins). The developers.openai.com pages were unreachable at the time, so Codex facts are source-verified only.

Naming: [AWS announcement of AI-DLC](https://www.aboutamazon.in/news/aws/aws-launches-new-ai-methodology-devsphere), [methodology summary](https://ttpsc.com/en/blog/how-aws-ai-dlc-defines-an-ai-native-methodology/), [overview](https://jellyfish.co/library/ai-driven-development-lifecycle/), [AI-DLC on the agentic-ai standards index](https://agentic-ai.readthedocs.io/en/latest/Standards/aidlc/), [Harness product page using the term](https://www.harness.io/products/use-cases/ai-dlc).

Process rationale in this repository: `docs/plans/assessment-lab-multiagent-research-report-2026-10-09.md` and its four companions, `docs/assessment-lab/PROCESS.md`, `START.md`, `RUNTIMES.md`, the three retrospectives and `retros/PROPOSALS.md`.
