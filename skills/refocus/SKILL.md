---
name: refocus
description: Re-plan a sliceworks milestone mid-flight when evidence contradicts the current increments - pause active slices at a safe point, record the pivot as a decision with its evidence, re-derive increments and scenarios, re-map rows without changing ids, mark paused slices with their resume increment, and leave a re-plan marker on the timeline. Use when the user says "refocus", "re-plan", "pivot", "the scope changed", "pause these slices", or when a Learn or Discover output invalidates the plan.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Refocus: re-plan a milestone

Method: `method/14-design-and-plan.md`.

1. **Pause.** Each active slice stops at a safe point: a candidate if T1 is green, otherwise a commit with a dated `PROGRESS.md` note. Set the slice `paused` with the reason.
2. **Record.** A `D` entry of class A2 or M: what evidence changed the plan (round, metric, incident, owner statement), what is dropped, what is added, what moves to a later milestone. Veto window applies.
3. **Re-derive.** Update `MILESTONES.md` (increments and exit demos), `SCENARIOS.json` (milestone and increment of each scenario), `BACKLOG.md` (slices per increment). Row ids never change; thinned rows keep their ids and reference the D entry.
4. **Re-map.** Every `FEATURES.json` row gets its new `milestone` and `increment`; paused slices get the increment they resume in; contracts that no longer hold are `retired` or `amended` with a `CONTRACT` message to pinned slices.
5. **Mark.** Write the re-plan into `STATE.md` history and `PROGRESS.md`; the dashboard shows the marker on the timeline.
6. **Resume.** Run `plan-increment` for the first re-planned increment; re-dispatch paused slices that survive from their branches.
