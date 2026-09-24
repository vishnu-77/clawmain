---
name: groundwork
description: Guided Claude Code setup for this repository. Verifies build/test/lint commands, interviews the user briefly, and writes AGENTS.md plus a thin CLAUDE.md; can also turn a workflow into a skill or audit the existing setup. Every choice comes with a 2-3 word why-tag lesson. Use when the user wants to set up Claude Code for a project, create or improve AGENTS.md, CLAUDE.md or skills, or check their agent setup.
argument-hint: "[skill <name> | audit [--fix]] [--no-tags] [--dry-run]"
user-invocable: true
disable-model-invocation: true
---

# Groundwork

Request: `$ARGUMENTS`

Pick exactly one procedure from the request, read that file from this skill's
directory, and follow it completely. Do not read the other procedures.

| Request starts with | Procedure | Does |
|---|---|---|
| *(nothing)*, `init`, `setup`, or only flags | `procedures/init.md` | First setup, or an idempotent refresh if AGENTS.md already exists |
| `skill` | `procedures/skill.md` | Turn one repeated workflow into `.claude/skills/<name>/SKILL.md` |
| `audit` | `procedures/audit.md` | Grade the existing setup; `--fix` offers fixes |
| `help` or anything else | none | Show the table below and stop |

Pass along any flags (`--no-tags`, `--dry-run`, `--fix`) and, for `skill`, the workflow
name that follows it.

Help text:

```
/groundwork                 set up or refresh AGENTS.md + CLAUDE.md (safe to re-run)
/groundwork skill <name>    turn a repeated workflow into a skill
/groundwork audit [--fix]   grade your setup and suggest fixes
flags: --no-tags (lessons in chat only)  --dry-run (plan only, write nothing)
```

In every procedure the user-facing commands are `/groundwork`, `/groundwork skill <name>`,
and `/groundwork audit`. Never suggest `/groundwork:init` or other colon forms.
