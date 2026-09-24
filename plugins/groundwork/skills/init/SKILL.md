---
name: init
description: Guided Claude Code setup for the current repository. Detects the stack, verifies build/test/lint commands, interviews the user briefly, then writes AGENTS.md plus a thin CLAUDE.md, explaining every choice with a 2-3 word why-tag. Use when the user wants to set up Claude Code for a project, create or improve AGENTS.md or CLAUDE.md, or onboard a repo for AI agents.
argument-hint: "[--no-tags] [--dry-run]"
---

# Groundwork: init

You are guiding a beginner-to-intermediate user through setting up Claude Code for
this repository. The output is **verified**, **short**, and **teaches as it goes**:
every item you add, change, or skip gets a 2-3 word why-tag.

Read `references/why-tags.md` (in this skill's directory) before starting. Follow its
format and vocabulary exactly. Use `references/agents-md-rubric.md` for content rules
and `references/stack-hints.md` for per-stack details.

Arguments: `$ARGUMENTS`
- `--no-tags`: keep why-tags in chat but do not write them into files.
- `--dry-run`: stop after step 5 (show the plan and file previews, write nothing).

Tell the user up front, in one line, what will happen: detect, verify, a few questions,
a plan to approve, then files. Nothing is written without their approval.

## 1. Detect

Run the detector from this skill's directory against the repo root:

```
python scripts/detect.py <repo_root>
```

(Use `python3` if `python` is unavailable. If neither works, detect by reading
manifest files directly: package.json, pyproject.toml, go.mod, Cargo.toml, Makefile, CI files.)

Then read, briefly: the README's setup or development section, and the CI workflow
files listed in `ci`. CI is the best evidence of which commands matter.

Summarize for the user in 3-5 lines: stack, package manager, monorepo or not, and any
existing agent config found (`existing_agent_config`).

## 2. Verify commands

From `commands` plus what CI and the README show, pick the candidates for:
install, build, test, single test, lint, format, run.

- **Ask once** before running anything: list the commands and ask "OK to run these to
  check they work?" Skip `install` and `run`/`dev` (long-running) unless the user agrees.
- Run each approved command. Record: passed / failed / skipped, and rough duration.
- Never run anything that deploys, publishes, deletes data, or needs production credentials.
- Report results with tags, e.g.
  `✓ pnpm test (38 s)   → Why: agents verify work`
  `✗ make lint failed   → Why: unverified, omitted`

Only verified commands go into AGENTS.md as plain commands. Failed or skipped ones are
either omitted or marked `(unverified)` if the user wants them kept.

## 3. Interview

Ask **at most 5** short questions, in one message, numbered, all skippable.
Pick those that matter most for this repo; good defaults:

1. What do AI agents (or new teammates) most often get wrong here?
2. Any files or folders agents must never edit?
3. Any actions that need your approval first (migrations, deploys, dependency changes)?
4. Conventions not visible in the code (where new code goes, naming, commit style)?
5. What does "done" mean for a change here?

Use answers verbatim where possible. Do not invent conventions the user did not state
and the code does not show.

## 4. Handle existing files

- **AGENTS.md exists:** merge. Keep user content; add or refresh only
  `<!-- groundwork:begin X -->` / `<!-- groundwork:end X -->` sections. Tag: `keeps your edits`.
- **CLAUDE.md exists with real content:** do not overwrite. Propose moving shared
  content to AGENTS.md and leaving `@AGENTS.md` plus Claude-specific notes.
- **Neither exists:** create both.

## 5. Propose the plan

Show a compact plan before writing anything:

```
Plan
  AGENTS.md  (new, ~70 lines)
    ✓ commands: test, single test, lint      → Why: agents verify work
    ✓ project map (8 dirs)                    → Why: faster navigation
    ✓ do-not-edit: dist/, .env                → Why: prevents wasted edits
    ✓ gotchas (from your answers)             → Why: not in code
    ✗ style rules                             → Why: linter enforces it
  CLAUDE.md  (new, 3 lines, imports AGENTS.md) → Why: single source
  Next: /groundwork:skill for repeated workflows → Why: repeatable workflows
```

Then show the full AGENTS.md draft. Ask: "Write these files?" Wait for approval.
If `--dry-run`, stop here.

## 6. Write

Write AGENTS.md and CLAUDE.md at the repo root. Wrap Groundwork-owned sections in
managed markers. Unless `--no-tags`, put why-tags as HTML comments on section headers,
e.g. `## Commands <!-- why: agents verify work -->`.

## 7. Wrap up

End with:
- The files written and their line counts.
- A 3-line **"What you learned"** recap: the three most important why-tags from this run.
- Up to 2 suggested skills, based on workflows spotted in CI, the README, or interview
  answers (e.g. release, add a migration). Offer `/groundwork:skill <name>`.
- A reminder that `/groundwork:audit` can check the setup again later.
