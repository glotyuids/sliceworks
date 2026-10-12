# 0. The life cycle: product, milestones, phases

A **product** moves through named **milestones**. A milestone is a goal with a promise, success metrics, exit criteria and gate families; "MVP" is the usual name of the first milestone with external users, "Pilot", "Launch" and "v2" are others. A milestone has nine **phases**; the Build phase is where increments, slices and ledger rows live (chapters 1 to 12). Phases overlap: Operate and Learn of one milestone run while the next milestone is in Discover and Decide; a hotfix runs Build, Accept and Release in a day while Design of the next milestone is being written.

```text
Product
  └── Milestone (name, promise, success metrics, exit criteria, gate families)
        ├── Spark      one page: who, what pain, why now, the riskiest assumptions
        ├── Discover   research rounds; claims with sources and verification verdicts
        ├── Decide     the decisions ledger: D entries with classes, Q entries with defaults and due dates
        ├── Design     invariants, architecture, specs with versions, user scenarios, gate families, threat models
        ├── Plan       increments with exit demos, rows per scenario, contracts, increment planning, re-planning
        ├── Build      increments → slices → rows            (chapters 1 to 12)
        ├── Accept     demo, gate rows, the acceptance packet, two verdicts kept apart
        ├── Release    the release checklist, environments, approvals, the one push, post-release verification
        ├── Operate    probes, incidents, the hotfix lane, production review digests
        └── Learn      evaluations under caps, metrics against the promise, the feedback register
              └── feeds the next milestone's Discover
```

## Milestone states

| State | Entry condition | Owner of the transition |
|---|---|---|
| `planned` | named in `MILESTONES.md` with a promise | owner (an A2 default if the owner does not name it) |
| `discovering` | `SPARK.md` or the previous milestone's feedback register names the questions; a round is open | coordinator |
| `deciding` | every round closed; open questions carry defaults and due dates | coordinator |
| `designing` | no open question blocks the acceptance contract; the design review passed | coordinator |
| `planning` | scenarios, gate families and success metrics recorded; increments derived | coordinator |
| `building` | increment 0 `started` (chapter 3) | coordinator |
| `accepting` | engineering-complete: every row of the milestone passes or is `blocked_on_human`; the acceptance packet written | coordinator |
| `releasing` | the owner accepted; a release slice is open | coordinator, acts by the owner |
| `operating` | the release is verified in its environment; probes run | scripts and coordinator |
| `closed` | success metrics measured and recorded, whatever they say; feedback register handed to the next milestone | coordinator, owner informed |

The autonomous run of chapters 1 to 12 ends at `accepting`, not at "the MVP". `refocus` (chapter 14) may return a milestone from `building` to `planning` with a recorded decision.

## Row kinds

One ledger, `FEATURES.json`, one row shape, a `kind` per row. Every kind has an executable check; a row without a check is not a row.

| Kind | Phase | What the check proves |
|---|---|---|
| `scenario` | Build | the named end-to-end test ran and passed (default kind) |
| `criterion` | Build | a slice criterion's test ran and passed |
| `claim` | Discover | the claim in a round's register has a source and a verification verdict |
| `experiment` | Discover | a measurement is recorded for the riskiest assumption the row names |
| `decision` | Decide | the D entry is `decided`, `defaulted` or `superseded`, and no Q it depends on is past due |
| `spec` | Design | the spec validates against its schema, a frozen spec has no `TODO`, every decision link resolves |
| `gate` | Accept | the gate's human act has a done date in the inbox, or a decision waived it |
| `release` | Release | the checklist step ran (a script) or was performed (a human act with a done date) |
| `probe` | Operate | the probe command exits 0 against the named environment |
| `eval` | Learn | a verdict file exists for the suite, within its token and money budget, at or above its threshold |

## Autonomy by phase

| Phase | Who leads | Owner involvement | Human-only acts |
|---|---|---|---|
| Spark | owner | writes the page | none |
| Discover | researchers, read-only | reads rounds | none |
| Decide | owner and coordinator | highest: answers what only they can, or lets defaults apply inside veto windows | scope, money, legal, real data |
| Design | architect and reviewers | vetoes inside windows; approves the acceptance contract once | approvals that bind real people |
| Plan | coordinator | reads the milestone plan | none |
| Build | coordinator and implementers | reads the dashboard | credentials for shared environments |
| Accept | coordinator prepares, owner accepts | reads one packet, signs the gate rows | acceptance |
| Release | coordinator prepares, owner performs | performs the deploy acts with prepared commands | deploy beyond the isolated environment, DNS, secrets |
| Operate | scripts and coordinator | notified on incidents | real-data access, external communications |
| Learn | evaluators under caps | reads verdicts | raising a money cap |

## Project kinds and profiles

The same phases serve different projects; the profile in the configuration chooses the phases and the row kinds that matter. A **product** uses all ten. A **library or tool** has rows of kind `criterion` and `eval`, a Release that is a version tag and a registry entry, an Operate that is issue triage. A **research-first project** lives in Discover, Decide and Design for months with claims, decisions and specs as its rows and a thin Build. An **infrastructure project** is mostly Release and Operate. The dashboard is the same for all because the ledger is.

## Entry

How a project enters the life cycle, how what it already has is reused, and how a request typed in chat becomes rows, is chapter 17.

## Two budgets

The usage window (chapter 8) bounds tokens. **Money** is a second dimension: every paid run (a provider call outside the plan, a cloud resource, an evaluation on a metered model) is recorded in `metrics/money.jsonl` against an authorization the owner granted as a decision, and the money guard refuses a paid command past the cap. The first run never spent money autonomously; a product that evaluates on real models does, and does so only under a cap.
