# Changelog

Versions are the marketplace version (`metadata.version` in `.claude-plugin/marketplace.json`).
Each plugin also has its own version; see the plugin table in each entry.

## 0.2.1

- Groundwork 0.2.1: idempotent re-runs, verified end to end in a live Claude Code session
  (re-run with no new facts writes nothing; new facts update the existing section in place;
  user edits outside markers are kept).
- `init` no longer writes timings or other volatile details into AGENTS.md.
- `init` runs the detector and each verified command as single plain commands, avoiding
  extra permission prompts.
- `skill` checks existing skills by name and purpose and updates in place instead of
  creating duplicates.

## 0.2.0

- 11 department plugins with 111 agents, generated from `catalog/*.toml` by `tools/build.py`.
- Shared loop harness (plan, act, verify, reflect) with budgets, stop rules, and an evidence report in every agent.
- Handoff graph and catalog docs; `git-subdir` snippets for other marketplaces.
- Groundwork 0.2.0: `init` recommends up to 3 agent departments.
- Release tooling: version gate, bump helper, plugin smoke test in a real Claude Code CLI, auto-release on green CI.

## 0.1.0

- Groundwork 0.1.0: `init`, `skill`, and `audit` skills with 2-3 word why-tag lessons, plus a stack detector.
