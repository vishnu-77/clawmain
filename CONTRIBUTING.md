# Maintaining clawmain

## Layout

```
catalog/                 source of truth for all agent plugins
  _harness.md            loop contract injected into every agent
  <department>.toml      one department = one plugin
tools/build.py           generates plugins, marketplace entries, graph, docs
plugins/groundwork/      hand-written plugin (skills), not generated
plugins/<department>/    GENERATED; do not edit by hand
docs/                    loop-harness.md is hand-written; the rest is generated
tests/                   detector and catalog tests
```

## Add or change an agent

1. Edit `catalog/<department>.toml` (copy an existing `[[agents]]` block).
2. Run `python tools/build.py`. It validates the catalog, then writes the agent files,
   the plugin README, the marketplace entries, and the graph.
3. Run `python -m unittest discover -s tests`.
4. Bump `version` in the department's `[department]` table when agent behavior changes.
5. Commit the catalog change **and** the generated files together.

CI runs `python tools/build.py --check` and fails if generated files are stale.

## Add a department

Create `catalog/<slug>.toml` with a `[department]` table (`slug`, `title`, `summary`,
`recommend_when`, `color`, optional `version`) and at least one agent. The build adds
the plugin to the marketplace automatically.

## Agent rules (enforced by the build)

- `name`: kebab-case, unique across all departments.
- `description`: what it does plus `Use when ...` triggers, at most 400 characters.
- `why`: a 2-3 word lesson (the Groundwork why-tag).
- `model`: `haiku` for mechanical work, `sonnet` for judgment, `opus` only when needed.
- `mode`: `read-only` agents get no Edit/Write tools; `writes` agents need one.
- `tools`: least privilege.
- `steps` 3-8, `outputs` 1-8, `guardrails` 1-6.
- `handoffs`: each `to` must be an existing agent, with a `when`.

## Release (same flow as OpenReflex)

1. Change catalog or plugin files.
2. Bump: `python tools/bump.py <plugin> patch` (or `all minor`). This bumps the plugin,
   bumps the marketplace version, and rebuilds.
3. Add a `## X.Y.Z` section to `CHANGELOG.md` for the new marketplace version.
4. Push to main. **CI** validates the catalog, the release metadata, and version bumps, runs
   the tests, and smoke-tests every plugin in a real Claude Code CLI (Ubuntu + Windows).
5. On green CI, **Auto Release** dispatches **Release** with the exact tested SHA. Release
   repeats the smoke test on Ubuntu, macOS, and Windows, then creates the `vX.Y.Z` tag and
   the GitHub Release, with notes taken from the changelog.

CI fails if a plugin changed after its version was released without a bump, because
Claude Code only offers an update when the version changes.

Local checks before pushing:

```
python tools/build.py --check
python tools/release_meta.py --check-bumps
python -m unittest discover -s tests
python scripts/smoke_plugins.py      # needs the claude CLI; uses an isolated config
```

Other marketplaces can pin a release with `ref: "vX.Y.Z"` in their `git-subdir` source
(see [docs/other-marketplaces.md](docs/other-marketplaces.md)).
