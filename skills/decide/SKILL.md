---
name: decide
description: Keep the sliceworks decisions ledger - turn open questions into Q entries with researched defaults and due dates, announce veto windows, apply defaults at due, record owner answers and vetoes as D entries with class and status, supersede rather than edit, and keep the precedence rule. Use when the user says "record this decision", "what is still open", "apply the defaults", "the owner answered", "veto", "decide", or when a round closes with open questions.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.4.0
---

# Decide: the decisions ledger

Method: `method/13-discover-and-decide.md`. File: `<state-dir>/DECISIONS.md` (template `DECISIONS.md`).

1. **Intake.** From a closed round's `design.md`, a review, a retrospective or an owner message, write `Q-<n>` entries: question, origin, owner, due date, the default that applies at due. Class A1 questions never get a default; the dependent rows are `blocked_on_human` and the ask goes to `NEEDS-HUMAN.md`.
2. **Recommend.** For A2, M and B questions, research the options once (an explorer or the round) and write the recommendation into the Q entry.
3. **Announce.** A2 defaults carry a 48-hour veto window, B one day. The announcement is the dashboard's owner view and the status line, never a chat message.
4. **Apply.** At the due date with no owner answer, write `D-<n>` with status `defaulted`, the default applied and the consequence of reversing; close the Q with `closed by D-<n>`.
5. **Record answers.** An owner answer becomes `D-<n>` with status `decided`; a veto becomes a D with `vetoed` that names the affected slices to reopen.
6. **Supersede, never edit.** A changed decision is a new D that `supersedes D-<m>`; the old entry's status becomes `superseded`.
7. **Check.** The decision check: no Q past due without its default applied; every D cites its origin. Register decisions that gate rows depend on as `decision` rows in `FEATURES.json`.

The kickoff of a project with a known scope is this skill run in one sitting with the owner present.
