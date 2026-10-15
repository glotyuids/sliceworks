# sliceworks 0.8.0. The Codex runtime: the two manifests agree, the agent sync and its parity check, and the worker
# launcher (dispatch.sh) driven against a stand-in `codex` that records its argv, role and working directory.
import datetime, json, os, pathlib, subprocess, tempfile, time, tomllib, unittest

PKG = pathlib.Path(__file__).resolve().parents[1]
CODEX = PKG / "scripts" / "runtimes" / "codex"
FAKE = """#!/bin/sh
o=""; prev=""; for a in "$@"; do [ "$prev" = "-o" ] && o="$a"; prev="$a"; done
{ printf '%s\\n' "$@"; echo "ROLE=$SW_ROLE"; echo "METRICS=$SW_METRICS_DIR"; echo "TIERS=$SW_TIERS_FILE"; echo "PWD=$(pwd)"; echo "MARKER=$(cat "$(git rev-parse --absolute-git-dir)/sliceworks-role" 2>/dev/null)"; } > "$FAKE_ARGS"
echo '{"type":"thread.started","thread_id":"th-123"}'
[ -z "$FAKE_SLEEP" ] || sleep "$FAKE_SLEEP"
if [ -n "$FAKE_GATE_REQUEST" ]; then
  cp "$FAKE_GATE_REQUEST" "$SW_CODEX_RUN_DIR/gate-request.json"
  n=0; while [ -z "$FAKE_GATE_NO_WAIT" ] && [ ! -f "$SW_CODEX_RUN_DIR/gate-result.json" ] && [ "$n" -lt 100 ]; do sleep .1; n=$((n+1)); done
  [ -n "$FAKE_GATE_NO_WAIT" ] || [ -f "$SW_CODEX_RUN_DIR/gate-result.json" ] || exit 9
fi
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
        (self.root / f"docs/process/allocations/{aid}.json").write_text(json.dumps({"id": aid, "slice": "slice-07", "base": git(self.root, "rev-parse", "HEAD"), **extra}))

    def agents(self, *args):
        return subprocess.run(["python3", str(CODEX / "agents.py"), *args, "--root", str(self.root)], capture_output=True, text=True)

    def environment(self):
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_ARGS": str(self.args)}
        env.pop("CLAUDE_PROJECT_DIR", None); env.pop("SW_ROLE", None)
        return env

    def dispatch(self, *args):
        return subprocess.run(["sh", str(CODEX / "dispatch.sh"), *args], cwd=self.root, env=self.environment(), capture_output=True, text=True)

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
        self.assertNotIn("-s", argv)
        self.assertIn('sandbox_mode="workspace-write"', argv)
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


class HardenedDispatch(Project):
    def configure(self, line):
        with (self.root / ".sliceworks/config.env").open("a") as out:
            out.write(line + "\n")

    def test_custom_binary_and_missing_binary_guidance(self):
        custom = self.bin / "custom codex"
        custom.write_text(FAKE); custom.chmod(0o755)
        self.configure('SW_CODEX_BIN="' + str(custom) + '"')
        self.assertEqual(self.dispatch("alloc-slice-07-r1", "--wait").returncode, 0)
        self.configure('SW_CODEX_BIN=/missing/codex')
        out = self.dispatch("alloc-slice-07-r1", "--wait")
        self.assertEqual(out.returncode, 2)
        self.assertIn("SW_CODEX_BIN", out.stderr)
        self.assertIn("ChatGPT.app", out.stderr)

    def test_network_is_explicitly_disabled_and_overrides_fail_closed(self):
        out = self.dispatch("alloc-slice-07-r1", "--dry-run")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("network_access=false", out.stdout)
        self.assertNotIn("network_access=true", out.stdout)
        for mode in ("1", "local", "invalid"):
            self.configure("SW_CODEX_NETWORK=" + mode)
            out = self.dispatch("alloc-slice-07-r1", "--dry-run")
            self.assertEqual(out.returncode, 2, out.stderr)
            self.assertIn("gate-runner.sh", out.stderr)
        self.configure("SW_CODEX_NETWORK=0")
        for flag in ('-c sandbox_workspace_write.network_access=true', '--sandbox danger-full-access', '--enable network_proxy', '--add-dir /', '--dangerously-bypass-approvals-and-sandbox'):
            self.configure('SW_CODEX_EXEC_ARGS="' + flag + '"')
            self.assertEqual(self.dispatch("alloc-slice-07-r1", "--dry-run").returncode, 2)

    def test_metrics_stay_in_writable_roots_and_thread_is_persisted(self):
        out = self.dispatch("alloc-slice-07-r1", "--wait")
        self.assertEqual(out.returncode, 0, out.stderr)
        metrics = self.root / ".run/codex/alloc-slice-07-r1/metrics"
        self.assertIn("METRICS=" + str(metrics), self.argv())
        self.assertIn("TIERS=" + str(metrics / "tiers.jsonl"), self.argv())
        roots = next(arg for arg in self.argv() if arg.startswith("sandbox_workspace_write.writable_roots="))
        self.assertNotIn("docs/process", roots)
        grants = json.loads(roots.split("=", 1)[1])
        gd = git(self.wt, "rev-parse", "--absolute-git-dir")
        self.assertEqual(grants, [gd, str(self.root / ".git/objects"),
                                 str(self.root / ".git/refs/heads/slice/07"), str(self.root / ".git/refs/heads/slice/07.lock"),
                                 str(self.root / ".git/logs/refs/heads/slice/07"), str(self.root / ".git/logs/refs/heads/slice/07.lock"),
                                 str(self.root / "outputs"), str(self.root / ".run")])
        self.assertEqual((self.root / ".run/codex/alloc-slice-07-r1.thread").read_text().strip(), "th-123")
        self.assertTrue((self.root / ".run/slice-07.pid").read_text().strip().isdigit())
        self.assertTrue((self.root / ".run/codex/alloc-slice-07-r1.pid").exists())

    def test_thread_and_pid_are_available_while_worker_is_running(self):
        env = self.environment(); env["FAKE_SLEEP"] = "2"
        child = subprocess.Popen(["sh", str(CODEX / "dispatch.sh"), "alloc-slice-07-r1", "--wait"], cwd=self.root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            thread = self.root / ".run/codex/alloc-slice-07-r1.thread"
            deadline = time.monotonic() + 15
            while not thread.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertEqual(thread.read_text().strip(), "th-123")
            self.assertIsNone(child.poll())
            pid = int((self.root / ".run/slice-07.pid").read_text())
            os.kill(pid, 0)
        finally:
            child.communicate(timeout=20)

    def test_profile_contains_pre_handoff_requirement(self):
        out = self.agents("show", "slice-implementer", "instructions")
        self.assertEqual(out.returncode, 0)
        self.assertIn("Before every HOLD or CANDIDATE", out.stdout)
        self.assertIn("SW_PREHANDOFF_CMD", out.stdout)
        self.assertIn("database-free tests", out.stdout)


class GateRunner(Project):
    def setUp(self):
        super().setUp()
        self.run_dir = self.root / ".run/codex/alloc-slice-07-r1"
        self.run_dir.mkdir(parents=True)
        verify = self.root / "scripts/dev/verify-slice.sh"
        verify.parent.mkdir(parents=True)
        verify.write_text('''#!/bin/sh\nmkdir "$SW_ROOT/.run/test-slot" || exit 5\ntrap 'rmdir "$SW_ROOT/.run/test-slot"' EXIT\nprintf "%s\\n" "$@" >> "$SW_ROOT/gate-args"\necho RESULT=pass\n''')
        verify.chmod(0o755)
        self.req = {"request_id": "probe-1", "allocation": "alloc-slice-07-r1", "slice": "slice-07", "tier": "t1", "head": git(self.wt, "rev-parse", "HEAD")}

    def request(self, **updates):
        (self.run_dir / "gate-request.json").write_text(json.dumps({**self.req, **updates}))

    def runner(self, env=None):
        return subprocess.run(["sh", str(CODEX / "gate-runner.sh"), "alloc-slice-07-r1"], cwd=self.root, env=env or self.environment(), capture_output=True, text=True)

    def result(self):
        return json.loads((self.run_dir / "gate-result.json").read_text())

    def test_host_runner_runs_configured_verifier_with_slot_and_writes_receipt(self):
        self.request()
        out = self.runner(); self.assertEqual(out.returncode, 0, out.stderr)
        result = self.result()
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("RESULT=pass", pathlib.Path(result["log"]).read_text())
        self.assertEqual((self.root / "gate-args").read_text().splitlines(), ["--cwd", str(self.wt), "--slice", "slice-07", "--base", self.req["head"], "t1"])
        self.assertFalse((self.root / ".run/test-slot").exists())
        rows = (self.run_dir / "metrics/tiers.jsonl").read_text().splitlines()
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0])["head_full"], self.req["head"])
        before = (self.root / "gate-args").read_text()
        self.request(); self.assertEqual(self.runner().returncode, 0)
        self.assertEqual((self.root / "gate-args").read_text(), before, "a repeated request ran twice")
        self.assertEqual(self.result()["result"], "pass")

    def test_request_cannot_select_command_slice_stale_head_or_tier(self):
        for changes in ({"command": "touch /tmp/forbidden"}, {"slice": "other"}, {"head": "0" * 40}, {"tier": "t3"}):
            self.request(**changes)
            out = self.runner()
            self.assertNotEqual(out.returncode, 0, changes)
            self.assertEqual(self.result()["result"], "NOT_RUN")
            self.assertFalse((self.root / "gate-args").exists())

    def test_stopped_or_sandboxed_runner_does_not_execute(self):
        self.request()
        (self.root / "docs/process/STOP").touch()
        self.assertNotEqual(self.runner().returncode, 0)
        self.assertEqual(self.result()["result"], "NOT_RUN")
        env = self.environment(); env["SW_ROLE"] = "slice-implementer"
        self.assertEqual(self.runner(env).returncode, 2)
        self.assertFalse((self.root / "gate-args").exists())

    def test_nonzero_exit_or_missing_pass_cannot_pass(self):
        verify = self.root / "scripts/dev/verify-slice.sh"
        for i, body in enumerate(("echo RESULT=pass; exit 1", "echo RESULT=fail", "echo no-result")):
            verify.write_text('#!/bin/sh\n' + body + '\n')
            self.request(request_id='failed-' + str(i))
            self.assertNotEqual(self.runner().returncode, 0)
            self.assertEqual(self.result()["result"], "fail")

    def test_reused_request_id_with_different_head_is_refused(self):
        self.request(); self.assertEqual(self.runner().returncode, 0)
        self.request(head="a" * 40)
        self.assertNotEqual(self.runner().returncode, 0)
        self.assertEqual(self.result()["result"], "NOT_RUN")
        self.assertIn("already used", self.result()["error"])

    def test_telemetry_write_failure_never_returns_pass(self):
        metrics = self.run_dir / "metrics"; metrics.mkdir()
        (metrics / "tiers.jsonl").mkdir()  # A failed append after a successful child must fail closed.
        self.request()
        self.assertNotEqual(self.runner().returncode, 0)
        self.assertEqual(self.result()["result"], "fail")
        self.assertIn("error", self.result())
        self.assertTrue(pathlib.Path(self.result()["log"]).read_text().rstrip().endswith("RESULT=fail"))

    def test_tracked_worktree_changes_are_not_verified_as_the_committed_head(self):
        (self.wt / "source").write_text("before")
        git(self.wt, "add", "source"); git(self.wt, "commit", "-qm", "source")
        self.req["head"] = git(self.wt, "rev-parse", "HEAD")
        (self.wt / "source").write_text("after")
        self.request()
        self.assertNotEqual(self.runner().returncode, 0)
        self.assertEqual(self.result()["result"], "NOT_RUN")
        self.assertFalse((self.root / "gate-args").exists())

    def test_stale_active_gate_requires_inspection_and_is_preserved(self):
        active = self.run_dir / "gate-active.json"; active.write_text("previous gate")
        self.request()
        self.assertNotEqual(self.runner().returncode, 0)
        self.assertEqual(active.read_text(), "previous gate")
        self.assertTrue((self.run_dir / "gate-request.json").exists())
        self.assertEqual(self.result()["result"], "NOT_RUN")
        self.assertFalse((self.root / "gate-args").exists())

    def test_supervisor_drains_request_after_worker_exits(self):
        req = self.root / "fake-request.json"; req.write_text(json.dumps(self.req))
        env = self.environment(); env.update(FAKE_GATE_REQUEST=str(req), FAKE_GATE_NO_WAIT="1")
        out = subprocess.run(["sh", str(CODEX / "dispatch.sh"), "alloc-slice-07-r1", "--wait"], cwd=self.root, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.result()["result"], "pass")

    def test_dispatch_supervisor_services_gate_without_model(self):
        req = self.root / "fake-request.json"; req.write_text(json.dumps(self.req))
        env = self.environment(); env["FAKE_GATE_REQUEST"] = str(req)
        out = subprocess.run(["sh", str(CODEX / "dispatch.sh"), "alloc-slice-07-r1", "--wait"], cwd=self.root, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.result()["result"], "pass")


if __name__ == "__main__":
    unittest.main()
