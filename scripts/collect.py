#!/usr/bin/env python3
# sliceworks 0.5.0. The collector (method chapter 19): completion read from durable artifacts, never from a message.
#   collect.py --root <repo> [--state-dir docs/process] [--json]
# For every open or stopped allocation prints one line:
#   ALLOC <id> <STATE> <detail>
# States: RUNNING (a recorded pid is alive, or the latest tier log has no RESULT= yet), DONE (handoff present, its head
# equals the branch head, its verification passed), BLOCKED or HOLD (from the handoff), STALE-HANDOFF (branch moved
# past the handoff head), STOPPED-NO-HANDOFF (nothing runs and nothing was written), MISSING-WORKTREE.
# Detection only; nothing is written and no message is sent.
import argparse, json, os, pathlib, re, subprocess, sys


def git(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def pid_alive(path):
    try:
        pid = int(pathlib.Path(path).read_text().strip())
    except Exception:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def parse_handoff(text):
    if not text.startswith("---"):
        return {}
    fm = text.split("---", 2)[1]
    out = {}
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    v = out.get("verification", "")
    m = re.search(r"result:\s*(pass|fail|NOT_RUN)", v)
    out["verification_result"] = m.group(1) if m else None
    m = re.search(r"log:\s*([^,}]+)", v)
    out["verification_log"] = m.group(1).strip() if m else None
    return out


def latest_log_result(root, log_dir):
    if not log_dir:
        return None, None
    d = root / log_dir
    if not d.is_dir():
        return None, None
    logs = sorted(d.glob("t*-*.log"), key=lambda p: p.stat().st_mtime)
    if not logs:
        return None, None
    text = logs[-1].read_text(errors="ignore")
    m = re.findall(r"^RESULT=(\w+)", text, re.M)
    return str(logs[-1].relative_to(root)), (m[-1] if m else None)


def assess(root, state_dir, alloc):
    wt = pathlib.Path(alloc["worktree"])
    wt = wt if wt.is_absolute() else root / wt
    if not wt.exists():
        return "MISSING-WORKTREE", f"{alloc['worktree']} does not exist"
    pid_file = (alloc.get("execution") or {}).get("pid_file")
    if pid_file and pid_alive(root / pid_file):
        return "RUNNING", f"pid in {pid_file} is alive"
    log_dir = (alloc.get("execution") or {}).get("log_dir")
    log, result = latest_log_result(root, log_dir)
    if log and result is None:
        return "RUNNING", f"{log} has no RESULT= yet"
    head = git(wt, "rev-parse", "HEAD")
    handoff_rel = f"{state_dir}/handoffs/{alloc['id']}.md"
    handoff_path = wt / handoff_rel
    if not handoff_path.exists():
        handoff_path = root / handoff_rel
    if not handoff_path.exists():
        return "STOPPED-NO-HANDOFF", f"no process, no {handoff_rel}; branch head {head[:8] if head else '?'}"
    h = parse_handoff(handoff_path.read_text(errors="ignore"))
    if h.get("head") and head and h["head"] != head:
        return "STALE-HANDOFF", f"handoff head {h['head'][:8]} but branch head {head[:8]}"
    res = (h.get("result") or "").upper()
    if res in ("BLOCKED", "HOLD"):
        return res, f"handoff {handoff_rel}: {h.get('verification_result') or 'no verification'}"
    if res == "CANDIDATE":
        if h.get("verification_result") == "pass":
            return "DONE", f"candidate at {head[:8]}, {h.get('verification_log') or 'log unnamed'} pass"
        return "STOPPED-NO-HANDOFF" if not h else "CANDIDATE-UNVERIFIED", f"candidate at {head[:8]} with verification {h.get('verification_result') or 'missing'}"
    return "STOPPED-NO-HANDOFF", f"handoff present but result unreadable: {res or 'none'}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--state-dir", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    state_dir = a.state_dir
    if state_dir is None:
        state_dir = "docs/process"
        cfg = root / ".sliceworks" / "config.env"
        if cfg.exists():
            m = re.search(r"^SW_STATE_DIR=(\S+)", cfg.read_text(), re.M)
            if m:
                state_dir = m.group(1).strip('"')
    adir = root / state_dir / "allocations"
    rows = []
    for f in sorted(adir.glob("*.json")) if adir.is_dir() else []:
        try:
            alloc = json.loads(f.read_text())
        except Exception as e:
            rows.append({"id": f.stem, "state": "UNREADABLE", "detail": str(e)}); continue
        if alloc.get("state") in ("closed", "collected"):
            continue
        state, detail = assess(root, state_dir, alloc)
        rows.append({"id": alloc["id"], "slice": alloc.get("slice"), "role": alloc.get("role"), "state": state, "detail": detail})
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(f"ALLOC {r['id']} {r['state']} {r['detail']}")
        if not rows:
            print("ALLOC none open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
