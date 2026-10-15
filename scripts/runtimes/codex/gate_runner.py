#!/usr/bin/env python3
# sliceworks 0.8.1. Request data selects an allocation and T1, never a shell command.
"""Run one pending gate request through the project's trusted, slot-admitting verifier."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import uuid


def atomic_json(path, value):
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(value) + '\n')
    tmp.replace(path)


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def run(aid):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', aid):
        raise ValueError('invalid allocation id')
    root = Path(os.environ['SW_ROOT']).resolve()
    run_dir = root / os.environ['SW_RUN_DIR'] / 'codex' / aid
    request = run_dir / 'gate-request.json'
    if not request.exists():
        return 0
    lock = run_dir / 'gate.lock'
    try:
        lock.mkdir()
    except FileExistsError:
        return 0  # One host runner owns this request. Never start a duplicate.
    result = {'result': 'NOT_RUN', 'exit_code': None, 'log': None}
    active = run_dir / 'gate-active.json'
    owned_active = False
    try:
        if request.is_symlink() or active.exists():
            raise ValueError('symlink request or unresolved active gate; inspect before retrying')
        request.rename(active)
        owned_active = True
        req = json.loads(active.read_text())
        result.update(request_id=req.get('request_id'), head=req.get('head'))
        if set(req) != {'request_id', 'allocation', 'slice', 'head', 'tier'}:
            raise ValueError('request must contain only request_id, allocation, slice, head, tier')
        rid = req['request_id']
        if not isinstance(rid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', rid):
            raise ValueError('invalid request_id')
        receipt = run_dir / ('gate-' + rid + '.json')
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if any(saved.get(key) != value for key, value in req.items()):
                raise ValueError('request_id was already used for different source or allocation')
            result = saved
            return 0 if result['result'] == 'pass' else 1
        alloc = json.loads((root / os.environ['SW_STATE_DIR'] / 'allocations' / (aid + '.json')).read_text())
        if alloc.get('role', 'slice-implementer').split(':')[-1] != 'slice-implementer':
            raise ValueError('database gate requires an implementer allocation')
        if alloc.get('state') in ('closed', 'collected'):
            raise ValueError('allocation is closed')
        if req['allocation'] != aid or req['slice'] != alloc['slice'] or req['tier'] != 't1':
            raise ValueError('allocation/slice mismatch or disallowed tier (only t1)')
        if not re.fullmatch(r'[0-9a-f]{40}', str(req['head'])):
            raise ValueError('head must be a full commit SHA')
        wt = (root / alloc['worktree']).resolve()
        if Path(git(wt, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve() != root / '.git':
            raise ValueError('worktree belongs to another repository')
        if git(wt, 'rev-parse', 'HEAD') != req['head']:
            raise ValueError('request head is stale')
        if subprocess.run(['git', '-C', str(wt), 'diff', '--quiet']).returncode or subprocess.run(['git', '-C', str(wt), 'diff', '--cached', '--quiet']).returncode:
            raise ValueError('commit tracked worktree changes before requesting verification')
        if (root / os.environ['SW_STOP_FILE']).exists():
            raise ValueError('STOP kill switch present')
        verify = (root / os.environ['SW_VERIFY_CMD']).resolve()
        if not verify.is_relative_to(root) or not verify.is_file() or not os.access(verify, os.X_OK):
            raise ValueError('configured main-checkout verifier is unavailable')
        log = run_dir / ('gate-' + rid + '.log')
        command = [str(verify), '--cwd', str(wt), '--slice', req['slice'], '--base', alloc['base'], 't1']
        result.update(command=command, head=req['head'], tier='t1', allocation=aid, slice=req['slice'], log=str(log))
        # The existing verifier owns verification-slot admission, including tickets and stale-slot recovery.
        # Its configured contract must accept --cwd/--slice/--base and must not bypass its slot queue.
        env = {**os.environ, 'SW_ALLOCATION': aid, 'SW_CODEX_RUN_DIR': str(run_dir),
               'SW_METRICS_DIR': str(run_dir / 'metrics'), 'SW_TIERS_FILE': str(run_dir / 'metrics/tiers.jsonl')}
        (run_dir / 'metrics').mkdir(exist_ok=True)
        with log.open('x') as out:
            child = subprocess.run(command, cwd=wt, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
        text = log.read_text(errors='replace')
        markers = re.findall(r'^RESULT=(\w+)\b', text, re.M)
        passed = child.returncode == 0 and bool(markers) and markers[-1] == 'pass'
        if git(wt, 'rev-parse', 'HEAD') != req['head'] or subprocess.run(['git', '-C', str(wt), 'diff', '--quiet']).returncode or subprocess.run(['git', '-C', str(wt), 'diff', '--cached', '--quiet']).returncode:
            passed = False
            result['error'] = 'worktree head or tracked source changed during verification'
        result.update(result='pass' if passed else 'fail', exit_code=child.returncode)
        with log.open('a') as out:
            out.write('\nRESULT=' + result['result'] + '\n')
        result['at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Durable transport row, even if the project verifier uses its own metrics format.
        with (run_dir / 'metrics/tiers.jsonl').open('a') as out:
            out.write(json.dumps({**result, 'head_full': req['head']}) + '\n')
        atomic_json(receipt, result)
    except Exception as exc:
        result.update(result='NOT_RUN' if result['exit_code'] is None else 'fail', error=str(exc))
        if result.get('log') and result['exit_code'] is not None:
            with Path(result['log']).open('a') as out:
                out.write('\nRESULT=fail\n')
    finally:
        atomic_json(run_dir / 'gate-result.json', result)
        if owned_active and active.exists():
            active.replace(run_dir / 'gate-request.last.json')
        lock.rmdir()
    return 0 if result['result'] == 'pass' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('allocation')
    args = parser.parse_args()
    raise SystemExit(run(args.allocation))
