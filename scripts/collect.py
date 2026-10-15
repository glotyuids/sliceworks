#!/usr/bin/env python3
# sliceworks 0.8.2. The collector (method chapter 19): completion read from durable artifacts, never from a message.
#   collect.py --root <repo> [--state-dir docs/process] [--json]
# For every open or stopped allocation prints one line:
#   ALLOC <id> <STATE> <detail>
# States: RUNNING (a recorded pid is alive, or the latest tier log has no RESULT= yet), QUEUED (the queue marker exists:
# a legitimate wait for a shared resource), DONE (handoff present, its head equals the branch head, and the verification
# it names is proven by the log's last RESULT=pass and, when metrics/tiers.jsonl exists, a row for that head), BLOCKED or
# HOLD (from the handoff), STALE-HANDOFF (branch moved past the handoff head), CANDIDATE-UNVERIFIED (handoff claims a
# candidate but the evidence does not prove it), STOPPED-NO-HANDOFF (nothing runs and nothing was written),
# MISSING-WORKTREE. After the allocations it prints UNREGISTERED lines for worktrees, pid files and result-less logs
# that no open allocation owns, so an empty registry is never a clean report.
# Detection is read-only by default. --merge-worker-metrics imports staged rows as the coordinator; no message is sent.
import argparse, json, os, pathlib, re, subprocess, sys
import fcntl
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from safe_git import git_command


def git(cwd, *args):
    r = subprocess.run(git_command("-C", cwd, *args), capture_output=True, text=True, check=False)
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


def verification_proven(root, state_dir, h, head):
    """A handoff's claim is proven only by the log it names (last RESULT=pass) and, when the tiers file exists, a row for that head."""
    if h.get("verification_result") != "pass":
        return False, f"handoff verification {h.get('verification_result') or 'missing'}"
    log = h.get("verification_log")
    if not log:
        return False, "handoff names no log"
    lp = pathlib.Path(log); lp = lp if lp.is_absolute() else root / lp
    if not lp.exists():
        return False, f"log {log} not found"
    results = re.findall(r"^RESULT=(\w+)", lp.read_text(errors="ignore"), re.M)
    if not results or results[-1] != "pass":
        return False, f"log {log} ends with RESULT={results[-1] if results else 'none'}"
    tiers = root / state_dir / "metrics" / "tiers.jsonl"
    if tiers.exists() and head:
        rows = [json.loads(l) for l in tiers.read_text().splitlines() if l.strip()]
        match = [r for r in rows if head.startswith(str(r.get("head", "")) or "\0") or r.get("head_full") == head]
        if not match:
            return False, f"no tiers row for head {head[:8]}"
        if not any(r.get("result") == "pass" for r in match):
            return False, f"tiers rows for {head[:8]} are not pass"
    return True, f"{log} RESULT=pass"


def unregistered(root, state_dir, allocs, worktree_root, outputs_dir):
    """Evidence of work that no open allocation owns: linked worktrees (from git itself), live pid files, result-less logs."""
    owned_wt = {str((root / a["worktree"]).resolve()) if not pathlib.Path(a["worktree"]).is_absolute() else str(pathlib.Path(a["worktree"]).resolve()) for a in allocs}
    owned_pid = {(a.get("execution") or {}).get("pid_file") for a in allocs}
    owned_logs = {(a.get("execution") or {}).get("log_dir") for a in allocs}
    out = []
    main_wt = str(root.resolve())
    porcelain = git(root, "worktree", "list", "--porcelain") or ""
    for block in porcelain.split("\n\n"):
        lines = block.strip().splitlines()
        if not lines or not lines[0].startswith("worktree "):
            continue
        path = lines[0][len("worktree "):].strip()
        try:
            rp = str(pathlib.Path(path).resolve())
        except Exception:
            rp = path
        if rp == main_wt or rp in owned_wt:
            continue
        branch = next((l[len("branch refs/heads/"):] for l in lines if l.startswith("branch refs/heads/")), "detached")
        try:
            shown = str(pathlib.Path(rp).relative_to(root.resolve()))
        except ValueError:
            shown = rp
        out.append(("worktree", shown, branch))
    run = root / ".run"
    if run.is_dir():
        for pf in sorted(run.glob("*.pid")):
            rel = str(pf.relative_to(root))
            if rel not in owned_pid and pid_alive(pf):
                out.append(("pid", rel, "alive"))
    od = root / outputs_dir / "slices"
    if od.is_dir():
        for sd in sorted(p for p in od.iterdir() if p.is_dir()):
            rel = str(sd.relative_to(root))
            if rel in owned_logs:
                continue
            log, result = latest_log_result(root, rel)
            if log and result is None:
                out.append(("log", log, "no RESULT= yet"))
    return out


