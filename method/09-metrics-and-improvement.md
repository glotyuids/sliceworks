# 9. Metrics and the improvement loop

## Metrics

Outcome: scenarios passing on the integration branch (ledger rows with `passes: true` and evidence); merge-to-green time per slice and the full slice cycle (`STATE.md` timestamps: ready, active, candidate, review pass, merged, green); usage percent of the window.

Tax: messages per merged slice (8 or fewer); coordinator turns per merged slice (20 or fewer); documentation-only commit share (20% or less); open human-only acts older than seven days (reported, not targeted; they are the owner's). Plus idle capacity hours: time with ready slices and free writer slots.

Quality: review rounds per slice, T2 revert rate, T3 and nightly red rate, escaped defects per increment.

Hourly status, five lines, produced by a script into `STATUS.md`, and the dashboard rebuilt every 30 seconds: both read only files, so the cadence spends no tokens. A status produced by a model turn would cost a full-context request per fire; that was the single largest avoidable spend in the design this method replaced.

## Three layers of analysis

**Telemetry (scripts, no model).** Per-slice timestamps, usage deltas, message counts, review rounds, T2 reverts, tier durations, the documentation-commit share, guard denials.

**Friction notes (one line each, at the source).** Any agent that repeats a manual step, waits for something, works around a tool, or re-reads the same large file appends one line to `PROGRESS.md`: `FRICTION: <what> <how often> <cost estimate>`.

**Efficiency review (one bounded run per increment).** The coordinator spawns the efficiency reviewer with the telemetry, the friction lines, the host's usage breakdown, the proposal log and the method. It writes a dated proposal file and appends to the append-only `PROPOSALS.md`, at most three proposals in this shape:

```text
PROPOSAL EP-<increment>-<n>: <title>
Status: proposed            # retrospective sets: adopted | rejected (reason) | verified | sunset
Observed: <what the data shows, with numbers>
Cause: <why>
First ask: can the step be removed? <yes/no and why>
Change: <remove | automate | re-sequence | re-route model | change a rule>
Expected effect: <metric, direction, size>
Cost: <hours or tokens to implement>
Verify by: <metric and the increment in which it should show>
Sunset: <when to remove the change if the effect is absent>
Prior art: <earlier proposal ids on the same cause and what happened to them>
```

Order of preference, from Lean: remove the step, then automate it, then make it cheaper.

## The retrospective

At each increment end: read the outcome and tax numbers against the previous increment; read the proposals and the friction they cite; walk the component table and remove any component whose failure did not occur (security invariants excepted); adopt at most three changes, each with a metric and a sunset, each becoming a process slice with a brief; revisit the previous retrospective's adopted changes and mark them `verified` or `sunset`; write one page; notify the owner. A change touching the human-only list, the holds, the scope or the binding documents is not adopted by the machine; it goes to the inbox as a decision.

## Rules that keep the loop cheap

Once per increment or once a week, never on a heartbeat. Read-only, its cost recorded like a slice. At most three changes, none without a metric, each with a sunset. Every proposal logged with its outcome; nothing proposed twice without new data. The method grows only by replacing text; a new rule names its failure, the proposal id and the retrospective that adopted it. Three-strikes: any manual step performed three times across runs becomes a script, hook or skill at the next retrospective.
