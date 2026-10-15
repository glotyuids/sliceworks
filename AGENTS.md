# Contributing agent guide, sliceworks

You are working **on** the package. To **use** it in a project, read [README.md](README.md) instead.

## What this repository is

`sliceworks` is an autonomous development life cycle for AI coding agents, extracted from a
real multi-agent run (eight increments, about seventy merged slices). It is at once a Claude Code
plugin (`agents/`, `skills/`, `hooks/`), an Agent Skills pack (every skill is a plain `SKILL.md`),
a scaffold (`templates/`, `schemas/`, written into a project by the `adopt` skill), a Python
package (`harness/`, `dashboard/`) and a method book (`method/`, `rationale/`). Everything here
is public under Apache-2.0: no hostnames, no local paths, no personal data, no project secrets.

## Rules

- English. One canonical source per fact: the method is in `method/`, the reason in `rationale/`,
  the mechanics in `hooks/`, `templates/` and `harness/`. Do not restate one in another; link.
- A hook or script reads every project-specific value from `.sliceworks/config.env` in the
  adopting project (see `templates/config.env`). Nothing project-specific is hard-coded here.
- Every hook exits 0 immediately when the project has no `.sliceworks/config.env`, so the plugin
  is inert in a project that did not adopt it.
- Plugin agents carry no `hooks`, `permissionMode` or `mcpServers` frontmatter: Claude Code
  ignores those for plugin agents. Role enforcement lives in `hooks/hooks.json`, keyed on the
  `agent_type` field of the hook input.
- Tests are never removed or weakened to pass. `claude plugin validate --strict .` must pass.
- Versions are semantic. Write the `## <version>` section in `CHANGELOG.md` first, then run `scripts/release.sh <version> "<summary>" --marketplace <path-to-engineering-skills>`: it bumps the manifest, runs every test and the strict validator, commits, tags and pushes, and keeps the library's marketplace entry in step. Users receive it through `claude plugin update` or the marketplace's auto-update.
- Install into projects by copying with a provenance stamp (`metadata.source`,
  `metadata.version` in skills; a `# sliceworks <version>` header in scripts and templates);
  improvements flow upstream first.

## Layout

```text
.claude-plugin/plugin.json   plugin manifest (Claude Code; Codex reads it as a fallback)
.agents/plugins/marketplace.json  the Codex marketplace file: this repository lists itself as a plugin
agents/                      coordinator-facing subagent profiles
skills/                      start, adopt, survey, prepare, intake, kickoff, discover, decide, design, plan-increment, brief, collect, refocus, resume, retro, accept, release, operate, learn, update
hooks/                       hooks.json plus the hook bodies (POSIX sh, jq)
templates/                   state files and ledgers for every phase, round/, brief, contract, retro, proposal, demo, release, acceptance packet, config, settings fragment
schemas/                     JSON Schemas for the state-file rows and telemetry
method/                      the process, generic
rationale/                   why each rule exists: research findings, lessons, sources
harness/                     Python: parsers, schemas, telemetry (phase 1)
dashboard/                   Python, standard library: collect, compute, render; run as `python3 dashboard --root <repo>`, installed into projects by `scripts/install.sh --dashboard`
scripts/                     survey.py (inventory and dispatcher), collect.py (completion from artifacts), check-design-docs.py (lints), install.sh (copy-install for runtimes without plugins, and the dashboard), dashboard-loop.sh (the 30-second rebuild), release.sh (the release in one command); the verification harness and runtime adapters follow (phase 2)
tests/                       hook behaviour tests, lint tests, dashboard tests on two fixture projects (tests/fixtures/dashboard); later the schema tests, red-team corpus, fixture repository
evals/                       claude plugin eval cases
docs/design/                 dated design notes, frozen
```

## Status

0.7.0 ships the dashboard (method chapter 9: the first run's page as the package's generator, installed by `adopt`); 0.6.0 closes the gaps of the second Codex report (two-actor allocations, evidence-checked completion, messages as dispatches, failure classes, unblocks); 0.5.0 adds allocation records, handoffs and the collector (chapter 19); 0.4.0 binds the package to the `engineering-skills` library (marketplace entry there, survey detection and phase bindings here); 0.3.0 adds the entry sequence (survey, prepare, start) and the intake pipeline; 0.2.0: method, rationale, manifest, agents, hooks, skills, templates, schemas, the design-doc lint and the hook tests. The depth plan (parser library, harness scripts, dashboard) is `docs/design/2026-10-12-extraction-analysis.md` section 10; the breadth plan is `docs/design/2026-10-12-lifecycle-coverage.md` section 8. Run `sh tests/test_hooks.sh` and `python3 -m unittest discover -s tests` before a release.
