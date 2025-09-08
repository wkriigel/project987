Project Standards (x987)

Scope: configuration, data locations, naming, logging, terminal output, and TypeScript/Python baselines.

- Config: single canonical file at `x987-config/config.toml`. No `v2`/`final`/`new` suffixes.
- Data: canonical generation catalog JSON at `x987-data/metadata/generation_catalog.json`.
- Paths: API resolves results from `x987-data/results` (env `RANKING_RESULTS_DIR` overrides).
- Naming: remove versioned filenames; provide shims for Python import paths when needed.
- Logging (Python): use `x987.utils.log` with INFO default; no ad‑hoc prints in libraries.
- Logging (Node): prefix logs with `x987-api`; use structured error messages.
- Terminal output: consistent emoji prefixes in CLI; quiet mode respected by steps (where available).
- TypeScript: `strict` enabled; JSON imports allowed; avoid `any` in new code.
- Git hygiene: do not commit build artifacts (`dist/`, `storybook-static/`), `.DS_Store`, or logs.

