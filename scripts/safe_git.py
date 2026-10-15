# sliceworks 0.8.2. Git argv shared by host-side Python readers and the Codex launcher.
"""Disable executable repository configuration before running host-side Git."""


def git_command(*args):
    return ['git', '-c', 'core.fsmonitor=', '-c', 'core.hooksPath=/dev/null', *map(str, args)]
