#!/bin/sh
# sliceworks 0.7.0. dashboard-loop.sh [seconds] - rebuild the dashboard every N seconds (default 30) while a session
# runs it with run_in_background, and run SW_DASHBOARD_PUBLISH_CMD (if set) every SW_DASHBOARD_PUBLISH_EVERY seconds
# (default 900). No model turn. Exits 0 at once when the project has no .sliceworks/config.env.
# Run from the repository root. Finds the dashboard next to itself (an installed copy: scripts/sliceworks/dashboard)
# or one level up (the package: dashboard/).
here="$(cd "$(dirname "$0")" && pwd)"
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
[ -f "$root/.sliceworks/config.env" ] || exit 0
# shellcheck disable=SC1091
. "$root/.sliceworks/config.env"
if [ -d "$here/dashboard" ]; then dash="$here/dashboard"; else dash="$here/../dashboard"; fi
run_dir="$root/${SW_RUN_DIR:-.run}"
mkdir -p "$run_dir"
last=0
while :; do
  [ -e "$root/${SW_STATE_DIR:-docs/process}/STOP" ] && exit 0
  python3 "$dash" --root "$root" >/dev/null 2>>"$run_dir/dashboard.err" || echo "DASHBOARD-ERROR $(date -u +%Y-%m-%dT%H:%MZ)" >&2
  now=$(date +%s)
  if [ -n "${SW_DASHBOARD_PUBLISH_CMD:-}" ] && [ $((now - last)) -ge "${SW_DASHBOARD_PUBLISH_EVERY:-900}" ]; then
    (cd "$root" && sh -c "$SW_DASHBOARD_PUBLISH_CMD") >>"$run_dir/dashboard-publish.log" 2>&1
    last=$now
  fi
  sleep "${1:-30}"
done
