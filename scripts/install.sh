#!/usr/bin/env sh
# sliceworks 0.7.0. Copy-install the skills (and, for Claude Code without the plugin, the agents) into a project
# or into the user's agent directories, for runtimes without a plugin system or when a plugin is not wanted.
#
#   scripts/install.sh <project-dir> --tools codex            # project scope: .agents/skills
#   scripts/install.sh <project-dir> --tools codex,claude     # also .claude/skills and .claude/agents
#   scripts/install.sh --user --tools codex                   # user scope: ~/.agents/skills
#   scripts/install.sh <project-dir> --tools cursor --dry-run
#   scripts/install.sh <project-dir> --dashboard              # the dashboard and its loop: scripts/sliceworks/
#
# Copies, never symlinks. Never overwrites an existing skill or agent unless --force is given. Every copied
# SKILL.md keeps its metadata.source and metadata.version, which is what the update skill compares.
set -eu
LIB="$(cd "$(dirname "$0")/.." && pwd)"
TARGET=""; TOOLS=""; USER_SCOPE=0; DRY=0; FORCE=0; DASH=0
usage() { sed -n '3,14p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --tools) TOOLS="${2:-}"; shift 2;; --user) USER_SCOPE=1; shift;; --dry-run) DRY=1; shift;; --force) FORCE=1; shift;; --dashboard) DASH=1; shift;;
    -h|--help) usage 0;; -*) echo "unknown flag $1" >&2; usage 1;; *) TARGET="$1"; shift;;
  esac
done
[ -n "$TOOLS" ] || [ "$DASH" -eq 1 ] || { echo "error: --tools codex|claude|cursor[,...] or --dashboard is required" >&2; usage 1; }
if [ "$USER_SCOPE" -eq 1 ]; then TARGET="$HOME"; else [ -n "$TARGET" ] && [ -d "$TARGET" ] || { echo "error: project directory missing" >&2; usage 1; }; fi
skills_dir() { case "$1" in claude) echo ".claude/skills";; codex|gemini|copilot) echo ".agents/skills";; cursor) echo ".cursor/skills";; *) echo "";; esac; }
agents_dir() { case "$1" in claude) echo ".claude/agents";; cursor) echo ".cursor/agents";; *) echo "";; esac; }
installed=0; skipped=0
copy() { # copy <src> <dst> <label>
  if [ -e "$2" ] && [ "$FORCE" -eq 0 ]; then echo "  = kept existing $3"; skipped=$((skipped+1)); return; fi
  echo "  + $3 -> ${2#"$TARGET"/}"
  if [ "$DRY" -eq 0 ]; then mkdir -p "$(dirname "$2")"; rm -rf "$2"; cp -R "$1" "$2"; fi
  installed=$((installed+1))
}
echo "sliceworks install: target $TARGET$([ "$USER_SCOPE" -eq 1 ] && echo ' (user scope)'), tools $TOOLS$([ "$DRY" -eq 1 ] && echo ', dry run')"
old_ifs="$IFS"; IFS=','; for tool in $TOOLS; do IFS="$old_ifs"
  sd="$(skills_dir "$tool")"; [ -n "$sd" ] || { echo "  ! unknown tool $tool"; continue; }
  echo "tool: $tool"
  for s in "$LIB"/skills/*/; do copy "$s" "$TARGET/$sd/$(basename "$s")" "skill $(basename "$s")"; done
  ad="$(agents_dir "$tool")"
  if [ -n "$ad" ]; then for a in "$LIB"/agents/*.md; do copy "$a" "$TARGET/$ad/$(basename "$a")" "agent $(basename "$a" .md)"; done; fi
done; IFS="$old_ifs"
if [ "$DASH" -eq 1 ]; then
  [ "$USER_SCOPE" -eq 0 ] || { echo "error: --dashboard installs into a project, not the user scope" >&2; exit 1; }
  echo "dashboard:"
  copy "$LIB/dashboard" "$TARGET/scripts/sliceworks/dashboard" "dashboard (collect, compute, render)"
  copy "$LIB/scripts/dashboard-loop.sh" "$TARGET/scripts/sliceworks/dashboard-loop.sh" "dashboard-loop.sh"
  [ "$DRY" -eq 1 ] || rm -rf "$TARGET/scripts/sliceworks/dashboard/__pycache__"
fi
echo "installed: $installed, kept: $skipped"
[ "$USER_SCOPE" -eq 1 ] || echo "Next: run the start skill in the project (adopt writes the configuration); for Codex, hooks and generated agents come with the dual profile (templates/codex-config.toml, scripts/runtimes/codex)."
