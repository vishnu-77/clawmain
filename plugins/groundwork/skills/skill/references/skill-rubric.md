# What a good skill looks like

## Frontmatter

```yaml
---
name: add-migration
description: Create and apply a database migration for this project using Alembic, including model update, autogenerate, review, and test run. Use when the user wants to add a column, change the schema, or create a migration.
---
```

- `name`: kebab-case, short, becomes `/name`.
- `description`: 1-3 sentences. First say **what it does**, then **when to use it**,
  with the words a user would naturally type. Vague descriptions never trigger.
- Optional: `argument-hint` for expected arguments; `disable-model-invocation: true`
  only for skills that must run only when typed explicitly (for example, anything that
  publishes or deploys).

## Body

1. **One-line purpose.**
2. **Preconditions**: what must be true first (clean git tree, on main, env var set).
3. **Numbered steps**, each with the exact command or file to touch.
4. **Done-check**: how to verify it worked (tests pass, command output, file exists).
5. **Guardrails**: what to never do, and what to ask before doing.
6. **If it fails**: the 1-3 most common failures and what to do.

## Size

- SKILL.md: aim for 20-80 lines.
- Move long checklists, templates, or examples to `references/<file>.md` and tell the
  skill when to read them ("Read `references/checklist.md` before step 4.").

## Anti-patterns

- A skill that restates general knowledge ("how to write Python").
- A skill with no commands or concrete steps.
- A description that says only "helps with X".
- Steps that assume knowledge the agent doesn't have ("deploy the usual way").
- Dangerous steps (publish, push --force, drop table) with no confirmation step.
