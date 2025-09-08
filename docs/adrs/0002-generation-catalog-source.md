ADR 0002: Canonical Generation Catalog Location

Status: Accepted
Date: 2025-09-08

Context
- Duplicate generation catalog JSONs existed under `x987-web/apps/api/data/` and `x987-data/metadata/`.
- API utils preferred the copy bundled with API sources, increasing drift risk.

Decision
- Canonicalize to `x987-data/metadata/generation_catalog.json` and delete API-local copies and partials.
- Update `findGenerationCatalogJson()` to prefer `x987-data/metadata` first.

Consequences
- Single source of truth for FE/API to consume; avoids accidental divergence.
- Legacy path remains as a fallback to ease transition.

