---
name: accept
description: Close a sliceworks milestone's engineering and prepare the owner's acceptance - run the demo, list the gate rows with their exact asks, assemble the acceptance packet, keep mechanism-verified and quality-accepted as separate verdicts, notify the owner, and on acceptance move the milestone to releasing or closed. Use when the user or the coordinator says "accept the milestone", "prepare acceptance", "is the MVP done", "acceptance packet", or when every row of a milestone passes or is blocked on a human.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Accept a milestone

Method: `method/15-accept-and-release.md`. Template: `acceptance-packet.md`.

1. **Engineering-complete.** Every row of the milestone passes or is `blocked_on_human`; every scenario of the milestone proves at least one row; the last increment's demo and retrospective are done.
2. **Gate rows.** One `gate` row per item of each gate family in `MILESTONES.md`, each with `human_act` pointing at a `NEEDS-HUMAN.md` row that states the exact ask and where the result must appear.
3. **Packet.** `<state-dir>/accept/<milestone>.md`: what to read, what to decide, what is parked, the two verdicts with "quality accepted" left for the owner or the named evaluator.
4. **Notify.** The acceptance packet is an inbox item and one of the five notifications. Set the milestone `accepting`.
5. **On acceptance.** Record a `D` entry (class A1, decided), close the gate rows with their done dates, move the milestone to `releasing` (or `closed` when it has no release), and start the `release` skill.
