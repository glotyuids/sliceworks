#!/usr/bin/env python3
# sliceworks 0.8.0. The plugin's agent profiles (agents/*.md) rendered for Codex, and the parity check (method 10,
# "Two runtimes": the profiles are the source, a sync renders them, T0 fails on drift).
#
#   agents.py sync  [--root <project>]          write <project>/.codex/agents/<role>.toml for every native role
#   agents.py check [--root <project>]          exit 1 and name each file that is missing, stale or extra (the stamp
#                                               line is not compared, so a package release alone is not drift)
#   agents.py show <role> instructions|model|effort|sandbox [--root <project>]   one field, for dispatch.sh
#
# Models: a profile's Claude model class maps to SW_CODEX_MODEL_STRONG (opus, fable) or SW_CODEX_MODEL (the rest) from
# the project's .sliceworks/config.env; an empty value leaves the key out, so the agent inherits the session's
# default_subagent_model. Effort maps onto Codex's model_reasoning_effort (max becomes xhigh).
# The slice implementer is not rendered as a native subagent: a native subagent shares the parent's checkout and
# sandbox, and an implementer needs its own worktree, so it always runs as a worker process (dispatch.sh).
import argparse, json, pathlib, re, subprocess, sys

PKG = pathlib.Path(__file__).resolve().parents[3]
STAMP = "# sliceworks {version}, generated from agents/{name}.md by scripts/runtimes/codex/agents.py; edit the source, not this file"
PROCESS_ONLY = {"slice-implementer"}
READ_ONLY = {"business-analyst", "system-analyst", "code-reviewer", "named-risk-reviewer", "code-explorer"}
STRONG = {"opus", "fable"}
EFFORT = {"low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh", "max": "xhigh"}


def version():
    return re.search(r'"version":\s*"([^"]+)"', (PKG / ".claude-plugin" / "plugin.json").read_text()).group(1)


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise SystemExit(f"{path}: no front matter")
    meta, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"\s+-\s", line) and key:
            meta.setdefault(key, []).append(line.split("-", 1)[1].strip())
        elif ":" in line and not line.startswith(" "):
            key, value = (s.strip() for s in line.split(":", 1))
            meta[key] = value if value else []
    return meta, m.group(2).strip() + "\n"


def config(root):
    cfg, f = {}, root / ".sliceworks" / "config.env"
    if f.exists():
        for line in f.read_text().splitlines():
            m = re.match(r"\s*([A-Z_][A-Z0-9_]*)=(\"[^\"]*\"|'[^']*'|[^\s#]*)", line)
            if m:
                cfg[m.group(1)] = m.group(2).strip("\"'")
    return cfg


def project_root(arg):
    if arg:
        return pathlib.Path(arg).resolve()
    try:
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return pathlib.Path(common).parent
    except (subprocess.CalledProcessError, FileNotFoundError):
        return pathlib.Path.cwd()


def toml_str(s):
    if "'''" not in s:
        return "'''\n" + s + "'''"
    return '"""\n' + s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"') + '"""'


def fields(meta, cfg):
    model = cfg.get("SW_CODEX_MODEL_STRONG" if meta.get("model") in STRONG else "SW_CODEX_MODEL", "")
    effort = EFFORT.get(str(meta.get("effort", "")), "")
    sandbox = "read-only" if meta["name"] in READ_ONLY else "workspace-write"
    return model, effort, sandbox


def render(path, cfg, ver):
    meta, body = frontmatter(path)
    model, effort, _ = fields(meta, cfg)
    lines = [STAMP.format(version=ver, name=meta["name"]), f'name = "{meta["name"]}"',
             f"description = {json.dumps(meta['description'], ensure_ascii=False)}"]
    if model:
        lines.append(f'model = "{model}"')
    if effort:
        lines.append(f'model_reasoning_effort = "{effort}"')
    lines.append(f"developer_instructions = {toml_str(body)}")
    return meta["name"], "\n".join(lines) + "\n"


def expected(root):
    cfg, ver, out = config(root), version(), {}
    for path in sorted((PKG / "agents").glob("*.md")):
        name, text = render(path, cfg, ver)
        if name not in PROCESS_ONLY:
            out[f"{name}.toml"] = text
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["sync", "check", "show"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--root")
    a = ap.parse_args()
    root = project_root(a.root)
    if a.cmd == "show":
        if len(a.args) != 2:
            raise SystemExit("usage: agents.py show <role> instructions|model|effort|sandbox")
        role, what = a.args
        path = PKG / "agents" / f"{role.split(':')[-1]}.md"
        if not path.exists():
            raise SystemExit(f"unknown role {role}")
        meta, body = frontmatter(path)
        model, effort, sandbox = fields(meta, config(root))
        print({"instructions": body.rstrip("\n"), "model": model, "effort": effort, "sandbox": sandbox}[what])
        return 0
    want, d = expected(root), root / ".codex" / "agents"
    have = {p.name: p.read_text() for p in d.glob("*.toml")} if d.is_dir() else {}
    ours = {n for n, t in have.items() if t.startswith("# sliceworks ")}
    if a.cmd == "sync":
        d.mkdir(parents=True, exist_ok=True)
        for name, text in want.items():
            if have.get(name) != text:
                (d / name).write_text(text)
                print(f"wrote .codex/agents/{name}")
        for name in sorted(ours - set(want)):
            (d / name).unlink()
            print(f"removed .codex/agents/{name}")
        return 0
    drift = [f"MISSING .codex/agents/{n}" for n in want if n not in have]
    body = lambda t: t.split("\n", 1)[1] if "\n" in t else ""   # the stamp line carries the version; parity is the content
    drift += [f"STALE .codex/agents/{n}" for n in want if n in have and body(have[n]) != body(want[n])]
    drift += [f"EXTRA .codex/agents/{n}" for n in sorted(ours - set(want))]
    for line in drift:
        print(line)
    if drift:
        print("agents: drift; run scripts/runtimes/codex/agents.py sync")
        return 1
    print(f"agents: {len(want)} in parity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
