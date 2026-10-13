---
name: design
description: Write or update the sliceworks design artifacts from decisions and rounds - INVARIANTS.md, ARCHITECTURE.md with decision citations, specs with format versions, SCENARIOS.json, MILESTONES.md with gate families and success metrics, threat models for material surfaces, the INDEX.md Current table - then run the design review before Plan. Use when the user says "design this", "write the architecture", "define the milestone", "list the user scenarios", "threat model", or when a milestone enters designing.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.6.0
---

# Design: the acceptance contract and the design surfaces

Method: `method/14-design-and-plan.md`. Templates: `ARCHITECTURE.md`, `specs-README.md`, `SCENARIOS.example.json`, `MILESTONES.md`, `threat-model.md`, `INDEX.md`, `INVARIANTS.md`. Run as the `architect` agent or in a session that writes only `SW_DESIGN_SURFACES`. After a pivot, `refocus` runs this skill for every surface its audit marked `amend`; each change cites the pivot D.

1. **Invariants.** From the decisions and rounds, one line each in `INVARIANTS.md`; the binding documents at the end. An invariant changes only through a D entry.
2. **Architecture.** `ARCHITECTURE.md` edited in place; every changed section cites the D that caused it; proposals are labelled `proposed (D-n)`.
3. **Specs.** Formats and protocols under `specs/` with version numbers in names; front matter `status: draft | frozen`. Where the project uses Spec Kit, `constitution` and `specify` produce these; register each as a `spec` row with the spec lint as its check.
4. **Scenarios.** `SCENARIOS.json`: user journey steps with stage, roles, segments, milestone and the rows that prove them; every scenario of the current milestone proves at least one row before the milestone is accepting.
5. **Milestones.** `MILESTONES.md`: the current milestone's promise, success metrics, exit criteria, increments with exit demos, gate families with rows and owners. The owner approves the section once (a D entry).
6. **Threat models.** One page per material surface in `SW_MATERIAL_SURFACES`; name the tests that prove each invariant, or "none yet" as an open H.
7. **Index.** Every living document in `INDEX.md` with status (`current`, or `archived (D-n)` with the file moved to `archive/<date>-<name>`) and last-reviewed date. After a pivot, refresh the date of every row the refocus audit marked `keep` and add the archive rows; the lint fails a current row not reviewed since the pivot.
8. **Design review.** When the library's `review-plan` skill is installed, run it as written: evidence from the repository and the rounds, the four dimensions (correctness and logic, architecture and principles, missing parts, ambiguity), a ranked findings table, open questions batched at the end. When it is absent, a read-only reviewer runs a reduced review under the same four headings. Fix H and M before Plan. Decision records follow the library's `documentation-standards` where installed.
