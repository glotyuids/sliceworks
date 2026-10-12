#!/usr/bin/env python3
# sliceworks 0.2.0. Design-document lints (method chapter 14), run from T0 in projects with living design documents.
#   1. A change to ARCHITECTURE.md since <base> cites a decision (D-<n>) in the added lines or in a commit message.
#   2. No INDEX.md row is older than SW_REVIEW_LIMIT_DAYS.
#   3. A frozen spec (front matter `status: frozen`) contains no TODO.
# Usage: check-design-docs.py --root <repo> [--base <ref>] [--state-dir docs/process] [--limit-days 30] [--specs specs]
# Prints one line per check (ok/fail) and RESULT=pass|fail; exit 1 on fail.
import argparse, datetime as dt, pathlib, re, subprocess, sys

D_REF = re.compile(r"\bD-\d+\b")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False).stdout


def check_architecture(root, state_dir, base):
    path = f"{state_dir}/ARCHITECTURE.md"
    if not (root / path).exists():
        return True, "architecture: no file"
    changed = git(root, "diff", "--name-only", f"{base}...HEAD", "--", path).strip()
    if not changed:
        changed = git(root, "diff", "--name-only", "--", path).strip()
    if not changed:
        return True, "architecture: unchanged"
    added = git(root, "diff", f"{base}...HEAD", "--", path) + git(root, "diff", "--", path)
    added_lines = "\n".join(l[1:] for l in added.splitlines() if l.startswith("+") and not l.startswith("+++"))
    messages = git(root, "log", "--format=%s%n%b", f"{base}..HEAD", "--", path)
    if D_REF.search(added_lines) or D_REF.search(messages):
        return True, "architecture: change cites a decision"
    return False, "architecture: ARCHITECTURE.md changed without citing a decision (D-<n>) in the changed lines or a commit message"


def check_index(root, state_dir, limit_days, today):
    path = root / state_dir / "INDEX.md"
    if not path.exists():
        return True, "index: no file"
    stale = []
    for line in path.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.lower().startswith("| file"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0] or cells[0].startswith("<"):
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", cells[3])
        if not m:
            continue
        age = (today - dt.date.fromisoformat(m.group(1))).days
        if age > limit_days:
            stale.append(f"{cells[0]} ({age} d)")
    if stale:
        return False, "index: rows past the review limit: " + ", ".join(stale)
    return True, "index: every dated row within the review limit"


def check_specs(root, specs_dir):
    d = root / specs_dir
    if not d.is_dir():
        return True, "specs: no directory"
    bad = []
    for f in sorted(d.rglob("*.md")):
        text = f.read_text()
        fm = text.split("---", 2)[1] if text.startswith("---") and text.count("---") >= 2 else ""
        if re.search(r"^status:\s*frozen\s*$", fm, re.M) and "TODO" in text:
            bad.append(str(f.relative_to(root)))
    if bad:
        return False, "specs: frozen specs contain TODO: " + ", ".join(bad)
    return True, "specs: no frozen spec contains TODO"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="HEAD~1")
    ap.add_argument("--state-dir", default="docs/process")
    ap.add_argument("--limit-days", type=int, default=30)
    ap.add_argument("--specs", default="specs")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD, for tests")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    results = [check_architecture(root, a.state_dir, a.base), check_index(root, a.state_dir, a.limit_days, today), check_specs(root, a.specs)]
    ok = True
    for passed, msg in results:
        print(("ok   " if passed else "FAIL ") + msg)
        ok = ok and passed
    print("RESULT=" + ("pass" if ok else "fail"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
