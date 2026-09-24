---
name: skill
description: Interview the user about one repeatable workflow in their project and turn it into a well-formed Claude Code skill (.claude/skills/<name>/SKILL.md), explaining each part with a 2-3 word why-tag. Use when the user wants to create a skill, turn a workflow or checklist into a skill, or automate a repeated multi-step task for Claude.
argument-hint: "[workflow-name] [--no-tags]"
---

# Groundwork: skill

Turn one repeatable workflow into a Claude Code skill, and teach the user how skills
work while doing it. Every part you write gets a why-tag.

Read `../init/references/why-tags.md` for the tag format and vocabulary, and
`references/skill-rubric.md` (in this skill's directory) for what makes a good skill.

Arguments: `$ARGUMENTS` (optional workflow name; `--no-tags` keeps tags out of files).

## 0. Does it already exist?

List `.claude/skills/*/SKILL.md` and read each `name` and `description`.

- **Same name, or same workflow under another name:** do not create a new skill. Offer to
  update the existing one in place, showing a diff. `→ Why: no duplicate skills`
- **Nothing to change** after the interview: say "unchanged" and write nothing.
- Never create variants such as `release-2` or `release-new`.
- If the workflow is already fully covered by a line in AGENTS.md, say so instead.

## 1. Is this a skill?

A skill is worth it when the workflow is **repeated**, has **several steps**, and the
agent would otherwise re-figure it each time. If the user describes a one-off task or a
single rule, say so with a tag and suggest the right home instead:

- Single rule or fact → a line in AGENTS.md. `✗ skill → Why: belongs in AGENTS.md`
- One-off task → just do it. `✗ skill → Why: not repeated`

## 2. Interview

Ask up to 5 questions in one message, skippable:

1. What is the workflow, and when do you use it? (what the user would type or be doing)
2. What are the steps, roughly in order? Any commands?
3. What must be checked before it counts as done?
4. What goes wrong most often?
5. Anything it must never do without asking (push, publish, delete, migrate)?

If the workflow is visible in the repo (CI job, Makefile target, script, docs page),
read it first and pre-fill the answers so the user only confirms.

## 3. Draft

Build the skill from `references/skill-rubric.md`:

- `name`: short kebab-case, verb-first where natural (`release`, `add-migration`).
- `description`: what it does and when to use it, including the words the user would
  naturally say. This is what makes Claude load it. `→ Why: triggers auto-loading`
- Body: numbered steps with exact commands, a done-check, and guardrails.
- Long reference material (checklists, templates) goes in `references/` next to SKILL.md.
  `→ Why: loads on demand`

## 4. Propose

Show:

```
Skill: release  → .claude/skills/release/SKILL.md (~40 lines)
  ✓ description with trigger words     → Why: triggers auto-loading
  ✓ 6 numbered steps                   → Why: predictable execution
  ✓ done-check: tag pushed, CI green   → Why: agents verify work
  ✓ guardrail: ask before publish      → Why: avoids costly mistakes
  ✗ changelog template inline          → Why: loads on demand
```

Then the full draft. Ask "Create this skill?" and wait for approval.

## 5. Write and teach

Write `.claude/skills/<name>/SKILL.md` (and any `references/` files). Unless `--no-tags`,
add why-tags as HTML comments on section headers.

Finish with:
- How to use it: "Type `/<name>`, or just ask for it; the description lets Claude pick it up."
- A 2-line "What you learned" recap using the top tags.
- If `AGENTS.md` exists, offer to add one line pointing to the skill.
  `→ Why: faster navigation`
