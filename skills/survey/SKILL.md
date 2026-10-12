---
name: survey
description: Inventory a project for sliceworks - detect the stack and its commands, the process systems already in use (Spec Kit, OpenSpec, decision records, plans, architecture documents, boards, runbooks), the agent configuration (instruction files, rules, agents, skills, hooks, plugins, MCP servers, project memory), and the coverage of every phase's artifacts; write SURVEY.md with an interpretation and the sources to import. Use when the user says "survey the project", "what do we have here", "analyze this repo for the process", "inventory", or right after adopt.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.4.0
---

# Survey the project

Method: `method/17-entry-and-intake.md`. Script: `${CLAUDE_PLUGIN_ROOT}/scripts/survey.py`. Template: `SURVEY.md`.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/survey.py" --root "$PWD" --markdown` and `--json`. The script detects; it never writes.
2. Write `<state-dir>/SURVEY.md`: the generated report, then the Interpretation section from the template: what the project is in one sentence; the sources `prepare` should import, in order (Spec Kit features, OpenSpec specs and changes, decision records, plans, the architecture document, end-to-end tests, boards); the artifacts no source can seed; the commands proposed for the tiers, init, smoke and demo from the detected `Makefile` targets, package scripts and CI steps; the protected files, contract surfaces and material surfaces proposed for `.sliceworks/config.env`.
3. Report the skills-library section as the script prints it: installed packs with versions, recommended packs, and per phase which library skills are present and absent (method chapter 18). A phase whose library skills are absent still runs, with the fallback the chapter names.
4. Read the host's project memory file if the survey found one, and the instruction files (`AGENTS.md`, `CLAUDE.md`, rules): list the rules and conventions the method must respect, and any conflict with the method's rules, in the Interpretation.
5. Report in one message: the five lines of the Interpretation and the dispatcher's next step. Do not ask questions here; `adopt` and `prepare` ask, once each.
