# Scripts (phase 2)

The verification harness and the runtime adapters land here in phase 2 of the plan (`docs/design/2026-10-12-extraction-analysis.md`, section 10):

- `verify-slice.sh`: the tier runner skeleton (slice id resolution, one log per run, `run()` that records every step, `RESULT=`/`LOG=`/`FAILED:`, a `tiers.jsonl` row, a slot queue for a shared resource, self-pinning to the harness commit) with the tiers' steps read from the project configuration.
- `must-run/`: "a named test must actually run and pass" for Go, pytest and Playwright.
- `record-usage.sh`, `wake.sh`, `hold-wait.sh`, `stall-check.py`, `stale-procs.py`, `next-ready.py`, `status.py`: budget and flow telemetry, on the `harness` library. Requirements carried over from the first run's fixes of 2026-10-12: timestamps are parsed by one helper that accepts ISO 8601 and integer epochs (`hooks/lib.sh` `sw_epoch` already does; port its tests from `test_budget_ts.py`); `wake.sh` never discards a detector's stderr and prints `STALL-CHECK-ERROR` on a non-zero exit; slice ids match `slice-\d+[A-Za-z0-9-]*$` everywhere (port `test_stall_check.py`).
- `protected-diff.sh`, `redteam-protected.sh`: protected files enforced at the diff, and the corpus that proves it.
- `new-worktree.sh`, `pin-t2.sh`, `milestone-push.sh`, `install-schedules.sh` (launchd and cron adapters).
- `install.sh`, `check-drift.sh`: copy-install with provenance stamps for runtimes without plugins.
- `runtimes/codex/`: dispatch, hook shim, session guard, execution rules, status, agent sync (parity check).

Already here: `release.sh` (bump, test, validate, commit, tag, push, marketplace entry), `collect.py` (method chapter 19: completion read from pids, tier logs, branch heads and committed handoffs for every open allocation; tests in `tests/test_collect.py`), `install.sh` (copy-install of the skills, and of the agents for Claude Code without the plugin, into a project or the user's directories; never symlinks, never overwrites without `--force`), `survey.py` (method chapter 17: the project inventory and the `--next` dispatcher, no writes; tests in `tests/test_survey.py`), `check-design-docs.py` (method chapter 14 lints: an ARCHITECTURE.md change cites a decision, INDEX.md rows within the review limit, frozen specs without TODO; a T0 step in projects with living design documents; tests in `tests/test_check_design_docs.py`), and, generic as copied from the first run: `run_logged_check.py`, `summarize_check.py`, `automation_errors.py`, and under `runtimes/codex/` the hook shim, the execution-policy rules and the status lister.
