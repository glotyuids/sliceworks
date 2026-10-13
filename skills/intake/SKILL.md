---
name: intake
description: Take a request typed in chat through the sliceworks intake pipeline - capture it as a feedback candidate, run business analysis and system analysis as read-only agents, adapt the user scenarios and ledger rows with named checks, record the questions and the placement decision, and place it into the current increment, the next one, or a later milestone, or route an idea to a round and a defect to a fix slice. Use when the user says "add a feature", "I want X", "can we also", "change how Y works", "users asked for", "new requirement", or describes something the product should do.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Intake: from a request to rows

Method: `method/17-entry-and-intake.md`. Template: `intake.md`. Output: `<state-dir>/intake/<id>.md` and the ledger changes.

1. **Capture.** Append the request verbatim to `FEEDBACK.md` with an id and the date; create `intake/<id>.md`. Classify the shape: *idea* (open a round with `discover` and stop here), *defect* (open a `fix` slice through `operate` and stop here), *question* (answer, no artifact), *feature or change* (continue).
2. **Business analysis.** Spawn the `business-analyst` agent with the request, `SPARK.md`, `MILESTONES.md`, `SCENARIOS.json` and `FEEDBACK.md`. Paste its output into the file.
3. **System analysis.** Spawn the `system-analyst` agent with the request, `ARCHITECTURE.md`, `INVARIANTS.md`, the contracts and the explorer's map of the touched area. Paste its output.
4. **Scenario adaptation.** New or changed `SCENARIOS.json` entries; new rows in `FEATURES.json` with `kind`, `milestone`, `increment` and a check that names a test (`TODO: <TestName>` until the slice writes it); superseded rows marked by id, never deleted.
5. **Decisions.** `Q` entries for the open questions with recommended defaults and due dates; a `D` entry for the placement when it changes the plan (class A2 or B).
6. **Placement.** Current increment if one slice, no contract change and a free writer slot; next increment if it needs a contract or a seam (`contract-author` first); a later milestone otherwise, with the scenarios recorded now. Write the brief with `brief` when the slice can start; call `refocus` when the request invalidates the current plan.
7. **Report** in one message: the placement and its reason, the scenarios and rows added, the questions that need the owner. Nothing else.
