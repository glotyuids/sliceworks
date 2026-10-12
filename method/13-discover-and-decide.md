# 13. Discover and Decide

## Spark

`SPARK.md`, one page, written by the owner (or by the coordinator from the owner's words and confirmed): who the product is for, what pain it removes, why now, what the first milestone promises, and the **riskiest assumptions**, the things that must be true for the milestone to be worth building. Each riskiest assumption becomes either a research question or an experiment row. Prevents: a backlog built on an unstated premise.

## Rounds

A **round** is one research-and-verification run with a fixed set of questions, frozen on close. `rounds/<n>-<slug>/`:

| File | Content |
|---|---|
| `questions.md` | the questions this round must answer, each with the decision or design artifact it serves |
| `sources.md` | everything read, with dates and what each source was used for |
| `register.md` | one claim per row: id `C-<n>-<k>`, the claim, source, confidence, verification verdict (`verified`, `refuted`, `unverified`), verified by what |
| `design.md` | the synthesis: what the claims mean for the product, the open questions handed to Decide |
| `.closed` | present once the round is frozen; the role guard then refuses writes to the directory |

A round is never appended to: a new question opens a new round. Researchers are read-only subagents, one question each, writing their claims into the register through the coordinator or an `architect` session. Prevents: analyses nobody can audit; the same question researched twice; a design resting on an unverified claim.

The **register lint** is the check of every `claim` row: every claim has a source and a verdict, and no verdict predates its source. An **experiment** row records a measurable outcome and a budget; its check is the recorded measurement. A two-day experiment beats building the milestone to learn the same thing.

## The decisions ledger

One file, `DECISIONS.md`, across all phases. Two entry kinds.

```text
### D-<n> · <title>
- <date> · <origin: round <n> | review <slice> | owner answer | retrospective <n>> · class <A1 | A2 | M | B> · **<status>** · refines D-<m> · supersedes D-<k> · veto by <date>
- Decision: <one paragraph>
- Default applied and consequence of reversing: <for A2 and B>
- Consequences to verify: <what must be checked before this is treated as settled>

### Q-<n> · <question>
- <date> · <origin> · owner <who answers> · due <date> · default at due: <what applies if nobody answers> · **open | closed by D-<n>**
```

Classes: **A1** human-only (never defaulted; the Q stays open and the dependent rows are `blocked_on_human`); **A2** product default applied by the coordinator with a 48-hour veto window; **M** method and process; **B** technical, one-day veto. Statuses: `open`, `recommended`, `defaulted`, `decided`, `vetoed`, `superseded`. A decision is revisited only through a new decision that supersedes it. Long-form technical decisions may also have an architecture decision record in the project's format; the D entry links to it.

`OWNER-DECISIONS.md` is no longer a file the coordinator writes: it is the dashboard's rendering of A2 entries with open veto clocks. Prevents: silent defaults; the same question answered twice differently; a decision without its evidence; a ready slice blocked on a question nobody owns.

The **decision check** of a `decision` row: the D entry's status is `decided`, `defaulted` or `superseded`, and no Q it depends on is past due without its default applied.

**Precedence** when documents disagree (from the Current index, chapter 14): active decisions, then accepted specs, then the architecture. A proposed decision cannot override an active one.

## The owner's part

Decide is where the owner's time goes. The coordinator keeps it small: every Q arrives with a researched recommendation and a default; the owner answers only A1 questions and vetoes; everything else applies itself at the due date and is announced. The kickoff session of a project that starts with a known scope is this phase run in one sitting.
