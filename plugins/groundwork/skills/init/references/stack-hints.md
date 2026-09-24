# Stack hints

Use these to fill gaps the detector leaves and to ask sharper interview questions.

## Python
- **Single test:** `pytest path/to/test_file.py::test_name` (prefix `uv run` / `poetry run` if used).
- Ask: which Python version? Is there a `src/` layout? Any tests that need network/DB?
- Gotchas worth capturing: virtualenv activation, slow integration tests behind a marker.

## Node / TypeScript
- **Single test:** vitest `pnpm vitest run path -t "name"`; jest `npx jest path -t "name"`.
- Monorepo (pnpm/turbo/nx): record the filter syntax, e.g. `pnpm --filter <pkg> test`.
- Ask: which package manager is mandatory? Is `typecheck` separate from `build`?
- Do not edit: `dist/`, `.next/`, generated API clients.

## Go
- **Single test:** `go test ./pkg/foo -run TestName`.
- Ask: is `golangci-lint` used? Are there generated files (`*_gen.go`, `*.pb.go`)?

## Rust
- **Single test:** `cargo test test_name` or `cargo test -p crate test_name` in workspaces.
- Ask: are `clippy` warnings errors in CI (`-D warnings`)?

## JVM
- **Single test:** Gradle `./gradlew test --tests 'pkg.ClassTest.method'`; Maven `mvn -Dtest=ClassTest#method test`.

## Any stack
- CI files are the best source of truth for which commands really matter. Read them.
- A README "Development" or "Contributing" section often lists setup steps.
- On Windows, prefer commands that work in both PowerShell and bash, or note which shell.
