---
name: learn
description: Learn about the product, not the process - run evaluation suites under token and money caps and record verdicts, review metrics against the milestone's success metrics, maintain the feedback register with evidence, record paid runs in the money ledger, and propose the next milestone's research questions. Use when the user says "evaluate", "run the evals", "metrics review", "what did we learn", "feedback", "did the MVP work", or at an increment or release close.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Learn

Method: `method/16-operate-and-learn.md`. Templates: `evals-README.md`, `FEEDBACK.md`.

1. **Evaluations.** For each suite: confirm the corpus pin, the threshold and the budget; confirm the authorization `D` entry and the remaining cap in `metrics/money.jsonl` before any paid run; run; write `results/<ts>/verdict.json`; append the money entry; flip the `eval` row.
2. **Metrics review.** For each success metric of the milestone: measure by script where it is a number, by a bounded reviewer where it is a judgment; record in `MILESTONES.md` "Metrics measured".
3. **Feedback.** Candidates from digests, metrics, incidents and owner notes into `FEEDBACK.md` with their evidence; no candidate becomes a row without a decision.
4. **Clean-up.** Run the library's `deslop` skill where installed on text and code the milestone keeps.
5. **Close the loop.** When the milestone's metrics are measured, move it to `closed` and hand the register to the next milestone's `discover` as its first questions.
