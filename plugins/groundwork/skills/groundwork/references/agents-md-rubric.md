# What a good AGENTS.md looks like

AGENTS.md is read at the start of every session, so every line costs context.
Aim for **40-120 lines**. Shorter is better if nothing important is lost.

## Include (in this order)

1. **One-line project summary.** What this is, in plain words.
2. **Commands**, verified only: install, build, test, single test, lint/format, run.
   Give the exact command and working directory. Mark a command `(slow)` only if it
   takes over about a minute. Never write exact timings: they drift and cause churn.
3. **Project map.** 5-12 key directories/files with a few words each. Not a full tree.
4. **Conventions that are NOT obvious from the code**: naming rules, where new code goes,
   error-handling style, commit message format, branch rules.
5. **Do-not-touch.** Generated, vendored, or build-output paths; secrets files.
6. **Gotchas.** Things the user said agents get wrong. This is the most valuable section.
7. **Definition of done.** For example: "tests pass, lint clean, no new warnings".

## Leave out

- Style rules a formatter or linter already enforces.
- Generic advice ("write clean code", "add comments").
- Anything the agent can learn by reading one obvious file.
- Long explanations. Link to docs/ instead.
- Unverified commands. If a command could not be verified, omit it or mark it `(unverified)`.

## Format

- Markdown headings: `## Commands`, `## Project map`, `## Conventions`,
  `## Do not edit`, `## Gotchas`, `## Done means`.
- Commands in fenced code blocks.
- Imperative, concrete sentences: "Run `pnpm test --filter api` for API changes."
- Wrap the sections Groundwork owns in managed markers:

```
<!-- groundwork:begin commands -->
...
<!-- groundwork:end commands -->
```

  On re-runs, only replace content inside markers. Everything outside is the user's.

## CLAUDE.md

Claude Code reads CLAUDE.md, not AGENTS.md. Generate a thin CLAUDE.md:

```
@AGENTS.md

<!-- Claude Code-specific notes go below. Shared instructions live in AGENTS.md. -->
```

If a CLAUDE.md already exists with real content, do not replace it. Offer to move
the shared content into AGENTS.md and leave the Claude-specific parts plus `@AGENTS.md`.
