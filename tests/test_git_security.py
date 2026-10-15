# sliceworks 0.8.2. Git metadata grants and host-side executable-config regression tests.
import ast
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
from safe_git import git_command


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, PKG / path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


roots_module = load('security_writer_roots', 'scripts/runtimes/codex/writer_roots.py')
gate = load('security_gate_runner', 'scripts/runtimes/codex/gate_runner.py')
collector = load('security_collector', 'scripts/collect.py')


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='git security ')
        self.root = Path(self.tmp.name).resolve()
        self.git('init', '-q', '-b', 'main')
        (self.root / 'base').write_text('base\n')
        self.git('add', 'base'); self.git('commit', '-qm', 'base')
        self.wt = self.root / 'writer'
        self.git('worktree', 'add', '-q', '-b', 'slice/secure', self.wt)
        (self.root / 'outputs').mkdir(); (self.root / '.run').mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, cwd=None):
        return subprocess.check_output(git_command('-C', cwd or self.root, '-c', 'user.name=Test', '-c',
                                                  'user.email=t@example.invalid', *args), text=True).strip()

    def roots(self, **kwargs):
        return roots_module.writer_roots(self.root, self.wt, 'outputs', '.run', **kwargs)


class WriterRoots(GitFixture):
    def test_grants_are_exact_files_and_never_the_common_git_directory(self):
        common = self.root / '.git'
        gd = Path(self.git('rev-parse', '--absolute-git-dir', cwd=self.wt))
        ref = common / 'refs/heads/slice/secure'
        log = common / 'logs/refs/heads/slice/secure'
        expected = [gd, common / 'objects', ref, Path(str(ref) + '.lock'), log, Path(str(log) + '.lock'),
                    self.root / 'outputs', self.root / '.run']
        self.assertEqual(self.roots(branch='slice/secure'), list(map(str, expected)))
        self.assertNotIn(str(common), self.roots())
        self.assertNotIn(str(common / 'refs/heads'), self.roots())
        for relative in ('config', 'hooks/x', 'info/x', 'packed-refs', 'refs/heads/main', 'refs/heads/other', 'worktrees/other/index'):
            path = common / relative
            self.assertFalse(any(path.is_relative_to(Path(root)) for root in self.roots()), relative)

    def test_packed_ref_still_gets_only_its_own_loose_ref_and_lock(self):
        self.git('pack-refs', '--all', '--prune')
        own = self.root / '.git/refs/heads/slice/secure'
        self.assertFalse(own.exists())
        self.assertIn(str(own), self.roots())
        self.assertIn(str(own) + '.lock', self.roots())
        self.assertNotIn(str(self.root / '.git/packed-refs'), self.roots())

    def test_host_prepares_only_own_namespace_after_packing(self):
        self.git('pack-refs', '--all', '--prune')
        namespace = self.root / '.git/refs/heads/slice'
        self.assertFalse(namespace.exists())
        self.roots(prepare=True)
        self.assertTrue(namespace.is_dir())
        self.assertFalse((self.root / '.git/refs/heads/slice/secure').exists())
        self.assertFalse((self.root / '.git/refs/heads/main').exists())

    def test_branch_mismatch_and_integration_branch_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'allocation'):
            self.roots(branch='slice/other')
        with self.assertRaisesRegex(ValueError, 'integration'):
            self.roots(integration='slice/secure')

    def test_main_checkout_and_foreign_repository_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'linked worktree'):
            roots_module.writer_roots(self.root, self.root, 'outputs', '.run')
        with self.assertRaisesRegex(ValueError, 'linked worktree'):
            roots_module.writer_roots(self.root / 'wrong-main', self.wt, 'outputs', '.run')

    def test_artifact_roots_cannot_widen_git_access(self):
        for outputs, run in (('.git', '.run'), ('outputs', '.'), ('.git/hooks', '.run')):
            with self.assertRaisesRegex(ValueError, 'expose Git metadata'):
                roots_module.writer_roots(self.root, self.wt, outputs, run)

    def test_symlinked_ref_is_refused(self):
        own = self.root / '.git/refs/heads/slice/secure'
        own.unlink(); own.symlink_to(self.root / '.git/refs/heads/main')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.roots()


class SafeHostGit(GitFixture):
    def setUp(self):
        super().setUp()
        self.monitor_marker, self.hook_marker = self.root / 'monitor-ran', self.root / 'hook-ran'
        monitor = self.root / 'fsmonitor.sh'
        monitor.write_text('#!/bin/sh\necho executed >> ' + shlex.quote(str(self.monitor_marker)) + '\n')
        monitor.chmod(0o755)
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho executed >> ' + shlex.quote(str(self.hook_marker)) + '\n')
        hook.chmod(0o755)
        self.git('config', 'core.fsmonitor', shlex.quote(str(monitor)))
        self.git('config', 'core.hooksPath', self.root / '.git/hooks')
        # Positive control: these exact planted executables run without the safety overrides.
        raw = ['git', '-C', str(self.wt), '-c', 'user.name=Test', '-c', 'user.email=t@example.invalid']
        subprocess.run(raw + ['status', '--porcelain'], check=True, capture_output=True)
        subprocess.run(raw + ['commit', '--allow-empty', '-qm', 'positive control'], check=True, capture_output=True)
        self.assertTrue(self.monitor_marker.exists())
        self.assertTrue(self.hook_marker.exists())
        self.monitor_marker.unlink(); self.hook_marker.unlink()

    def assert_no_execution(self):
        self.assertFalse(self.monitor_marker.exists(), 'host Git executed planted fsmonitor')
        self.assertFalse(self.hook_marker.exists(), 'host Git executed planted hook')

    def test_shared_python_helper_disables_monitor_and_commit_hooks(self):
        self.git('status', '--porcelain', cwd=self.wt)
        self.git('commit', '--allow-empty', '-qm', 'safe commit', cwd=self.wt)
        self.assert_no_execution()

    def test_collector_and_gate_git_helpers_ignore_planted_monitor(self):
        collector.git(self.wt, 'status', '--porcelain')
        gate.git(self.wt, 'status', '--porcelain')
        self.assert_no_execution()

    def test_hook_shell_helper_disables_monitor_and_commit_hooks(self):
        script = '. "$1"; sw_git -C "$2" status --porcelain; sw_git -C "$2" -c user.name=Test -c user.email=t@example.invalid commit --allow-empty -qm safe-shell-commit'
        out = subprocess.run(['sh', '-eu', '-c', script, 'probe', str(PKG / 'hooks/lib.sh'), str(self.wt)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assert_no_execution()

    def test_runtime_modules_have_no_raw_git_subprocess_argv(self):
        for path in ('scripts/collect.py', 'scripts/runtimes/codex/gate_runner.py', 'scripts/runtimes/codex/worker.py',
                     'scripts/runtimes/codex/agents.py', 'scripts/runtimes/codex/writer_roots.py'):
            tree = ast.parse((PKG / path).read_text())
            for call in ast.walk(tree):
                if isinstance(call, ast.Call) and call.args and isinstance(call.args[0], (ast.List, ast.Tuple)):
                    values = call.args[0].elts
                    if values and isinstance(values[0], ast.Constant):
                        self.assertNotEqual(values[0].value, 'git', path)
