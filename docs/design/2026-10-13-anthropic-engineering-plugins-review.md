# Review: Anthropic's engineering and architecture skills against ours

Design note, 2026-10-13. Question from the owner: the official catalog has an Anthropic "Engineering" plugin with architecture and system-design skills; would prompting with those be better than the package's own `design` skill and `architect` agent?

## What exists

| Source | Author, tier | What it is | Size |
|---|---|---|---|
| **Engineering** plugin (`anthropics/knowledge-work-plugins`, `engineering/`) | Anthropic, catalog | ten skills for knowledge work with optional connectors: `architecture` (an ADR with an options table and trade-offs), `system-design` (a five-step framework), `deploy-checklist`, `testing-strategy`, `tech-debt`, `incident-response`, `code-review`, `debug`, `documentation`, `standup` | 32 to 158 lines each; `system-design` 42, `architecture` 85 |
| `feature-dev:code-architect` (official marketplace) | Anthropic | a Sonnet agent that reads the codebase's patterns, picks one architecture decisively and returns an implementation blueprint: files, components, data flow, build sequence | one agent |
| `core/architect`, `core/planner`, `process/review-plan` (`engineering-skills`) | the owner's library | an Opus architect with principles (clean architecture, coarse services, light DDD), a six-step procedure (requirements, bounded contexts and data ownership, one to three options with migration and operational impact, recommendation, contracts with versioning and idempotency, cross-cutting concerns) and an ADR hand-off; a phased file-level planner; a 381-line plan review with evidence first, four dimensions, ranking and batched questions | mature |
| `sliceworks` `architect` and `design` | this package | the artifacts and their rules: invariants, `ARCHITECTURE.md` citing decisions, specs with versions, `SCENARIOS.json`, `MILESTONES.md` with gate families, threat models that name their tests, the Current index; role-guarded writes; design review before Plan; runs on the top-tier model | artifact and rule oriented |
| `system-design-skills` (catalog, community) | Proyecto 26 | twenty-two divide-and-conquer skills (capacity, caching, consistency, resilience, messaging, sharding) with an orchestrator | deep, scale-focused |

## Verdict

**Not as replacements.** The Engineering plugin's `architecture` and `system-design` skills are short, generic frameworks written for knowledge work across tools, with connector placeholders and no project grounding, no artifacts, no checks and no enforcement. Prompting with them alone would produce a well-shaped document that nothing reads afterwards. Our `architect` is the opposite: it knows exactly which files to write, what each must cite and prove, and the guard stops it writing anything else; but it says little about **how to think** from requirements to components and trade-offs. The library's `core/architect` sits in between: it has the reasoning procedure, in Go-and-Kubernetes wording.

**The gap is real and it is ours.** Our design step lacks a reasoning framework and an options comparison. The decisions ledger records a decision, its default and its consequences, never the options that lost and why. That is the one thing the Engineering `architecture` skill does well.

**Model.** Skills run on the caller's model, so borrowing their structure into our `architect` keeps the design on the top-tier model. `feature-dev:code-architect` is pinned to Sonnet and makes one decisive choice without options; it is a fit for slice-level implementation blueprints at `plan-increment`, not for milestone design.

## What to take, and where

| From | Into | Change |
|---|---|---|
| Engineering `system-design` steps 1 to 5; library `core/architect` steps 1 to 6 | `agents/architect.md` | a design procedure before the artifacts: functional and non-functional requirements and constraints; bounded contexts, data ownership and contracts touched; one to three options with a dimension table; one recommendation; deep dive (data model, interfaces, caching, queues, errors and retries, idempotency, versioning); scale and reliability (load estimate, failover, observability, rollback); explicit trade-offs and "what we would revisit as the system grows" |
| Engineering `architecture` ADR options table | `templates/DECISIONS.md`, method chapter 13 | an **Options considered** table on class B and A2 entries: option, complexity, cost, scalability, team familiarity, operational impact, migration risk; losing options stay in the entry |
| Engineering `deploy-checklist` | `templates/release.md`, chapter 15 | two rows: on-call or the owner notified before the deploy; canary where the environment offers one |
| Engineering `testing-strategy` | `templates/brief.md` section 6 | one line: test type per component (unit for logic, integration for adapters, contract for consumers, end-to-end for the scenario) |
| Engineering `tech-debt` scoring | `FEEDBACK.md`, the retrospective | a priority column: (impact + risk) × (6 − effort), for candidates that are debt rather than features |
| `feature-dev:code-architect` | method chapter 18, `plan-increment` | an optional binding: when the plugin is enabled, the surface map for a slice may come from it; the fallback is our explorers |
| `system-design-skills` | method chapter 18 | an optional deep-dive pack the architect may consult for scale-heavy designs; not needed at the current projects' scale |

Not taken: the Engineering `code-review` skill, which reviews security, performance and style together. The method restricts the reviewer to correctness and stated requirements on purpose (rationale finding 4) and gives security its own named-risk review; widening the reviewer is what the research warns against.

## Cost of taking it

About forty lines in the architect profile, one table in the decisions template, five rows across three templates, two table rows in chapter 18. No new dependency: the structures are borrowed with attribution in `rationale/sources.md`; the two optional bindings follow the chapter 18 rule, present or absent with a stated fallback.