def assess(root, state_dir, alloc):
    wt = pathlib.Path(alloc["worktree"])
    wt = wt if wt.is_absolute() else root / wt
    if not wt.exists():
        return "MISSING-WORKTREE", f"{alloc['worktree']} does not exist"
    pid_file = (alloc.get("execution") or {}).get("pid_file")
    if pid_file and pid_alive(root / pid_file):
        return "RUNNING", f"pid in {pid_file} is alive"
    qm = (alloc.get("execution") or {}).get("queue_marker")
    if qm and (root / qm).exists():
        return "QUEUED", f"queue marker {qm} present: waiting for a shared resource"
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
        ok, why = verification_proven(root, state_dir, h, head)
        if ok:
            return "DONE", f"candidate at {head[:8]}, {why}"
        return "CANDIDATE-UNVERIFIED", f"candidate at {head[:8]}: {why}"
    return "STOPPED-NO-HANDOFF", f"handoff present but result unreadable: {res or 'none'}"


def merge_worker_metrics(root, state_dir, run_dir):
    """Coordinator-only opt-in import; preserve rows and make repeated collection idempotent."""
    target = root / state_dir / "metrics"
    target.mkdir(parents=True, exist_ok=True)
    merged = 0
    # Serialize coordinator imports so two collectors never duplicate a row.
    with (target / ".worker-merge.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for source in sorted((root / run_dir / "codex").glob("*/metrics/*.jsonl")):
            if source.is_symlink() or not re.fullmatch(r"[a-z][a-z0-9_-]*\.jsonl", source.name):
                raise ValueError(f"invalid worker metrics path: {source}")
            raw = source.read_text()
            # A running writer may be between writes; consume complete lines only.
            lines = raw.splitlines() if raw.endswith("\n") else raw.splitlines()[:-1]
            rows = [json.loads(line) for line in lines if line.strip()]
            if any(not isinstance(row, dict) for row in rows):
                raise ValueError(f"worker metrics must contain objects: {source}")
            dest = target / source.name
            if dest.is_symlink():
                raise ValueError(f"symlink metrics destination: {dest}")
            existing = {json.dumps(json.loads(line), sort_keys=True) for line in dest.read_text().splitlines() if line.strip()} if dest.exists() else set()
            with dest.open("a") as out:
                for row in rows:
                    key = json.dumps(row, sort_keys=True)
                    if key not in existing:
                        out.write(json.dumps(row) + "\n")
                        existing.add(key)
                        merged += 1
    return merged


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--state-dir", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--merge-worker-metrics", action="store_true", help="coordinator: import staged worker rows before assessing allocations")
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
    worktree_root, outputs_dir, run_dir = ".claude/worktrees", "outputs", ".run"
    cfg = root / ".sliceworks" / "config.env"
    if cfg.exists():
        t = cfg.read_text()
        m = re.search(r"^SW_WORKTREE_ROOT=(\S+)", t, re.M); worktree_root = m.group(1).strip('"') if m else worktree_root
        m = re.search(r"^SW_OUTPUTS_DIR=(\S+)", t, re.M); outputs_dir = m.group(1).strip('"') if m else outputs_dir
        m = re.search(r"^SW_RUN_DIR=(\S+)", t, re.M); run_dir = m.group(1).strip('"') if m else run_dir
    if a.merge_worker_metrics:
        if os.environ.get("SW_ROLE"):
            raise SystemExit("collect: only the coordinator merges worker metrics")
        merge_worker_metrics(root, state_dir, run_dir)
    adir = root / state_dir / "allocations"
    rows = []; open_allocs = []
    for f in sorted(adir.glob("*.json")) if adir.is_dir() else []:
        try:
            alloc = json.loads(f.read_text())
        except Exception as e:
            rows.append({"id": f.stem, "state": "UNREADABLE", "detail": str(e)}); continue
        if alloc.get("state") in ("closed", "collected"):
            continue
        open_allocs.append(alloc)
        state, detail = assess(root, state_dir, alloc)
        w = alloc.get("worker") or {}; ex = alloc.get("execution") or {}
        rows.append({"id": alloc["id"], "slice": alloc.get("slice"), "role": alloc.get("role"), "state": state, "detail": detail,
                     "chat": w.get("chat_id"), "session": ex.get("session_id") or w.get("id")})
    extra = unregistered(root, state_dir, open_allocs, worktree_root, outputs_dir)
    if a.json:
        print(json.dumps({"allocations": rows, "unregistered": [{"kind": k, "path": p, "detail": x} for k, p, x in extra]}, indent=2))
    else:
        for r in rows:
            ids = " ".join(f"{k}={v}" for k, v in (("chat", r.get("chat")), ("session", r.get("session"))) if v)
            print(f"ALLOC {r['id']} {r['state']} {r['detail']}{(' [' + ids + ']') if ids else ''}")
        if not rows:
            print("ALLOC none open")
        for k, p, x in extra:
            print(f"UNREGISTERED {k} {p} {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
