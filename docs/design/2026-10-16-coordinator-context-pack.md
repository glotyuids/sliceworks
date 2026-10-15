# A deterministic context for the coordinator

Dated design note, frozen. Written 2026-10-16 on the branch `codex-runtime`. Status: **decided, implementation deferred.**

Question from the owner: the coordinator's own context grows with its reasoning, and after a compaction it recovers by reading prose, some of which it wrote itself. Can recovery and growth be made deterministic, with short structured log entries, growth protection, and clear states and statuses instead of raw text? Scope: the coordinator only. What reaches a worker is the subject of [2026-10-15-context-isolation.md](2026-10-15-context-isolation.md); this note does not change it.

**Decision.** The coordinator's working context is built by a script from records, never carried in its conversation. Tools write a structured journal. A context pack, a pure function of the state files and the journal, is injected at startup, resume and compaction, with a hard cap on every section. Anything the coordinator must remember that has no other record goes into the journal through one short note command; what is not in a record does not survive a compaction. The mechanism belongs in this package, because it works with plain Claude Code and Codex; an external launcher can reuse it to start a fresh coordinator session on every wake.

## What exists today, and where it falls short

| Piece | Today | Gap |
|---|---|---|
| Allocation records | the unit of recovery ([method 19](../../method/19-allocation-and-completion.md)) | already structured; kept as is |
| `hooks/session-context.sh` | runs on `startup\|resume\|compact` and prints one paragraph naming the files to read | the coordinator then reads prose into its context, with no bound on size |
| `.run/coordinator-session.md` | what only the conversation knew, written by hand at every dispatch and merge | written by the model; it can be stale or wrong, and nothing checks it |
| `PROGRESS.md` | one dated prose paragraph per run | grows without limit; useful to people, costly as context |
| Automatic compaction | the runtime's own summary of the conversation | lossy and not reproducible; the first run resumed an obsolete task from its own history (method 19) |

## Design

### 1. A journal written by tools

`<state-dir>/journal.jsonl`, append-only, one line per event, at most about 140 characters of summary:

```json
{"ts":"2026-10-16T09:12Z","kind":"merge","ref":"S-410@3f2a91c","summary":"merged after review, T2 started"}
```

Emitters are the mechanisms, not the model: `dispatch.sh` (dispatch, resume), the collector (state transitions only, not every poll), the merge step, review verdicts, budget holds and releases, inbox answers. The coordinator writes exactly one kind of line itself, through `sw note "<text>"`, for knowledge that has no other record. A JSON Schema in `schemas/` fixes the kinds. `PROGRESS.md` stays as reading for people and is no longer loaded into the coordinator's context.

### 2. The context pack

`scripts/context-pack.py` reads the allocations, the collector's output, the ledger counts, `NEEDS-HUMAN.md`, the last usage reading, the kill switch, the ready briefs and the journal, and prints fixed sections:

```
RUN       increment 4 "exports" · goal 9/14 rows · budget week 41%, 5h 22% · STOP absent
ALLOC     alloc-411-impl  S-411 codex impl   RUNNING 23m  head 3f2a91c
          alloc-412-impl  S-412 claude impl  BLOCKED      waits C-7 (unblocks on S-411 merge)
DELTA     since the last pack: S-410 DONE→merged · S-411 T1 fail→fixing
INBOX     A1 pricing tiers (blocks S-415, S-416) · veto EUR closes 14h
READY     S-413 brief ready, 1 writer slot free
JOURNAL   last 20 lines of this increment; earlier: 31 dispatch, 12 merge, 4 hold
NEXT      derived: dispatch S-413 · review S-411 on CANDIDATE
POINTERS  briefs/S-413.md · handoffs/alloc-412-impl.md · .run/tiers/
PACK      sha256:…
```

Rules:

- **Pointers, not content.** The pack names files; the coordinator opens one only when it needs it, and reads logs through explorers as the `resume` skill already requires.
- **Hard caps.** Every section has a token cap and ends with "N more, see <path>" when it overflows. The whole pack stays near 3 to 5 thousand tokens however long the run.
- **Deterministic roll-up.** Journal lines older than the current increment collapse into counts per kind. No model writes a summary.
- **Derived, not remembered.** `NEXT` comes from the collector and the ready detector, not from a list the coordinator keeps.
- **Hashed.** The last line is the pack's hash. Each decision line in the journal carries the hash of the pack it was taken from, which answers "what did the coordinator know when it merged S-410?".

### 3. Injection

`hooks/session-context.sh` prints the pack for the coordinator instead of today's pointer paragraph, on `startup|resume|compact`. The worker branch of the hook is unchanged, and the hook stays inert in a project without `.sliceworks/config.env`. Whatever the runtime's compaction summary loses, the exact state comes back on the next turn. Under Codex the same pack is printed by the shim's session start.

### 4. The recovery file

`.run/coordinator-session.md` becomes generated from the allocations and the journal, or is retired if the pack covers it entirely. Either way the model no longer writes it.

### 5. External launchers

A launcher that drives the coordinator through a runtime's SDK can start a fresh coordinator session for each wake: the cached static part (role profile, method rules) first, the pack last. A wake becomes a small transaction (read the pack, act, end), so the coordinator's context never grows large enough to need compaction. Such a launcher calls the script, or a port of it held to the same golden fixtures.

## Trade-off

The coordinator's chain of reasoning no longer carries across a compaction or a wake. That is intended: reasoning that must persist becomes a note, a decision entry or a brief. The cost is discipline in the `resume` and `brief` skills, which must turn any conclusion worth keeping into a record before the turn ends.

## What changes when this is implemented

| Where | Change |
|---|---|
| `schemas/` | `journal-entry.schema.json` |
| `templates/config.env` | the journal path and the pack's caps |
| `scripts/` | `context-pack.py`; the `sw note` command; journal emitters in `dispatch.sh` and `collect.py` |
| `hooks/session-context.sh` | the pack for the coordinator |
| `skills/resume` | read the pack, not the prose files; record conclusions as notes |
| `method/10`, `method/11`, `method/19` | the rule (method), with the reason in `rationale/` |
| `tests/` | golden packs on the fixture projects, cap and overflow tests, determinism (same input, same hash), hook tests |

Done when `sh tests/test_hooks.sh`, `python3 -m unittest discover -s tests` and `claude plugin validate --strict .` pass.

## Sequencing

Not scheduled. It touches `hooks/session-context.sh` and the dispatch path, which the uncommitted 0.8.0 work on this branch and the 0.9.0 spawn guard of the context-isolation note also change, so it lands after both.

## Open questions

- The cap for each section and for the whole pack, to be set from a measured run rather than guessed.
- Whether the journal lives in the state directory (committed, audited) or under `.run/` (local). The decision lines argue for committed.
- Whether Codex's compaction offers a hook point equivalent to Claude Code's `SessionStart` with `compact`, or the pack must be re-injected on the next turn by the Stop hook.
