---
name: update
description: Bring a project's installed sliceworks files up to the package's current version - compare every stamped file (config, templates, rules, scripts, skills copies) with the package, replace stale ones wholesale, never overwrite hand-modified ones, and report new configuration keys the project must fill. Use when the user says "update sliceworks", "bring the delivery process up to date", "check whether our sliceworks files are stale", or after a plugin update.
disable-model-invocation: true
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.4.0
---

# Update installed files

1. **Find what is installed.** Every file in the project carrying a `# sliceworks <version>` header or a `metadata.source: glotyuids/sliceworks` front matter: `.sliceworks/config.env`, `.claude/rules/sliceworks.md`, the scripts the package installed, `.agents/skills/*` copies, `.codex/` files. State files (`FEATURES.json`, `STATE.md`, briefs, retros) are the project's data and are never touched.
2. **Classify** each against `${CLAUDE_PLUGIN_ROOT}`: in sync (identical), stale (package version newer, content differs only by the package's changes), modified (same version, different content: hand-edited; do not overwrite, list it and ask whether to move the edit upstream), orphan (no longer shipped: report, remove only on confirmation).
3. **Replace stale files wholesale**, keeping the new stamp. For `config.env`, never replace: diff the template's keys against the project's file and append missing keys with their defaults and a `# new in <version>` comment.
4. **Read `CHANGELOG.md`** of the package for every version between the installed and the current one; tell the user what changed in substance and which new configuration keys or template sections the project must now fill.
5. **Report.** Updated (old → new), kept as modified and why, orphans, new keys to fill. Do not claim an update you did not perform.
