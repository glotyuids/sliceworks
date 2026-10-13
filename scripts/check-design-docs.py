#!/usr/bin/env python3
# sliceworks 0.6.0. Design-document lints (method chapter 14), run from T0 in projects with living design documents.
#   1. A change to ARCHITECTURE.md since <base> cites a decision (D-<n>) in the added lines or in a commit message.
#   2. No current INDEX.md row is older than SW_REVIEW_LIMIT_DAYS (archived rows are history and exempt).
#   3. A frozen spec (front matter `status: frozen`) contains no TODO.
#   4. After the newest pivot decision (a D entry whose metadata line carries `pivot`), every current INDEX.md row
#      carries a last-reviewed date at or after it; archived rows are exempt.
#   5. No brief (slices/) or contract (contracts/) references an archived document (archive/<date>-<name>).
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


def index_rows(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.lower().startswith("| file"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0] or cells[0].startswith("<"):
            continue
        rows.append(cells)
    return rows


def check_index(root, state_dir, limit_days, today):
    path = root / state_dir / "INDEX.md"
    if not path.exists():
        return True, "index: no file"
    stale = []
    for cells in index_rows(path):
        if cells[2].lower().startswith("archived"):
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", cells[3])
        if not m:
            continue
        age = (today - dt.date.fromisoformat(m.group(1))).days
        if age > limit_days:
            stale.append(f"{cells[0]} ({age} d)")
    if stale:
        return False, "index: rows past the review limit: " + ", ".join(stale)
    return True, "index: every dated current row within the review limit"


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


PIVOT_MARK = re.compile(r"(^|·)\s*pivot\s*(·|$)")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
ARCHIVED_REF = re.compile(r"archive/\d{4}-\d{2}-\d{2}-[^\s)\]`'\"]+")


def latest_pivot(root, state_dir):
    """The newest D entry in DECISIONS.md whose metadata line (the first `- ` line after `### D-n`) carries `pivot`."""
    path = root / state_dir / "DECISIONS.md"
    if not path.exists():
        return None, None
    best, current = (None, None), None
    for line in path.read_text().splitlines():
        m = re.match(r"^###\s+(D-\d+)", line)
        if m:
            current = m.group(1)
            continue
        if current and line.startswith("- "):
            d = DATE.search(line)
            if PIVOT_MARK.search(line) and d:
                date = dt.date.fromisoformat(d.group(1))
                if best[1] is None or date > best[1]:
                    best = (current, date)
            current = None
    return best


def check_pivot_review(root, state_dir):
    path = root / state_dir / "INDEX.md"
    if not path.exists():
        return True, "pivot: no index"
    pid, pdate = latest_pivot(root, state_dir)
    if pid is None:
        return True, "pivot: no pivot decision recorded"
    unreviewed = []
    for cells in index_rows(path):
        if cells[2].lower().startswith("archived"):
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", cells[3])
        if not m or dt.date.fromisoformat(m.group(1)) < pdate:
            unreviewed.append(f"{cells[0]} ({m.group(1) if m else 'undated'})")
    if unreviewed:
        return False, f"pivot: current rows not reviewed since {pid} ({pdate}): " + ", ".join(unreviewed)
    return True, f"pivot: every current row reviewed since {pid} ({pdate})"


def check_archived_refs(root, state_dir):
    hits = []
    for sub in ("slices", "contracts"):
        d = root / state_dir / sub
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.md")):
            refs = sorted(set(ARCHIVED_REF.findall(f.read_text(errors="ignore"))))
            if refs:
                hits.append(f"{f.relative_to(root)} -> {', '.join(refs)}")
    if hits:
        return False, "archive: briefs or contracts reference archived documents: " + "; ".join(hits)
    return True, "archive: no brief or contract references an archived document"


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
    results = [check_architecture(root, a.state_dir, a.base), check_index(root, a.state_dir, a.limit_days, today), check_specs(root, a.specs),
               check_pivot_review(root, a.state_dir), check_archived_refs(root, a.state_dir)]
    ok = True
    for passed, msg in results:
        print(("ok   " if passed else "FAIL ") + msg)
        ok = ok and passed
    print("RESULT=" + ("pass" if ok else "fail"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
