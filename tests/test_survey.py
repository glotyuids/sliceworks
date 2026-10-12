# sliceworks 0.3.0. The survey detects what a project has and the dispatcher picks the next skill from it.
import importlib.util, io, json, os, pathlib, tempfile, unittest, contextlib

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("survey", HERE.parent / "scripts" / "survey.py")
survey = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(survey)


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        survey.main(list(args))
    return buf.getvalue()


class Survey(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def adopt(self, state="docs/process"):
        (self.root / ".sliceworks").mkdir(); (self.root / ".sliceworks/config.env").write_text(f"SW_PROFILE=lite\nSW_STATE_DIR={state}\n")
        (self.root / state).mkdir(parents=True)
        s = self.root / state / "SURVEY.md"; s.write_text("# Survey\n")
        os.utime(s, None)

    def test_blank_project_needs_adopt(self):
        self.assertIn("NEXT=adopt", run("--root", str(self.root), "--next"))

    def test_adopted_without_survey_needs_survey(self):
        (self.root / ".sliceworks").mkdir(); (self.root / ".sliceworks/config.env").write_text("SW_STATE_DIR=docs/process\n")
        self.assertIn("NEXT=survey", run("--root", str(self.root), "--next"))

    def test_idea_only_goes_to_discover(self):
        self.adopt()
        self.assertIn("NEXT=discover", run("--root", str(self.root), "--next"))

    def test_existing_spec_kit_goes_to_prepare(self):
        self.adopt()
        (self.root / ".specify/memory").mkdir(parents=True); (self.root / ".specify/memory/constitution.md").write_text("x")
        (self.root / "specs/001-login").mkdir(parents=True); (self.root / "specs/001-login/spec.md").write_text("# Login\n")
        out = run("--root", str(self.root), "--next")
        self.assertIn("NEXT=prepare", out)
        rep = json.loads(run("--root", str(self.root), "--json"))
        self.assertTrue(rep["process_systems"]["spec_kit"]["present"]); self.assertEqual(len(rep["process_systems"]["spec_kit"]["features"]), 1)

    def test_openspec_detected(self):
        self.adopt()
        (self.root / "openspec/specs/auth").mkdir(parents=True); (self.root / "openspec/specs/auth/spec.md").write_text("## Requirements\n")
        (self.root / "openspec/changes/add-sso").mkdir(parents=True); (self.root / "openspec/changes/archive").mkdir()
        rep = json.loads(run("--root", str(self.root), "--json"))
        self.assertEqual(rep["process_systems"]["openspec"]["specs"], ["openspec/specs/auth/spec.md"]); self.assertEqual(rep["process_systems"]["openspec"]["changes"], ["add-sso"])
        self.assertEqual(rep["next"]["skill"], "prepare")

    def test_design_done_without_rows_goes_to_design_then_plan(self):
        self.adopt(); st = self.root / "docs/process"
        (st / "SPARK.md").write_text("x"); (st / "INVARIANTS.md").write_text("x"); (st / "ARCHITECTURE.md").write_text("x"); (st / "MILESTONES.md").write_text("x")
        (st / "SCENARIOS.json").write_text('[{"id":"A1"}]'); (st / "FEATURES.json").write_text("[]")
        self.assertIn("NEXT=design", run("--root", str(self.root), "--next"))
        (st / "FEATURES.json").write_text('[{"id":"AC-001","passes":false}]'); (st / "BACKLOG.md").write_text("x"); (st / "slices").mkdir()
        self.assertIn("NEXT=plan-increment", run("--root", str(self.root), "--next"))
        (st / "slices/slice-01-a.md").write_text("x"); (st / "STATE.md").write_text("## Slices\n| id | state |\n|---|---|\n| slice-01 | ready |\n")
        self.assertIn("NEXT=resume", run("--root", str(self.root), "--next"))
        (st / "FEATURES.json").write_text('[{"id":"AC-001","passes":true}]')
        self.assertIn("NEXT=accept", run("--root", str(self.root), "--next"))

    def test_stack_and_agent_config_detected(self):
        self.adopt()
        (self.root / "go.mod").write_text("module x\n"); (self.root / "Makefile").write_text("build:\n\ttrue\ntest:\n\ttrue\n")
        (self.root / "AGENTS.md").write_text("x"); (self.root / ".claude/agents").mkdir(parents=True); (self.root / ".claude/agents/go-reviewer.md").write_text("x")
        (self.root / "a_test.go").write_text("func TestAC001_Login(t *testing.T) {}\n")
        rep = json.loads(run("--root", str(self.root), "--json"))
        self.assertEqual(rep["stack"]["languages"], ["go"]); self.assertEqual(rep["stack"]["commands"]["make"], ["build", "test"])
        self.assertEqual(rep["stack"]["e2e_test_names"], ["TestAC001_Login"]); self.assertEqual(rep["agent_config"]["claude_agents"], ["go-reviewer"])
        md = run("--root", str(self.root), "--markdown")
        self.assertIn("## Phase coverage", md)


if __name__ == "__main__":
    unittest.main()
