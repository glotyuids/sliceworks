---
name: adopt
description: Set up a repository to run under the sliceworks development life cycle - write the state files, the project configuration, the invariants file, the start page, the agent-guide block and the settings fragment from the package templates, then run the harness self-test. Use when the user says "adopt sliceworks", "set this project up with the delivery process", "run this project with slices and a coordinator", "install the autonomous development process here", or asks to bootstrap the coordinator, implementers, tiers, kill switch or feature ledger in a repository. Run it once per repository; re-running never overwrites an existing file.
disable-model-invocation: true
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.6.0
---

# Adopt sliceworks in a project

Templates live in `${CLAUDE_PLUGIN_ROOT}/templates/`; the method in `${CLAUDE_PLUGIN_ROOT}/method/`. This skill writes files into the user's project through ordinary tools, with the user's permission; a plugin cannot do it at install time. It never overwrites a file that exists; it reports what it skipped.

## Phase 1, read the ground truth (no questions yet)

- Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/survey.py" --root "$PWD" --markdown`; it detects the stack, the commands, the process systems in use (Spec Kit, OpenSpec, decision records, plans), the agent configuration and the phase coverage, and writes nothing. Pre-fill every answer below from it.
- Repository root, default branch, remotes. Existing `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/agents/`, `.agents/skills/`, `Makefile`, CI configuration.
- Language and test runner from manifest files (`go.mod`, `package.json`, `pyproject.toml`, `Cargo.toml`). The commands that build, lint and test today (`Makefile` targets, `package.json` scripts, CI steps).
- Whether the project already has a state directory, a backlog, decision records or a kanban board; whether it uses worktrees under `.claude/worktrees`.
- Whether `jq`, `git` and `python3` are available.

## Phase 2, ask once

One message, every remaining question, with your best guess pre-filled so the user confirms rather than composes:

1. Profile: `lite` (one session), `full` (coordinator plus implementers), `dual` (plus Codex); and the phases this project runs (a library drops Spark and Operate; a research project may start with Discover, Decide and Design only).
2. State directory (default `docs/process`), outputs directory (default `outputs`).
3. Integration branch and slice branch prefix.
4. Tier commands: T0 (under two minutes), T1, T2, T3, from what you found; the init command and its smoke check; the demo command if any.
5. Protected files beyond the defaults; contract surfaces; material-boundary surfaces; the project's invariants (one line each).
6. Budget: the run's share of the provider window (default 85%), hold and stop percentages (defaults 80, 85, 90, 100).
7. Additions to the human-only list.

## Phase 3, write

From `${CLAUDE_PLUGIN_ROOT}/templates/`, substituting the answers:

- `.sliceworks/config.env` from `config.env` (every `SW_*` the hooks read).
- `<state-dir>/`: `FEATURES.json` (an empty array, or rows the user already has), `STATE.md`, `BACKLOG.md`, `PROGRESS.md`, `DECISIONS.md`, `NEEDS-HUMAN.md`, `INVARIANTS.md`, `MILESTONES.md`, `SCENARIOS.json` (empty array), `SPARK.md`, `ARCHITECTURE.md`, `INDEX.md`, `RUNTIME.md`, `INCIDENTS.md`, `FEEDBACK.md`, `START.md`, `contracts/`, `slices/`, `plans/`, `rounds/`, `threat-models/`, `accept/`, `allocations/`, `handoffs/`, `intake/`, `refocus/`, `archive/`, `retros/PROPOSALS.md`, `retros/proposals/`, `metrics/` (empty `usage.jsonl`, `tiers.jsonl`, `money.jsonl`), `demos/`, `evals/README.md`, `specs/README.md` at the repository root. Omit the files of phases the profile does not run (`SW_PHASES`).
- `.claude/rules/sliceworks.md` from `rules.md` (the rules for every agent), and the `AGENTS.fragment.md` block appended to `AGENTS.md` (create `AGENTS.md` and a `CLAUDE.md` containing `@AGENTS.md` if neither exists).
- `.claude/settings.json`: merge the keys of `settings.fragment.json` (permissions, environment, subagent model, cache TTL, auto-continue, worktree base, `enabledPlugins`). Show the diff before writing. Do not copy any hook into settings: the plugin's hooks already run, and a duplicate runs twice.
- `.gitignore`: add `<state-dir>/STATUS.md`, `<state-dir>/STOP`, `.run/`, `<outputs>/`.
- `.worktreeinclude` with the files a new worktree must inherit (environment files), if the profile is `full` or `dual`.
- For `dual`: `.codex/config.toml` from `codex-config.toml`, and `.agents/skills/` copies of this plugin's skills.

Stamp every written file with `# sliceworks <version>` (or the `metadata` block in Markdown front matter) so the `update` skill can detect drift.

## Phase 3b, the skills library

The survey lists the skills installed from `engineering-skills` and the packs it recommends for this stack and these phases (method chapter 18). Offer the recommended packs in the Phase 2 message; install the confirmed ones through the library's own procedure (its README's agent-followable section, or `scripts/install.sh` from a clone), never by copying skills yourself. Record declined packs as a `D` entry so the survey stops recommending them.

## Phase 3c, a running project

If the survey found linked worktrees, live pid files or result-less logs, register each as an allocation record (worker unknown, state `stopped` or `open` as the evidence says) before anything is dispatched; run the collector and confirm it reports no `UNREGISTERED` lines. A project adopted mid-run with an empty registry would otherwise read as idle.

## Phase 4, self-test

- Run the project's T0 command once; it must print `RESULT=` and `LOG=` lines or the user must accept that the tier runner (phase 2 of the package) is not installed yet.
- Create `<state-dir>/STOP`, attempt a trivial edit through the Edit tool, confirm the kill switch denies it, remove the file.
- If the harness scripts are installed, run the protected-files red team.

## Report

List: files written, files skipped because they existed, `TODO` fields left in `config.env` and `INVARIANTS.md`, the settings diff applied. Then run the `survey` skill to write `SURVEY.md`, and `start`, which picks the next phase (`prepare` when the survey found specifications, decisions or plans to import; `discover` for an idea; `kickoff` is the composed path for a known scope).
