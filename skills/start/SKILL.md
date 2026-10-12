---
name: start
description: The one entry point of sliceworks - look at the project's state and run the right thing next: adopt a blank project, survey a newly adopted one, prepare from existing specs and decisions, discover from an idea, design scenarios, plan the first increment, resume the run, or accept a finished milestone. Use when the user says "start", "what's next", "continue", "let's go", "where are we", "begin development", or gives no more direction than "go".
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.3.0
---

# Start: run what is next

Method: `method/17-entry-and-intake.md`.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/survey.py" --root "$PWD" --next` (or the project's installed copy). It prints `NEXT=<skill> REASON=<why>` from the ledgers and artifacts; it writes nothing.
2. Tell the user the next step and the reason in one line.
3. Run that skill: `adopt`, `survey`, `prepare`, `discover`, `design`, `plan-increment`, `resume` or `accept`. Do not skip ahead: a project with scenarios but no rows gets `design` even if the user asked to "start development", because development starts from rows with checks.
4. When that skill finishes, run the dispatcher again and report the new next step. Stop when the next step needs the owner (an A1 question, an acceptance, a release act) or when `resume` has started the run.

If the kill switch file exists, say so and stop. If the dispatcher's reason contradicts what the user believes (for example "every row passes" on a project the user calls unfinished), show the ledger numbers and ask before acting.
