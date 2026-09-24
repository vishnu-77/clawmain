---
name: audit
description: Review the existing Claude Code setup in this repository (AGENTS.md, CLAUDE.md, .claude/skills) for bloat, vague or contradictory rules, stale or broken commands, and weak skill descriptions, and give a graded report where every finding carries a 2-3 word why-tag. Use when the user asks to check, review, audit, or improve their CLAUDE.md, AGENTS.md, or skills.
argument-hint: "[--fix]"
---

# Groundwork: audit

Grade the repo's current agent setup and teach the user what to improve. Read-only
unless the user passes `--fix` or approves fixes at the end.

Read `../init/references/why-tags.md`, `../init/references/agents-md-rubric.md`,
and `../skill/references/skill-rubric.md` first.

Arguments: `$ARGUMENTS`

## 1. Collect

Run `python ../init/scripts/detect.py <repo_root>` (from this skill's directory) and read
every file listed in `existing_agent_config`: AGENTS.md, CLAUDE.md, CLAUDE.local.md,
each `.claude/skills/*/SKILL.md`. If nothing exists, say so and offer `/groundwork:init`.

## 2. Check

**AGENTS.md / CLAUDE.md**
- Length: > 150 lines is bloat. `→ Why: context is budget`
- Commands: each one should exist in a manifest, CI, or script. Offer to run them to verify.
  Missing or failing: `→ Why: unverified, check`
- Style rules duplicating a configured linter/formatter. `→ Why: linter enforces it`
- Vague rules ("write good code", "be careful"). `→ Why: not actionable`
- Contradictions between files or sections. `→ Why: confuses agents`
- Missing essentials: test command, do-not-edit paths, gotchas. `→ Why: agents verify work` etc.
- Both files full of the same content instead of CLAUDE.md importing `@AGENTS.md`.
  `→ Why: single source`

**Skills**
- Description missing trigger words or only "helps with X". `→ Why: triggers auto-loading`
- No numbered steps or no done-check. `→ Why: predictable execution`
- Dangerous steps without a confirmation guardrail. `→ Why: avoids costly mistakes`
- Over ~150 lines with no `references/`. `→ Why: loads on demand`

## 3. Report

```
Groundwork audit: B  (7 findings)

AGENTS.md (182 lines)
  ✗ 182 lines, target ≤ 120              → Why: context is budget
  ✗ "npm run e2e" script not found        → Why: unverified, check
  ✗ 12 lines of formatting rules          → Why: linter enforces it
  ✓ clear do-not-edit list                → Why: prevents wasted edits
skills/release
  ✗ description lacks trigger words       → Why: triggers auto-loading
```

Grade: A (0-1 minor), B (a few fixable issues), C (missing essentials or broken commands),
D (contradictory or mostly generic). List worst issues first. Include what is good too;
beginners learn from both.

## 4. Fix (optional)

Offer to apply fixes. With `--fix` or approval, show diffs for each file and apply only
approved ones. Preserve user content outside `groundwork` markers unless the user
approves a change to it. End with a 2-line "What you learned" recap.
