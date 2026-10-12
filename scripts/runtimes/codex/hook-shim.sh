#!/bin/sh
# codex-hook.sh <hook-script> — run a .claude/hooks/<hook-script> under Codex (RUNTIMES.md section 7). Reads the
# Codex hook JSON on stdin, rewrites it into the shape the Claude hook scripts read, runs the script with
# CLAUDE_PROJECT_DIR set, and passes its stdout and exit status back. Tool names: shell/exec_command/local_shell ->
# Bash (command arrays are joined), apply_patch -> Edit (first file named in the patch), spawn_agent -> Agent.
# Refusal fixtures and live tool calls verified in RUNTIMES.md section 9; merge backstops still apply.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../.." && pwd)"
script="${1:?hook script name, e.g. stop-guard.sh}"
case "$script" in */*|..*) echo "codex-hook: bad script name" >&2; exit 2;; esac
target="$ROOT/.claude/hooks/$script"
[ -x "$target" ] || { echo "codex-hook: $target missing" >&2; exit 2; }
input="$(cat)"
norm="$(printf '%s' "$input" | jq -c '
  def tn: (.tool_name // .tool // .name // "");
  def cmd: (.tool_input.command // .tool_input.cmd // .arguments.command // .arguments.cmd // .input.command // null)
           | if type == "array" then (if .[0] == "bash" and .[1] == "-lc" then .[2] else join(" ") end) else . end;
  def patchfiles: [((.tool_input.command // .tool_input.input // .arguments.input // .input // "") | tostring
           | match("\\*\\*\\* ((Add|Update|Delete) File|Move to): (?<f>[^\\n]+)"; "g").captures[]
           | select(.name == "f").string)];
  . as $in
  | (tn) as $t
  | (if ($t|test("^(shell|exec_command|local_shell|container.exec|bash)$";"i")) then "Bash"
     elif ($t|test("apply_patch";"i")) then "Edit"
     elif ($t|test("spawn_agent";"i")) then "Agent"
     else $t end) as $mapped
  | $in + {hook_event_name: ($in.hook_event_name // $in.event // "PreToolUse"),
     tool_name: $mapped,
     cwd: ($in.cwd // $in.workdir // null),
     tool_input: (($in.tool_input // {}) + {command: cmd, file_paths: patchfiles,
       file_path: ($in.tool_input.file_path // (patchfiles | .[0]) // null)})}
' 2>/dev/null)" || { echo "codex-hook: invalid hook input" >&2; exit 2; }
CLAUDE_PROJECT_DIR="$ROOT" export CLAUDE_PROJECT_DIR
if [ "$(printf '%s' "$norm" | jq -r '.tool_name')" = Edit ]; then
  paths="$(printf '%s' "$norm" | jq -r '.tool_input.file_paths[]')"
  if [ -n "$paths" ]; then
    set -f
    oldifs="$IFS"; IFS='
'
    for path in $paths; do
      result="$(printf '%s' "$norm" | jq -c --arg p "$path" '.tool_input.file_path = $p' | "$target")" || exit $?
      [ -z "$result" ] || { printf '%s\n' "$result"; exit 0; }
    done
    IFS="$oldifs"
    exit 0
  fi
fi
printf '%s' "$norm" | "$target"
