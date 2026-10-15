# sliceworks 0.8.0. The Codex runtime: the two manifests agree, the agent sync and its parity check, and the worker
# launcher (dispatch.sh) driven against a stand-in `codex` that records its argv, role and working directory.
import datetime, json, os, pathlib, subprocess, tempfile, tomllib, unittest

PKG = pathlib.Path(__file__).resolve().parents[1]
CODEX = PKG / "scripts" / "runtimes" / "codex"
FAKE = """#!/bin/sh
o=""; prev=""; for a in "$@"; do [ "$prev" = "-o" ] && o="$a"; prev="$a"; done
{ printf '%s\\n' "$@"; echo "ROLE=$SW_ROLE"; echo "PWD=$(pwd)"; echo "MARKER=$(cat "$(git rev-parse --absolute-git-dir)/sliceworks-role" 2>/dev/null)"; } > "$FAKE_ARGS"
echo '{"type":"thread.started","thread_id":"th-123"}'
echo '{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":5}}'
[ -z "$o" ] || printf 'CANDIDATE outputs/slices/slice-07/t1.log\\n' > "$o"
"""


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True, text=True).stdout.strip()


class Manifests(unittest.TestCase):
    def test_codex_manifest_matches_claude_manifest(self):
        claude = json.loads((PKG / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((PKG / ".codex-plugin/plugin.json").read_text())
        for key in ("name", "version", "description", "license"):
            self.assertEqual(claude[key], codex[key], key)


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = pathlib.Path(os.path.realpath(self.tmp.name))
        git(self.root, "init", "-q"); git(self.root, "commit", "-q", "--allow-empty", "-m", "base")
        (self.root / ".sliceworks").mkdir()
        (self.root / ".sliceworks/config.env").write_text('SW_STATE_DIR=docs/process\nSW_CODEX_MODEL_STRONG="gpt-strong"  # comment\nSW_WRITER_CAP=1\n')
        (self.root / "docs/process/allocations").mkdir(parents=True); (self.root / "docs/process/metrics").mkdir()
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.root / "docs/process/metrics/usage.jsonl").write_text(json.dumps({"at": now, "weekly_pct": 10, "five_hour_pct": 5}) + "\n")
        self.wt = self.root / ".claude/worktrees/slice-07"
        git(self.root, "worktree", "add", "-q", "-b", "slice/07", str(self.wt))
        self.bin = self.root / "bin"; self.bin.mkdir(); (self.bin / "codex").write_text(FAKE); (self.bin / "codex").chmod(0o755)
        self.args = self.root / "args.txt"
        self.alloc("alloc-slice-07-r1", {"role": "slice-implementer", "worktree": ".claude/worktrees/slice-07",
                                          "message_ref": "docs/process/slices/slice-07.md", "completion": "rows of slice-07 pass in T1",
                                          "execution": {"pid_file": ".run/slice-07.pid"}})

    def tearDown(self):
        self.tmp.cleanup()

    def alloc(self, aid, extra):
        (self.root / f"docs/process/allocations/{aid}.json").write_text(json.dumps({"id": aid, "slice": "slice-07", **extra}))

    def agents(self, *args):
        return subprocess.run(["python3", str(CODEX / "agents.py"), *args, "--root", str(self.root)], capture_output=True, text=True)

    def dispatch(self, *args):
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_ARGS": str(self.args)}
        env.pop("CLAUDE_PROJECT_DIR", None); env.pop("SW_ROLE", None)
        return subprocess.run(["sh", str(CODEX / "dispatch.sh"), *args], cwd=self.root, env=env, capture_output=True, text=True)

    def argv(self):
        return self.args.read_text().splitlines()


class Agents(Project):
    def test_sync_then_check_is_in_parity(self):
        self.assertEqual(self.agents("check").returncode, 1)
        self.assertEqual(self.agents("sync").returncode, 0)
        out = self.agents("check"); self.assertEqual(out.returncode, 0, out.stdout)
        names = sorted(p.stem for p in (self.root / ".codex/agents").glob("*.toml"))
        self.assertNotIn("slice-implementer", names)
        self.assertIn("code-reviewer", names)
        for p in (self.root / ".codex/agents").glob("*.toml"):
            doc = tomllib.loads(p.read_text())
            self.assertEqual(doc["name"], p.stem)
            self.assertTrue(doc["developer_instructions"].strip())

    def test_models_map_by_class(self):
        self.agents("sync")
        architect = tomllib.loads((self.root / ".codex/agents/architect.toml").read_text())
        reviewer = tomllib.loads((self.root / ".codex/agents/code-reviewer.toml").read_text())
        self.assertEqual(architect["model"], "gpt-strong")
        self.assertEqual(architect["model_reasoning_effort"], "xhigh")
        self.assertNotIn("model", reviewer)

    def test_hand_edit_is_drift_but_a_version_stamp_is_not(self):
        self.agents("sync")
        f = self.root / ".codex/agents/researcher.toml"
        lines = f.read_text().split("\n"); lines[0] = "# sliceworks 0.0.1, generated"; f.write_text("\n".join(lines))
        self.assertEqual(self.agents("check").returncode, 0)
        f.write_text(f.read_text() + "# local\n")
        out = self.agents("check"); self.assertEqual(out.returncode, 1); self.assertIn("STALE .codex/agents/researcher.toml", out.stdout)


class Dispatch(Project):
    def test_worker_runs_in_its_worktree_with_its_role_and_a_fresh_prompt(self):
        out = self.dispatch("alloc-slice-07-r1", "--wait"); self.assertEqual(out.returncode, 0, out.stderr)
        argv = self.argv()
        self.assertEqual(argv[:2], ["exec", "--json"])
        self.assertEqual(argv[argv.index("-s") + 1], "workspace-write")
        self.assertIn(f"PWD={self.wt}", argv); self.assertIn("ROLE=slice-implementer", argv)
        self.assertIn("Allocation alloc-slice-07-r1 (slice-implementer, slice-07)", self.args.read_text())
        self.assertIn("Goal: rows of slice-07 pass in T1.", self.args.read_text())
        gitdir = git(self.wt, "rev-parse", "--absolute-git-dir")
        self.assertIn("MARKER=slice-implementer", argv)
        self.assertFalse(pathlib.Path(gitdir, "sliceworks-role").exists(), "the marker outlives its worker")
        self.assertEqual(git(self.wt, "status", "--short"), "")
        logs = sorted((self.root / "outputs/slices/slice-07/codex").glob("slice-implementer-*.jsonl"))
        self.assertEqual(len(logs), 1)
        self.assertTrue(logs[0].with_suffix(".done").read_text().startswith("0 "))
        self.assertTrue(logs[0].with_suffix(".last").read_text().startswith("CANDIDATE"))

    def test_resume_continues_the_recorded_thread(self):
        self.dispatch("alloc-slice-07-r1", "--wait")
        out = self.dispatch("alloc-slice-07-r1", "--resume", "FINDINGS: H1 fix the nil check", "--wait"); self.assertEqual(out.returncode, 0, out.stderr)
        argv = self.argv()
        self.assertEqual(argv[:3], ["exec", "resume", "th-123"])
        self.assertIn("FINDINGS: H1 fix the nil check", argv)
        self.assertNotIn("You implement one slice", self.args.read_text())

    def test_reviewer_is_read_only(self):
        self.alloc("rev-slice-07", {"role": "code-reviewer", "mode": "review"})
        out = self.dispatch("rev-slice-07", "--wait"); self.assertEqual(out.returncode, 0, out.stderr)
        argv = self.argv()
        self.assertEqual(argv[argv.index("-s") + 1], "read-only")
        self.assertFalse(any("writable_roots" in a for a in argv))
        self.assertIn("ROLE=code-reviewer", argv)

    def test_refusals(self):
        (self.root / "docs/process/STOP").write_text("halt")
        out = self.dispatch("alloc-slice-07-r1", "--wait"); self.assertEqual(out.returncode, 3); self.assertIn("STOP", out.stderr)
        (self.root / "docs/process/STOP").unlink()
        self.assertEqual(self.dispatch("missing-alloc").returncode, 2)
        sleeper = subprocess.Popen(["sleep", "30"])
        try:
            (self.root / ".run").mkdir(exist_ok=True)
            (self.root / ".run/other.pid").write_text(str(sleeper.pid)); (self.root / ".run/other.writer").write_text("")
            out = self.dispatch("alloc-slice-07-r1", "--wait"); self.assertEqual(out.returncode, 3); self.assertIn("writer cap", out.stderr)
            (self.root / ".run/slice-07.pid").write_text(str(sleeper.pid))
            out = self.dispatch("alloc-slice-07-r1", "--wait"); self.assertIn("already has a live worker", out.stderr)
        finally:
            sleeper.kill(); sleeper.wait()

    def test_budget_hold_refuses(self):
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.root / "docs/process/metrics/usage.jsonl").write_text(json.dumps({"at": now, "weekly_pct": 90, "five_hour_pct": 5}) + "\n")
        out = self.dispatch("alloc-slice-07-r1", "--wait"); self.assertEqual(out.returncode, 3); self.assertIn("Budget hold", out.stderr)

    def test_status_lists_finished_workers(self):
        self.dispatch("alloc-slice-07-r1", "--wait")
        out = subprocess.run(["sh", str(CODEX / "status.sh")], cwd=self.root, capture_output=True, text=True,
                             env={k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"})
        self.assertIn("DONE", out.stdout); self.assertIn("CANDIDATE", out.stdout)


if __name__ == "__main__":
    unittest.main()
