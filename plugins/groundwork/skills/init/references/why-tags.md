# Why-tags: the Groundwork lesson format

Every item Groundwork creates, changes, or deliberately skips carries a **why-tag**:
a 2-3 word reason that teaches the user what the item is for.

## Rules

1. **2-3 words, no more.** Lowercase except proper nouns. No trailing period.
2. **State the benefit, not the action.** "agents verify work", not "adds test command".
3. **Skips get tags too.** Explaining why something was left out is often the best lesson.
4. **Same idea, same tag.** Reuse tags from the table below so the user sees a consistent vocabulary.
5. **Never invent certainty.** If a command was not verified, the tag must say so ("unverified, check").

## Where tags appear

- **Chat, during setup**, one line per item:
  `✓ AGENTS.md: test command  → Why: agents verify work`
  `✗ skipped: style rules     → Why: linter enforces it`
- **In generated files**, as an HTML comment at the end of the line or section header
  (invisible when rendered): `<!-- why: agents verify work -->`.
  Omit in-file tags if the user said `--no-tags` or asked for clean files.

## Standard vocabulary

| Item | Why-tag |
|---|---|
| Build / test / lint command | agents verify work |
| Single-test command | fast feedback loop |
| Project map / key directories | faster navigation |
| "Do not edit" paths (generated, vendored) | prevents wasted edits |
| Forbidden / dangerous actions | avoids costly mistakes |
| Non-obvious convention | not in code |
| Environment / setup steps | reproducible runs |
| CLAUDE.md containing `@AGENTS.md` | single source |
| Keeping AGENTS.md short | context is budget |
| Skill created | repeatable workflows |
| Skill `description` field | triggers auto-loading |
| Skill steps numbered | predictable execution |
| Skill references/ file | loads on demand |
| Skipped: style rules covered by linter/formatter | linter enforces it |
| Skipped: info obvious from code | agent can read |
| Skipped: unverified command | unverified, omitted |
| Skipped: one-off task as skill | not repeated |
| Merged with existing file | keeps your edits |
| Managed markers | safe regeneration |

Coin a new tag only when none fits; keep it within 2-3 words.

## `explain` expansion

If the user asks "why?" about a tag, expand it into 2-4 plain sentences aimed at
someone new to agent setup: what the item does, what goes wrong without it, and one
concrete example from their repo.
