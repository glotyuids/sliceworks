#!/usr/bin/env sh
# sliceworks 0.6.1. Release the package: one command instead of six.
#   scripts/release.sh <version> ["<one-line summary for the commit>"] [--no-push] [--marketplace <path-to-engineering-skills>]
# Steps: the CHANGELOG must already carry a "## <version>" section (write the entry first; the script refuses otherwise);
# bumps .claude-plugin/plugin.json and the README status prefix; runs the hook tests, the Python tests and the strict
# validator; commits; tags v<version>; pushes with tags. With --marketplace, also bumps the sliceworks entry version in the
# library's marketplace.json, commits and pushes there, so the listing matches (the plugin's own manifest is what installs).
# Users then get the new version by `claude plugin update sliceworks@engineering-skills`, or automatically when the
# marketplace entry in their settings has autoUpdate: true.
set -eu
here="$(cd "$(dirname "$0")/.." && pwd)"; cd "$here"
version="${1:-}"; [ -n "$version" ] || { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
shift; summary=""; push=1; market=""
while [ $# -gt 0 ]; do case "$1" in --no-push) push=0; shift;; --marketplace) market="${2:-}"; shift 2;; *) summary="$1"; shift;; esac; done
printf '%s' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "error: version must be MAJOR.MINOR.PATCH" >&2; exit 1; }
grep -q "^## $version" CHANGELOG.md || { echo "error: CHANGELOG.md has no '## $version' section; write the entry first" >&2; exit 1; }
# Preflight against the remote before anything is modified: another session may have released from this checkout.
git fetch -q --tags origin 2>/dev/null || echo "note: could not fetch origin; checking local state only"
git rev-parse -q --verify "refs/tags/v$version" >/dev/null 2>&1 && { echo "error: tag v$version already exists (locally or on origin); pick the next version" >&2; exit 1; }
behind="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"; [ "$behind" = 0 ] || { echo "error: this checkout is $behind commit(s) behind origin/main; pull or rebase first" >&2; exit 1; }
current="$(python3 -c 'import json; print(json.load(open(".claude-plugin/plugin.json"))["version"])')"
[ "$current" != "$version" ] || { echo "error: the manifest is already at $version; another release used this number" >&2; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no | grep -v '^ M CHANGELOG.md$' | grep -v '^M  CHANGELOG.md$' || true)" ] || echo "note: releasing with uncommitted changes in the tree; they will be included"
python3 - "$version" <<'PY'
import json,re,sys
v=sys.argv[1]
p='.claude-plugin/plugin.json'; m=json.load(open(p)); old=m['version']; m['version']=v; json.dump(m,open(p,'w'),indent=2); open(p,'a').write('\n')
r=open('README.md').read(); r2=re.sub(r'^(\d+\.\d+\.\d+):', v+':', r, count=1, flags=re.M)
if r2!=r: open('README.md','w').write(r2)
print(f"version {old} -> {v}")
PY
echo "== tests =="; sh tests/test_hooks.sh | grep -E 'FAIL|tests:'; python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | grep -E '^(Ran|OK|FAILED|ERROR)'
python3 -m unittest discover -s tests -p 'test_*.py' >/dev/null 2>&1 || { echo "error: tests failed" >&2; exit 1; }
sh tests/test_hooks.sh >/dev/null 2>&1 || { echo "error: hook tests failed" >&2; exit 1; }
echo "== validate =="; claude plugin validate --strict . | tail -1 | grep -q passed || { echo "error: validation failed" >&2; exit 1; }
git add -A
git commit -q -m "$version: ${summary:-release}" -m "$(awk -v v="## $version" '$0==v{f=1;next} /^## /{if(f)exit} f' CHANGELOG.md | sed '/^$/d' | head -20)" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git tag -a "v$version" -m "sliceworks $version"
echo "committed $(git rev-parse --short HEAD), tagged v$version"
if [ "$push" -eq 1 ]; then git push -q && git push -q --tags && echo "pushed main and v$version"; fi
if [ -n "$market" ]; then
  python3 - "$market" "$version" <<'PY'
import json,sys,os
p=os.path.join(sys.argv[1],'.claude-plugin','marketplace.json'); m=json.load(open(p))
for e in m['plugins']:
    if e['name']=='sliceworks': e['version']=sys.argv[2]
json.dump(m,open(p,'w'),indent=2,ensure_ascii=False); open(p,'a').write('\n'); print('marketplace entry ->', sys.argv[2])
PY
  ( cd "$market" && git add .claude-plugin/marketplace.json && git commit -q -m "Marketplace: sliceworks $version" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && [ "$push" -eq 1 ] && git push -q && echo "marketplace pushed" ) || echo "marketplace: nothing to commit or push skipped"
fi
echo "Users update with: claude plugin update sliceworks@engineering-skills   (automatic when the marketplace has autoUpdate: true)"
