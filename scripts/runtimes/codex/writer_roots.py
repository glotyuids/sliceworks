#!/usr/bin/env python3
# sliceworks 0.8.2. Exact Git metadata grants for one linked worktree and its checked-out branch.
"""Render a workspace-write root list without granting the main Git directory."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from safe_git import git_command


def git(cwd, *args):
    return subprocess.check_output(git_command('-C', cwd, *args), text=True).strip()


def writer_roots(root, worktree, outputs, run, integration='main', branch=None, prepare=False):
    root, worktree = Path(root).resolve(), Path(worktree).resolve()
    common = Path(git(worktree, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    gd = Path(git(worktree, 'rev-parse', '--absolute-git-dir')).resolve()
    if common != root / '.git' or gd.parent != common / 'worktrees':
        raise ValueError('writer must use a linked worktree of the configured main checkout')
    ref = git(worktree, 'symbolic-ref', '--quiet', 'HEAD')
    if not ref.startswith('refs/heads/') or ref == 'refs/heads/' + integration:
        raise ValueError('writer must have its own non-integration branch')
    subprocess.run(git_command('check-ref-format', ref), check=True, capture_output=True)
    if branch and ref != 'refs/heads/' + branch:
        raise ValueError('worktree branch differs from its allocation')
    # Ref updates use a sibling lock and atomic rename. Grant those exact files, never their parent directory.
    ref_file, log_file = common / ref, common / 'logs' / ref
    metadata = [gd, common / 'objects', ref_file, Path(str(ref_file) + '.lock'),
                log_file, Path(str(log_file) + '.lock')]
    for path in metadata:
        if path.resolve() != path:
            raise ValueError('symlink in writer Git metadata path: ' + str(path))
    artifacts = [(root / outputs).resolve(), (root / run).resolve()]
    for path in artifacts:
        if path.is_relative_to(common) or common.is_relative_to(path):
            raise ValueError('artifact root would expose Git metadata: ' + str(path))
    if prepare:
        # pack-refs may remove empty branch namespace directories. Only the host creates these parents;
        # granting the parent would expose sibling branches to the writer.
        ref_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.parent.mkdir(parents=True, exist_ok=True)
    return [str(path) for path in metadata + artifacts]


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root'); ap.add_argument('worktree'); ap.add_argument('outputs'); ap.add_argument('run')
    ap.add_argument('--integration', default='main'); ap.add_argument('--branch')
    ap.add_argument('--prepare', action='store_true', help='host: create only the own branch/reflog parent directories')
    args = ap.parse_args()
    try:
        print(json.dumps(writer_roots(args.root, args.worktree, args.outputs, args.run, args.integration, args.branch, args.prepare)))
    except (ValueError, subprocess.CalledProcessError) as exc:
        ap.exit(2, 'dispatch: cannot grant writer roots: ' + str(exc) + '\n')
