# 18. The skills library

`sliceworks` owns the life cycle: phases, ledgers, gates, coordination, the dashboard. It does not say how to write Go, run a migration, build a pipeline or respond to an incident. Those are **skills**, and the owner's library of them is [`engineering-skills`](https://github.com/sudo-sane/engineering-skills): packs of Agent Skills installed into a project by copy with a provenance stamp, upstream-first, tool-agnostic. The two are bound in both directions.

## The library lists the life cycle

`sliceworks` is a plugin entry in the library's marketplace, installed from its own repository:

```text
/plugin marketplace add sudo-sane/engineering-skills
/plugin install sliceworks@engineering-skills
```

## The life cycle knows the library

The survey (chapter 17) reads every installed `SKILL.md` whose front matter names the library as its source, groups them by pack with their versions, recommends the packs the project's stack and phases call for, and reports, per phase, which library skills the phase skills would use and which are absent. The `adopt` skill offers the recommended packs through the library's own install procedure (the agent-followable section of its README, or `scripts/install.sh`); it never copies skills itself.

| Phase | Library skill | What it supplies when present | When absent |
|---|---|---|---|
| adopt | `bootstrap-project` | the always-on layer: `AGENTS.md` with the project-context block, `CLAUDE.md` as `@AGENTS.md`, the docs tree, the secrets contract | `adopt` writes a minimal `AGENTS.md` block and leaves the rest as `TODO` |
| design | `review-plan` | the four-dimension design review before Plan | the coordinator runs a reduced review with the same four headings |
| design, release, operate | `documentation-standards` | ADR, runbook and postmortem templates and rules | the project's own formats; the method's templates for the rest |
| plan | `kanban-md` | the file-based board, when the project tracks work there | `BACKLOG.md` alone |
| build | `git-workflow`, `integration-testing`, `security-guidelines` | commit and branch discipline, how integration tests are organised, the security practice the reviewers check against | the briefs state the project's rules directly |
| release | `cicd-build-deploy`, `secrets-management`, the infra pack | how the pipeline builds and deploys, how secrets are referenced, the vendor layer | the release checklist carries `TODO` rows for the steps no skill covers; a human performs them with the coordinator's prepared commands |
| operate | `incident-response` | the incident procedure the `fix` slice follows and the postmortem shape | the method's `INCIDENTS.md` and a one-page postmortem |
| learn | `deslop` | the clean-up pass on model-written text and code before it is kept | none |
| any | the language and database packs (`go`, `database`, `frontend`, `llm`) | the conventions the implementers follow and the review agents the reviewers can delegate to | the project's own conventions; the method's reviewers alone |

Two optional bindings reach outside the library, to plugins from the official catalog, under the same rule:

| Phase | Plugin | What it supplies when enabled | When absent |
|---|---|---|---|
| plan-increment | `feature-dev` (Anthropic): the `code-architect` agent | a codebase-grounded implementation blueprint for one slice: patterns found, files to touch, data flow, build sequence | the method's explorers write the surface map |
| design | `system-design-skills` (community): the divide-and-conquer pack | deep-dive recipes for capacity, caching, consistency, resilience and messaging when a milestone is scale-heavy | the architect's own procedure (chapter 14) |

The Anthropic knowledge-work "Engineering" plugin's `architecture` and `system-design` skills were reviewed on 2026-10-13 (`docs/design/2026-10-13-anthropic-engineering-plugins-review.md`); their structure is folded into the architect's procedure and the decisions' options table rather than bound, because they carry no project grounding of their own.

Two rules keep the binding cheap. A phase skill names the library skill and the section it relies on; it never restates its content. When a library skill is absent the phase still runs, with the fallback in the last column, and the survey keeps recommending the pack until it is installed or the owner records a decision not to.

## Other runtimes

Codex reads `.agents/skills` and its own marketplace file, `.agents/plugins/marketplace.json`, which this repository carries so that the package installs as a Codex plugin; `scripts/install.sh` copies the skills for any runtime without plugins, never by symlink, keeping the provenance stamps. The hooks and agent profiles are Claude Code mechanisms; the dual profile (chapter 10) carries their Codex counterparts.

## Versions

The survey records each installed skill's version. The library's own drift check (`scripts/check-drift.sh`) and its update procedure keep the copies current; the `update` skill of this package runs them when the project has a clone of the library and reports the result next to its own.
