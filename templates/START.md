# Starting and resuming the coordinator

<!-- sliceworks 0.7.0 -->

## Before the first start (owner, once)

1. Answer the kickoff questions (the `kickoff` skill); the answers land in OWNER-DECISIONS.md and NEEDS-HUMAN.md.
2. Keep the host open and the machine awake. Any shared service the init command needs (a database container) must be running.
3. Install the scheduled jobs (hourly status, nightly full suite) with the package's schedule script.

## Start or restart

Open a session at the repository root in the `auto` permission mode with the project's coordinator model, effort high. Run `/sliceworks:resume`, or paste:

```text
Resume the coordinator. Read .run/coordinator-session.md if it exists, then <state-dir>/STATE.md, the tail of PROGRESS.md and NEEDS-HUMAN.md. If <state-dir>/STOP exists, stop. Record a usage reading. At or above the dispatch hold do not dispatch; at or above the stop line stop every running implementer, write the hold into STATE.md, start the hold timer in the background and end the turn; when it wakes you, record a fresh reading and continue. Otherwise re-dispatch every slice recorded active or repair whose implementer is not running, keep one ready brief per writer, record a reading before every dispatch and at every merge, keep the dashboard loop and the wake timer running in the background and act on their STALL, STALE and READY lines. Goal: every FEATURES.json row of the current increment is passes:true or blocked_on_human, the demo passed, and retros/increment-<n>.md exists; when the milestone's last increment closes, write the acceptance packet and move the milestone to accepting.
```

The same prompt is the recovery prompt after a restart, a usage-limit pause or a kill-switch stop (remove STOP first).

## What the owner sees

The dashboard (`<state-dir>/dashboard.html` unless `SW_DASHBOARD_OUT` says otherwise; it reloads itself every 30 seconds) and STATUS.md; NEEDS-HUMAN.md when an item is added; OWNER-DECISIONS.md as defaults are applied; the demo artifact and the retrospective at each increment close. To stop everything: create `<state-dir>/STOP`. To resume: delete it and run `/sliceworks:resume`.

## Background processes

| Process | When | Purpose |
|---|---|---|
| dashboard loop | always | `sh scripts/sliceworks/dashboard-loop.sh 30`: rebuilds the dashboard every 30 s and publishes it through `SW_DASHBOARD_PUBLISH_CMD` if set, no model turn |
| wake timer | while any slice is active | wakes the coordinator every 15 min with STALL, STALE and READY lines; the coordinator records a reading and restarts it |
| hold timer | during a budget hold | sleeps until the window resets, then wakes the coordinator |
| T2 after a merge | after each merge | integration check of the merged head in a clean worktree |
