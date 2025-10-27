Title: MSRP‑Only Pipeline: remove Fair Value/Deal; rank by Options MSRP

Summary
- Consolidates pipeline to MSRP‑only (no Fair Value/Deal). UI and outputs show per‑option MSRP aggregation and options list only.
- Back end computes `total_options_msrp` using per‑generation overrides first, then `options.msrp_catalog`, else a default MSRP of 494 for unknown options.
- Ranking uses deduplicated listings and sorts by `total_options_msrp` (descending). Outputs a single `ranking_main_*.csv` compatible with the FE/API.
- Frontend removes deal/fair value usage; MSRP column is kept and now defaults to descending sort.

Key Changes
- Config
  - Renamed `[options_v2]` to `[options]`, kept backward‑compatible loader.
  - Enforces `storage.mode = 'sqlite'` (no JSON fallback).
  - `pipeline.export_csv = true` by default; `pipeline.output_directory` set to top‑level results for FE/API.
  - Files: `x987-app/x987/config/defaults.py`, `x987-app/x987/config/manager.py`, `x987-app/x987/config/validation.py`, `x987-config/config.toml`.

- Options detection
  - `x987-app/x987/options/detector.py`: compute per‑option MSRP instead of “value”. Uses per‑generation overrides, else catalog, else 494 fallback. Still returns `(display, value, category)` to preserve API shape; value now equals MSRP.

- Transformation
  - `x987-app/x987/pipeline/steps/transformation.py`:
    - Aggregates `total_options_msrp` with override/catalog/494 fallback.
    - Writes `total_options_value` as blank when `pricing_mode=msrp_only` for soft deprecation.
    - Builds a robust text source (title + raw_dom_text + raw_sections) for extractors to improve mileage/year/price detection.
    - Emits `total_options` count for CSV.

- Fair value step
  - Removed entirely; pipeline order is Collection → Scraping → Transformation → Deduplication → Ranking → View.

- Ranking
  - `x987-app/x987/pipeline/steps/ranking.py`: depends on `deduplication`, sorts by `total_options_msrp` desc, writes `asking_price_usd` for FE compatibility.

- Frontend
  - `x987-web/apps/fe/src/App.tsx`: MSRP column default sort order set to `descend`. FE continues to show options list and MSRP total only.

CSV/Contracts
- Transformed CSV minimal fields include: `source_url, listing_url, year, model, trim, price, mileage, exterior, interior, options_list, options_by_category, total_options_msrp`.
- Legacy `total_options_value` is present but blank when `msrp_only` for backward compatibility.
- Fair value / deal fields are not emitted; legacy fields are blank.

Docs
- Updated callgraphs and inventories to remove Fair Value; examples reflect MSRP totals only.

Testing/Validation
- Manual validation: pipeline completes end‑to‑end with MSRP‑only mode; FE loads results, shows MSRP column and options chips; default sort is MSRP highest first.
- Extraction robustness: transformation now composes a better text source for year/price/mileage; verified populated mileage where previously empty.

Breaking/Risk
- Consumers expecting fair value/deal fields will no longer receive them (legacy fields remain blank). Ranking output omits deal columns by design.

Follow‑ups
- Update any ancillary docs still referencing “fair value” or “deal”.
- Refresh tests around MSRP aggregation paths and DB‑backed cache/seen behavior.

How to test locally
1) Ensure Playwright Chromium is installed: `python -m playwright install chromium`.
2) Run pipeline: `python -m x987 pipeline --headful`.
3) Start API: `pnpm --filter @x987/api dev` (or `npm run dev` in `x987-web/apps/api`).
4) Start FE: `pnpm --filter @x987/fe dev`.
5) Verify FE “MSRP” column sorts descending and options chips render.

New in this PR: Seen Registry + Cache Skip (SQLite)
- Collection annotates `canonical_url`, `is_new`, and `first_seen_at` using SQLite seen_registry.
- Scraping uses SQLite‑backed cache to skip VDP loads when TTL valid and fields complete.
- Serial and concurrent scrapers both respect DB cache; summary prints `Cache hits` and `Network scrapes`.
- CSVs include per‑row `is_new`, `first_seen_at`, `cache_hit`, and `cache_reason` for visibility.

Quick validation
- First run seeds the cache: expect `Cache hits: 0 | Network scrapes: N`.
- Immediate second run: expect `Cache hits: ~N | Network scrapes: 0`.
- To reset, delete `x987-app/x987-data/listing_cache.json`.

Notes
- `view.py` requires `rich`; optional for pipeline execution. Install with `pip install rich` if you want the view step registered.

Config notes
- Options are under `[options]` (legacy `[options_v2]` still accepted).
- `storage.mode` must be `sqlite`.

Acceptance criteria mapping
- No value/spec score/fair value/deal in UI or CSV outputs in MSRP‑only mode: ✅ (legacy fields blank; no fair value/deal emitted in ranking)
- Options MSRP totals compute with per‑generation overrides: ✅
- FE shows MSRP + options only; default sort is MSRP desc: ✅
- Tests: requires follow‑up adjustments (Phase 2): ⚠️ pending
- Docs reflect MSRP‑only: Phase 2 cleanup: ⚠️ pending
