#!/bin/sh
# sliceworks 0.8.0. List the Codex worker processes of this project (dispatch.sh): running ones (no .done yet) and
# finished ones with the first line of their final message (CANDIDATE / BLOCKED / HOLD / REVIEW). No model turn.
# Run from the project's main checkout or any of its worktrees.
here="$(cd "$(dirname "$0")" && pwd)"; PKG="$(cd "$here/../../.." && pwd)"
input='{}'; . "$PKG/hooks/lib.sh"; sw_load_config || { echo "status: no .sliceworks/config.env" >&2; exit 2; }
for j in "$SW_ROOT/$SW_OUTPUTS_DIR"/slices/*/codex/*.jsonl; do
  [ -e "$j" ] || continue
  base="${j%.jsonl}"; slice="$(basename "$(dirname "$(dirname "$j")")")"; name="$(basename "$base")"
  if [ -f "$base.done" ]; then
    first="$(head -n 1 "$base.last" 2>/dev/null | cut -c1-160)"
    printf 'DONE    %-14s %-34s exit %s  %s\n' "$slice" "$name" "$(cat "$base.done")" "${first:-<no final message; see ${base#"$SW_ROOT"/}.err>}"
  else
    printf 'RUNNING %-14s %-34s since %s\n' "$slice" "$name" "$(date -r "$j" -u +%H:%MZ 2>/dev/null || echo '?')"
  fi
done
