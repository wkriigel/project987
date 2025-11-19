Contributing Guide

Principles
- Keep the single canonical config: `x987-config/config.toml`.
- Prefer SQLite storage; file-based storage remains for legacy support.
- Avoid committing build artifacts, logs, or OS files.
- Preserve API and CLI shapes unless explicitly changing a contract.

Code Style
- Python: type hints where practical; use cohesive modules (`x987/...`).
- Node: small composable utilities; prefix logs with `[x987-api]`.
- FE: clear state names; keep thresholds and catalogs in isolated helpers.

PRs
- Use the template in `PR_BODY.md` for feature/bug PRs.
- For DB or storage migrations, see `PR_DB_TRANSITION_BODY.md`.
- Link to relevant ADRs under `docs/adrs/`.

Tests
- Add targeted unit tests near the modules changed.
- For pipeline changes, include at least one representative data sample.

Docs
- Active docs live under `docs/` and `x987-app/docs/`.
- Archive outdated specs under `archive/` with a brief rationale as needed.

