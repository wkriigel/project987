ADR 0001: Consolidate Config to a Single Canonical File

Status: Accepted
Date: 2025-09-08

Context
- Two TOML configs existed: `x987-config/config.toml` and `x987-config/config-v2.toml`.
- Code loads only `config.toml`; `config-v2.toml` diverged and caused confusion.

Decision
- Remove `config-v2.toml` and keep `x987-config/config.toml` as the single source of truth.
- Preserve behavior with Python config defaults/validation.
- Update docs to reference only `config.toml`.

Consequences
- Eliminates drift and confusion; fewer configuration entry points.
- Any values in the old `config-v2.toml` can be reintroduced via `config.toml` as needed.

