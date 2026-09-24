# Groundwork

Guided Claude Code setup that teaches as it goes.

Groundwork detects your stack, **verifies** your build/test/lint commands by running
them, asks a few questions, and writes a short **AGENTS.md**, a thin **CLAUDE.md**
(`@AGENTS.md`), and **skills** for your repeated workflows.

Every choice comes with a 2-3 word lesson:

```
✓ AGENTS.md: test command   → Why: agents verify work
✓ CLAUDE.md → @AGENTS.md    → Why: single source
✓ skill description         → Why: triggers auto-loading
✗ skipped: style rules      → Why: linter enforces it
```

## Commands

One command: `/groundwork`.

| Command | What it does |
|---|---|
| `/groundwork` | First setup: detect, verify, interview, write AGENTS.md + CLAUDE.md. Safe to re-run: with no new facts it writes nothing |
| `/groundwork skill <name>` | Turn a repeated workflow into `.claude/skills/<name>/SKILL.md` (reuses an existing skill instead of duplicating it) |
| `/groundwork audit [--fix]` | Grade your existing setup and suggest fixes |

Flags: `--no-tags` keeps lessons in chat but out of files; `--dry-run` shows the plan
without writing.

## Install

```
/plugin marketplace add vishnu-77/clawmain
/plugin install groundwork@clawmain
```

## Safety

- Nothing is written without your approval; existing files are merged, not replaced.
- Commands are run only after you approve the list. Deploy/publish/destructive commands are never run.
- Groundwork-owned sections are wrapped in `<!-- groundwork:begin/end -->` markers so re-runs don't touch your edits.

## Requirements

Claude Code. Python 3.8+ for the stack detector (3.11+ for TOML-based hints); without
Python, Groundwork falls back to reading manifest files directly.
