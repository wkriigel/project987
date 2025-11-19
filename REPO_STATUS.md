Project Status – Paused (Safe Stopping Point)

Summary
- Scope: Pipeline, API, and FE work completed through “MSRP-only” path; fair-value logic intentionally disabled.
- Status: Project paused as of 2025-11-19. Code builds and runs; docs and archive organized for easy resume.
- Stability: No functional changes made as part of this cleanup. Only docs, archive moves, and OS cruft removal.

What Works
- Python pipeline: scrapes, extracts, and produces ranking CSVs.
- API: serves latest ranking CSV and generation catalog (if present).
- FE: browses and filters served data; shows defaults when catalog is missing.

Key Entry Points
- Config: `x987-config/config.toml`
- Pipeline CLI: `python -m x987 pipeline --headful`
- API: `x987-web/apps/api` (Express; `npm ci && npm run build && node dist/index.js`)
- FE: `x987-web/apps/fe` (Vite; `npm ci && npm run dev`)

Decisions & Standards
- Single canonical config file (no versioned filenames).
- Storage defaults to SQLite (`x987-data/x987.db`). File-based storage remains available for legacy runs.
- Logging via `x987.utils.log` (Python) and `[x987-api]` prefixes (Node).
- Build artifacts and logs are not committed; OS files (`.DS_Store`) removed and ignored.

Known Gaps (for future work)
- Fair value model: intentionally disabled; MSRP-only calculations in place.
- Options catalog: extend values/patterns as needed (see `[options]` in `config.toml`).
- Generation catalog: provide canonical JSON at `x987-data/metadata/generation_catalog.json` for richer FE metadata.

Where Older Material Lives
- Archive root: `archive/`
  - Early exploration and legacy requirement notes: `archive/specs/early-exploration/`
  - Context assets: `archive/assets/`
- Additional in-repo docs are kept under `docs/` and `x987-app/docs/`.

How To Resume
- See `RESUME_GUIDE.md` for an end-to-end, copy/paste flow.

