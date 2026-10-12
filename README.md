# sliceworks

An autonomous development life cycle for AI coding agents.

One long-lived **coordinator** session keeps a small set of state files, freezes contracts, writes
briefs and dispatches **slice implementers** into their own git worktrees. Deterministic
**verification tiers** decide what is reviewable; an independent **reviewer** reads the diff in a
fresh context; the coordinator merges by SHA and runs the merge gate in the background. Progress
is the number of acceptance scenarios passing end to end on the integration branch, recorded in a
**feature ledger** with pass flags and evidence. A human is interrupted only for acts a machine may
not perform: credentials, money, legal and consent, real personal data, irreversible actions outside
the repository. Everything else runs under recorded, vetoable defaults, within **budget holds** on
the provider's usage window, behind a **kill switch** file.

The method was extracted from a real run and is written so that every component names the failure
it prevents; a component whose failure stops occurring is removed at the retrospective.

## Install

Claude Code, in the project you want to run this way:

```text
/plugin marketplace add glotyuids/engineering-skills
/plugin install sliceworks@engineering-skills
/sliceworks:adopt
```

Local development or a checkout of this repository:

```bash
claude --plugin-dir /path/to/sliceworks
```

Codex and other runtimes read the same `AGENTS.md` and the skills under `.agents/skills`; the
`adopt` skill (or `scripts/install.sh`, phase 2) copies them. See `method/10-autonomous-operation.md`
and `scripts/runtimes/codex/`.

## The life cycle

A product moves through named **milestones** (MVP is one name among others). Each milestone has ten phases: Spark, Discover, Decide, Design, Plan, Build, Accept, Release, Operate, Learn. Build is the autonomous run described above; the other phases have their own ledgers, checks and skills, and the owner's time concentrates in Decide, Accept and Release. One ledger holds every phase's rows, each with a `kind` that says what its check proves. See `method/00-lifecycle.md`.

## Starting

`/sliceworks:start` looks at the project and runs what is next. A blank repository is adopted; a newly adopted one is surveyed (stack, commands, the specifications, decisions, plans and boards it already has, its agent configuration); a project with existing specifications or decision records has them imported before anything is written from scratch; an idea opens a research round; scenarios without rows go to design; rows without a brief go to increment planning; a running project resumes; a finished milestone goes to acceptance. A request typed in chat ("add a feature", "users asked for") goes through `intake`: business analysis, system analysis, scenario adaptation, decisions, placement. See `method/17-entry-and-intake.md`.

## With the skills library

`sliceworks` owns the life cycle; [`engineering-skills`](https://github.com/glotyuids/engineering-skills) owns how each engineering thing is done. The survey detects which packs a project has, recommends the rest for its stack, and each phase names the library skill it calls (`review-plan` at design, `incident-response` at operate, the infra pack at release) and what happens when it is absent. See `method/18-skills-library.md`.

## Profiles

| Profile | For | What runs |
|---|---|---|
| `lite` | one developer, one session | state files, tiers, briefs, kill switch, dashboard; the session is coordinator and implementer at once; the Stop hook is the only gate |
| `full` | unattended runs | coordinator plus worktree-isolated implementers, reviewers, named-risk review, budget holds, stall and ready detection |
| `dual` | Claude Code and Codex on one project | `full` plus the generated Codex agent files, the hook shim and the parity check |

## Read

- `method/` is the process: principles, roles, lifecycles, preparation, verification, review and
  integration, communication, budget, metrics and the improvement loop, autonomous operation,
  the component table, the glossary.
- `rationale/` is why: the research findings behind the rules, the lessons from the first run,
  the sources.
- `docs/design/2026-10-12-extraction-analysis.md` is the design note this package was built from.

## Status

0.4.1: bound to the skills library, with a design procedure in the architect; the method book covers the whole life cycle and the entry sequence; the manifest, ten agents, hooks with a money guard, nineteen skills, templates and schemas validate; the survey script, the hook tests, the lint tests and the survey tests pass. The verification harness, the Python library and the dashboard generator follow (`docs/design/2026-10-12-extraction-analysis.md`, section 10; `docs/design/2026-10-12-lifecycle-coverage.md`, section 8).

## Licence

Apache-2.0.
