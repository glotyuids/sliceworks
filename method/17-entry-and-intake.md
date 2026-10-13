# 17. Entry and intake

Two things happen before any phase can run: the method learns what the project already is, and the project is brought to the shape the method reads. And one thing happens throughout: someone types a request in chat. This chapter is the entry sequence, the dispatcher that picks the phase, the importers that reuse what exists, and the intake pipeline for requests.

## The entry sequence

```text
adopt  →  survey  →  prepare  →  start ──┬── discover      (an idea, nothing on file)
                                         ├── design        (scenarios or milestones missing, or no rows)
                                         ├── plan-increment (rows but no brief)
                                         ├── resume        (briefs or active slices)
                                         └── accept        (every row passes)
```

- **adopt** (chapter 0, the `adopt` skill) writes the configuration and the empty ledgers. It asks once.
- **survey** runs `scripts/survey.py`: a deterministic inventory of the project, written to `SURVEY.md` in the state directory. It detects the stack and its commands (manifests, `Makefile` targets, package scripts, CI, test files, end-to-end test names), the skills installed from the skills library and the packs to recommend (chapter 18), the process systems already in use (Spec Kit, OpenSpec, decision records and logs, plans and roadmaps, an architecture document, a kanban board, runbooks, postmortems), the agent configuration (instruction files, rules, agents, skills, hooks, plugins, MCP servers, the host's project memory, worktrees), and the coverage of every phase's artifacts. The script never writes; the skill writes the report and reads it back to the user. Prevents: adopting blind, and asking the owner what the repository already says.
- **prepare** brings the project to the method's shape **from what exists**, through importers (below), before anything is written from scratch. Every derived artifact is marked `derived from <source>` and confirmed by the owner in one message. Prevents: re-authoring specifications, decisions and scenarios that the project already has in another format.
- **start** is the dispatcher: `survey.py --next` prints the next skill and the reason, from the state of the ledgers and artifacts; the `start` skill runs it. A blank repository goes to `adopt`; an idea with nothing on file goes to `discover`; scenarios without rows go to `design`; rows without a brief go to `plan-increment`; briefs or active slices go to `resume`; a milestone whose rows all pass goes to `accept`. Prevents: starting the wrong phase, and the owner having to know the method to begin.

The sequence is idempotent. Running `start` on a project that is mid-run resumes it; running it on a project that just adopted surveys it.

## Importers

An importer reads one source format the project already has and proposes the method's artifacts. It proposes, never replaces: the owner confirms, and the source stays the project's own document.

| Source | Where found | Produces |
|---|---|---|
| README, product docs | `README.md`, `docs/` | `SPARK.md` draft; the first user scenarios |
| Spec Kit | `.specify/memory/constitution.md`; `specs/<nnn>-<name>/spec.md`, `plan.md`, `tasks.md`, `contracts/` | invariants from the constitution; scenarios and `scenario` rows from user stories and acceptance scenarios; architecture pointers from plans; slice candidates from tasks; contracts from contracts |
| OpenSpec | `openspec/project.md`; `openspec/specs/<capability>/spec.md` (requirements with Given/When/Then scenarios); `openspec/changes/<id>/` (proposal, design, tasks, spec deltas) | `SPARK.md` and architecture pointers from the project file; scenarios and rows from requirement scenarios; an increment or slice per open change; decisions from proposals; thinning from `REMOVED` deltas |
| Decision records | `docs/adr/`, `docs/decisions/`, a `decisions.md` log | `D` entries that link to the record; open questions as `Q` entries |
| Plans and roadmaps | `docs/plans/`, `ROADMAP.md` | `MILESTONES.md` sections with promises, increments and exit criteria |
| Architecture document | `ARCHITECTURE.md`, `docs/architecture.md` | the Current index entry; invariants quoted from it; material surfaces for threat models |
| Tests | end-to-end test names, acceptance test files | `criterion` rows with must-run checks; `scenario` rows where a test name encodes a scenario id |
| Board | kanban-md tasks, issue trackers | `BACKLOG.md` slice candidates; `FEEDBACK.md` candidates |
| Runbooks, postmortems | `docs/runbooks/`, `docs/postmortems/` | the Operate baseline: probes to register, incidents to record |

An importer leaves a gap list: artifacts no source could seed. Those go to `discover` or `design`, which generate them, and that is the "scenario-generating execution" of a project that had none.

## Intake: a request typed in chat

Any request from the owner (a feature, a change, a complaint, an idea) enters through one pipeline, so that nothing becomes a slice because it was said. The `intake` skill records the request first and then runs four analyses, each a bounded, read-only step whose output is a section of `intake/<id>.md`:

1. **Capture.** The request verbatim, dated, as a `FEEDBACK.md` candidate with an id. Classify by shape: idea (goes to a round), feature or change (continues), defect (opens a `fix` slice through Operate), question (answered, no artifact).
2. **Business analysis** (`business-analyst` agent): who benefits and how, which milestone promise it serves or whether it is a new promise, value and urgency in the owner's terms, the riskiest assumption, the class A questions it raises, what it would replace, and whether it is a pivot (chapter 14: it changes the milestone promise, a riskiest assumption, an invariant, or a scenario of the current milestone). Output: a recommendation to place now, later or not at all, with the reason.
3. **System analysis** (`system-analyst` agent, over an explorer's map): components and contracts touched, invariants at risk, whether it crosses a material boundary, data and numbered artifacts affected, what exists to reuse, the rough size (one slice, several, an increment).
4. **Scenario adaptation.** New or changed entries in `SCENARIOS.json`; new `scenario` or `criterion` rows with checks named as tests; rows thinned or superseded, by id; the milestone and increment each belongs to.
5. **Decisions.** The questions as `Q` entries with recommended defaults; a `D` entry for the placement when it changes the plan.
6. **Placement.** Into the current increment when it is one slice with no contract change and a free slot; into the next increment when it needs a contract or a seam; into a later milestone otherwise, with the scenarios recorded now. Then `brief` for a slice that can start. When the business analysis answers **pivot: yes**, the placement is `refocus` (chapter 14): the product is audited against the pivot decision and what the new focus contradicts is archived before anything is re-planned or briefed.

The owner sees one message: the placement and its reason, the rows and scenarios added, the questions that need them. Prevents: features entering by chat without analysis; analysis without a record; a request lost because it arrived while the coordinator was busy.

## Where the analysts fit

The two analysts are read-only roles, like the reviewer: they return structured analyses and write nothing. The coordinator (or the owner's session) turns their output into ledger changes through the ordinary skills. In the lite profile one session plays all three.
