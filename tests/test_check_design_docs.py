# sliceworks 0.2.0. Tests for scripts/check-design-docs.py: each lint turns red on its failure and stays green otherwise.
import importlib.util, os, pathlib, subprocess, tempfile, unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cdd", HERE.parent / "scripts" / "check-design-docs.py")
cdd = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(cdd)


def run(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)


class DesignDocLints(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = pathlib.Path(self.tmp.name)
        run(self.root, "init", "-q"); run(self.root, "config", "user.email", "t@t"); run(self.root, "config", "user.name", "t")
        (self.root / "docs/process").mkdir(parents=True); (self.root / "specs").mkdir()
        (self.root / "docs/process/ARCHITECTURE.md").write_text("# Architecture\n\n## 1\nbase\n")
        (self.root / "docs/process/INDEX.md").write_text("| file | governs | status | last reviewed | notes |\n|---|---|---|---|---|\n| ARCHITECTURE.md | design | current | 2026-10-01 | |\n")
        (self.root / "specs/events-1.md").write_text("---\nstatus: frozen\n---\n# Events 1\nno todo here\n")
        run(self.root, "add", "-A"); run(self.root, "commit", "-qm", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def lint(self, **kw):
        args = ["--root", str(self.root), "--base", "HEAD~1", "--today", kw.pop("today", "2026-10-12")]
        for k, v in kw.items():
            args += [f"--{k.replace('_', '-')}", str(v)]
        return cdd.main(args)

    def test_clean_tree_passes(self):
        (self.root / "README.md").write_text("x"); run(self.root, "add", "-A"); run(self.root, "commit", "-qm", "unrelated")
        self.assertEqual(self.lint(), 0)

    def test_architecture_change_without_decision_fails(self):
        (self.root / "docs/process/ARCHITECTURE.md").write_text("# Architecture\n\n## 1\nchanged\n")
        run(self.root, "add", "-A"); run(self.root, "commit", "-qm", "edit architecture")
        self.assertEqual(self.lint(), 1)

    def test_architecture_change_citing_decision_in_lines_passes(self):
        (self.root / "docs/process/ARCHITECTURE.md").write_text("# Architecture\n\n## 1 (D-012)\nchanged\n")
        run(self.root, "add", "-A"); run(self.root, "commit", "-qm", "edit architecture")
        self.assertEqual(self.lint(), 0)

    def test_architecture_change_citing_decision_in_message_passes(self):
        (self.root / "docs/process/ARCHITECTURE.md").write_text("# Architecture\n\n## 1\nchanged\n")
        run(self.root, "add", "-A"); run(self.root, "commit", "-qm", "edit architecture per D-7")
        self.assertEqual(self.lint(), 0)

    def test_uncommitted_architecture_change_is_checked(self):
        (self.root / "docs/process/ARCHITECTURE.md").write_text("# Architecture\n\n## 1\nworking tree edit\n")
        self.assertEqual(self.lint(), 1)

    def test_stale_index_row_fails(self):
        self.assertEqual(self.lint(today="2026-12-01"), 1)
        self.assertEqual(self.lint(today="2026-12-01", limit_days=90), 0)

    def test_frozen_spec_with_todo_fails(self):
        (self.root / "specs/events-1.md").write_text("---\nstatus: frozen\n---\n# Events 1\nTODO decide\n")
        self.assertEqual(self.lint(), 1)
        (self.root / "specs/events-1.md").write_text("---\nstatus: draft\n---\n# Events 1\nTODO decide\n")
        self.assertEqual(self.lint(), 0)


if __name__ == "__main__":
    unittest.main()
