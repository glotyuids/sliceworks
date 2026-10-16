#!/usr/bin/env python3
# sliceworks 0.7.0. The dashboard command (method chapter 9): rebuilds one self-contained HTML page from the state files.
#   python3 <dir>/dashboard --root <repo> [--out <file>] [--state-dir <dir>] [--now <iso>] [--no-history] [--open]
# Reads .sliceworks/config.env; exits 0 without writing when the project has not adopted sliceworks and no
# --state-dir is given. Writes the page atomically (default SW_DASHBOARD_OUT, else <state-dir>/dashboard.html) and
# appends one point to <run-dir>/progress-history.jsonl when the progress moved. No network, no model turn.
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):  # run as `python3 path/to/dashboard`: import the package by its directory name
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = Path(__file__).resolve().parent.name

from importlib import import_module

collect = import_module(f"{__package__}.collect")
compute = import_module(f"{__package__}.compute")
render = import_module(f"{__package__}.render")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dashboard", description="Rebuild the sliceworks dashboard page.")
    ap.add_argument("--root", default=".", help="repository root (default: the current directory)")
    ap.add_argument("--state-dir", help="state directory, overriding SW_STATE_DIR")
    ap.add_argument("--out", help="output file, overriding SW_DASHBOARD_OUT")
    ap.add_argument("--now", help="render as of this ISO time (tests and reproductions)")
    ap.add_argument("--no-history", action="store_true", help="do not read or append the progress history")
    ap.add_argument("--open", action="store_true", help="open the page after writing it (macOS open, xdg-open)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    cfg = collect.load_config(root)
    if not cfg and not a.state_dir:
        print("dashboard: no .sliceworks/config.env and no --state-dir; nothing to do")
        return 0
    state_dir = Path(a.state_dir).resolve() if a.state_dir else root / cfg.get("SW_STATE_DIR", "docs/process")
    out = Path(a.out) if a.out else (root / cfg["SW_DASHBOARD_OUT"] if cfg.get("SW_DASHBOARD_OUT") else state_dir / "dashboard.html")
    now = collect.parse_iso(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    if now is None:
        print(f"dashboard: --now {a.now!r} is not an ISO time", file=sys.stderr)
        return 2
    snap = collect.snapshot(root, cfg, state_dir)
    try:
        state_rel = state_dir.relative_to(root).as_posix()
    except ValueError:
        state_rel = state_dir.as_posix()
    snap["links"] = {"base": cfg.get("SW_DASHBOARD_LINK_BASE", ""), "state_rel": state_rel,
                     "page_to_root": Path(os.path.relpath(root, out.resolve().parent)).as_posix()}
    hist_file = root / cfg.get("SW_RUN_DIR", ".run") / "progress-history.jsonl"
    history = [] if a.no_history else collect.jsonl(hist_file)
    html = render.page(snap, now, history)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(f".{out.name}.tmp{os.getpid()}")
    tmp.write_text(html, encoding="utf-8")
    os.replace(tmp, out)
    if not a.no_history:
        incs = compute.increments(snap)
        try:
            cur = int(snap["increment"].get("current", "0") or 0)
        except ValueError:
            cur = 0
        per = compute.progress(snap, incs, cur)
        prog = 100 * sum(d for *_, d in per) / (sum(t for _, _, t, _ in per) or 1)
        if not history or abs(float(history[-1].get("p", 0)) - prog) > 0.05:
            try:
                hist_file.parent.mkdir(parents=True, exist_ok=True)
                with hist_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"t": now.isoformat(timespec="seconds"), "p": round(prog, 2)}) + "\n")
            except OSError:
                pass
    print(f"dashboard: {out}")
    if a.open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.run([opener, str(out)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
