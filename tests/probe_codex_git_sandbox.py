#!/usr/bin/env python3
# sliceworks 0.8.2. Explicit live CLI sandbox probe; never dispatches a model.
"""Probe writer Git grants on an installed Codex CLI, retaining commands and evidence under .run."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import queue
import threading

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
from safe_git import git_command

spec = importlib.util.spec_from_file_location('writer_roots', PKG / 'scripts/runtimes/codex/writer_roots.py')
roots_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roots_module)

PAYLOAD = '''import json, os, subprocess
from pathlib import Path
root = Path(os.environ['PROBE_MAIN'])
results = []
Path('candidate.txt').write_text('sandbox commit proof\\n')
for command in (['git', 'add', 'candidate.txt'], ['git', '-c', 'user.name=Sandbox Probe', '-c', 'user.email=probe@example.invalid', 'commit', '-m', 'sandbox commit proof']):
    child = subprocess.run(command, capture_output=True, text=True)
    results.append({'command': command, 'exit_code': child.returncode, 'stdout': child.stdout, 'stderr': child.stderr})
for relative in ('.git/config', '.git/hooks/x', '.git/info/x', '.git/packed-refs', '.git/refs/heads/main', '.git/refs/heads/other', '.git/worktrees/other/index'):
    path = root / relative
    try:
        # Opening is itself a write attempt; do not corrupt the disposable repository on a failed boundary.
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        os.close(fd)
        results.append({'write': relative, 'refused': False})
    except OSError as exc:
        results.append({'write': relative, 'refused': True, 'errno': exc.errno, 'error': str(exc)})
print(json.dumps(results, indent=2))
raise SystemExit(0 if all(row.get('exit_code', 0) == 0 and row.get('refused', True) for row in results) else 1)
'''


def host_git(cwd, *args):
    return subprocess.run(git_command('-C', cwd, '-c', 'user.name=Sandbox Probe', '-c',
                                     'user.email=probe@example.invalid', *args),
                          capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--codex', default='codex')
    ap.add_argument('--packed', action='store_true', help='also require creating the own loose ref from packed refs')
    args = ap.parse_args()
    parent = PKG / '.run'; parent.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='codex-git-probe-', dir=parent)).resolve()
    root, wt = directory / 'main', directory / 'writer'
    root.mkdir()
    host_git(root, 'init', '-q', '-b', 'main')
    (root / 'base.txt').write_text('base\n')
    host_git(root, 'add', 'base.txt'); host_git(root, 'commit', '-qm', 'base')
    host_git(root, 'worktree', 'add', '-q', '-b', 'slice/probe', wt)
    host_git(root, 'worktree', 'add', '-q', '-b', 'other', directory / 'other')
    if args.packed:
        host_git(root, 'pack-refs', '--all', '--prune')
    (root / 'outputs').mkdir(); (root / '.run').mkdir()
    cli_home = directory / 'cli-home'; cli_home.mkdir()
    payload = wt / 'probe_payload.py'; payload.write_text(PAYLOAD)
    roots = roots_module.writer_roots(root, wt, 'outputs', '.run', branch='slice/probe', prepare=True)
    command = [args.codex, 'app-server', '-c', 'sandbox_mode="workspace-write"',
               '-c', 'sandbox_workspace_write.writable_roots=' + json.dumps(roots),
               '-c', 'sandbox_workspace_write.network_access=false', '-c', 'approval_policy="never"',
               '-c', 'web_search="disabled"']
    before_main = host_git(root, 'rev-parse', 'main')
    before_slice = host_git(wt, 'rev-parse', 'HEAD')
    version = subprocess.run([args.codex, '--version'], capture_output=True, text=True, check=True).stdout.strip()
    requests = []
    with (directory / 'app-server.stderr').open('w') as err:
        server = subprocess.Popen(command, cwd=wt, env={**os.environ, 'CODEX_HOME': str(cli_home)},
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True)
        messages = queue.Queue()
        def read():
            for line in server.stdout:
                messages.put(json.loads(line))
        reader = threading.Thread(target=read, daemon=True); reader.start()
        def rpc(rid, method, params):
            request = {'id': rid, 'method': method, 'params': params}; requests.append(request)
            server.stdin.write(json.dumps(request) + '\n'); server.stdin.flush()
            while True:
                message = messages.get(timeout=60)
                if message.get('id') == rid:
                    if 'error' in message:
                        raise RuntimeError(message['error'])
                    return message['result']
        try:
            rpc(1, 'initialize', {'clientInfo': {'name': 'sliceworks-git-probe', 'version': '0.8.2'},
                                  'capabilities': {'experimentalApi': True}})
            response = rpc(2, 'command/exec', {'command': [sys.executable, str(payload)], 'cwd': str(wt),
                                              'env': {'PROBE_MAIN': str(root)}, 'timeoutMs': 30000})
        finally:
            server.terminate(); server.wait(timeout=10)
            server.stdin.close(); server.stdout.close(); reader.join(timeout=1)
    evidence = {'cli_version': version, 'mode': 'codex app-server command/exec sandbox (no thread or model dispatch)', 'directory': str(directory),
                'packed_refs': args.packed, 'command': command, 'requests': requests, 'writable_roots': roots, 'exit_code': response['exitCode'],
                'stdout': response['stdout'], 'stderr': response['stderr'],
                'main_unchanged': host_git(root, 'rev-parse', 'main') == before_main,
                'slice_committed': host_git(wt, 'rev-parse', 'HEAD') != before_slice}
    (directory / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))
    return 0 if response['exitCode'] == 0 and evidence['main_unchanged'] and evidence['slice_committed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
