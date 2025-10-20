feat(storage): SQLite-backed data layer with dual-write and migration

This PR transitions storage from CSV/JSON to a lightweight SQLite DB while keeping CSV exports for continuity.

Highlights
- Adds `storage` config with `mode=sqlite`, `db_path`, and retention knobs.
- Introduces SQLite schema: listings, seen_registry, listing_cache, scrapes, parsed_listings, enrichments, rankings, url_vin_index, vin_enriched, listing_options.
- Dual-writes pipeline stages to DB: collection (listings + seen), scraping (scrapes + cache), transformation (parsed + enrichments + listing_options), ranking (rankings).
- DB-backed seen-registry, cache, and URL↔VIN index; JSON fallbacks removed from write paths.
- Adds migration script (`python -m x987.scripts.migrate_to_db`) and archive script (`python -m x987.scripts.archive_legacy_storage`).
- Adds `pipeline.export_csv` toggle (default true) to reduce redundant CSVs.
- Internal docs: Technical Decision, Migration Plan, Data Model, Refinement Plan, Risk, Internal Review.

Risk
- Low. Single-user, staged, reversible (set `storage.mode=files`).

Post-merge follow-ups (optional)
- Add `pipeline.export_csv=false` in environments to reduce artifacts.
- Consider additional view/queries; add retention tuning as needed.

Validation
- Ran migration and verified tables populated; dual-write confirmed.

