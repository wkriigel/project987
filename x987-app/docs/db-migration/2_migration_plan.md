Title: Migration Plan — File Storage to SQLite

Goals
- Preserve app functionality during changeover.
- Establish durable linking across stages via `listing_key` (canonical URL).

Phases
1) Add config + DB layer
   - Add `[storage]` with `mode = 'sqlite'` and `db_path`.
   - Create schema and connection helpers; no behavior change yet.

2) Dual-write from pipeline
   - Collection: continue CSV, mirror to DB (`listings`, `seen_registry`).
   - Scraping: continue CSV/artifacts, mirror to DB (`scrapes`).
   - Transformation: export CSV, mirror parsed fields to DB (`parsed_listings`).
   - Ranking: export CSV, mirror to DB (`rankings`).

3) Import historical files
   - Script `scripts/migrate_to_db.py` imports JSON registries and CSV outputs.

4) Validate and cut over
   - Spot-check counts (rows per stage vs CSV line counts).
   - Toggle reads to DB in future iterations; retain exports for inspection.

Validation
- Row counts per stage match recent CSVs (± expected skips).
- Sample listing resolves across tables by `listing_key` and `listing_id`.

Rollback
- Switch `storage.mode` to `files` to disable DB writes.
- No destructive changes to original JSON/CSV.

