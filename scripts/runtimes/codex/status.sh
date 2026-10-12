#!/bin/sh
# codex-status.sh — list Codex session dispatches (RUNTIMES.md section 6): running ones (no .done yet) and finished
# ones with the first line of their final message (CANDIDATE / BLOCKED / HOLD / REVIEW verdict). No model turn.
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../.." && pwd)"
for j in "$ROOT"/outputs/slices/*/codex/*.jsonl; do
  [ -e "$j" ] || continue
  base="${j%.jsonl}"; slice="$(basename "$(dirname "$(dirname "$j")")")"; name="$(basename "$base")"
  if [ -f "$base.done" ]; then
    first="$(head -1 "$base.last" 2>/dev/null | cut -c1-160)"
    printf 'DONE    %-12s %-28s %s  %s\n' "$slice" "$name" "$(cat "$base.done")" "${first:-<no final message; see $base.err>}"
  else
    printf 'RUNNING %-12s %-28s since %s\n' "$slice" "$name" "$(date -r "$j" -u +%H:%MZ)"
  fi
done
