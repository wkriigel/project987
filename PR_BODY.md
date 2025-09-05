Title: MSRP‑Only Mode (Phase 1): Remove Value/Fair Value/Deal; show MSRP total only

Summary
- Adds `pricing_mode = "msrp_only"` feature flag (default) to gate removal of all price modeling fields: Value/Spec Score/Fair Value/Deal. UI and outputs show only per‑option MSRP aggregation and options list.
- Back end computes `total_options_msrp` using per‑generation overrides first, then `options_v2.msrp_catalog`, else a default MSRP of 494 for unknown options.
- Fair value step is a no‑op in MSRP‑only mode; ranking uses deduplicated listings and sorts by `total_options_msrp` (descending). Outputs a single `ranking_main_*.csv` compatible with the FE/API.
- Frontend removes deal/fair value usage; MSRP column is kept and now defaults to descending sort.

Key Changes
- Config
  - New: top‑level `pricing_mode` with values: `msrp_only` | `current`; default is `msrp_only`.
  - `fair_value` section is optional/ignored in MSRP‑only mode; validation updated to reflect that.
  - Files: `x987-app/x987/config/defaults.py`, `x987-app/x987/config/manager.py`, `x987-app/x987/config/validation.py`, `x987-config/config.toml`, `x987-config/config-v2.toml`.

- Options detection
  - `x987-app/x987/options/detector.py`: compute per‑option MSRP instead of “value”. Uses per‑generation overrides, else catalog, else 494 fallback. Still returns `(display, value, category)` to preserve API shape; value now equals MSRP.

- Transformation
  - `x987-app/x987/pipeline/steps/transformation.py`:
    - Aggregates `total_options_msrp` with override/catalog/494 fallback.
    - Writes `total_options_value` as blank when `pricing_mode=msrp_only` for soft deprecation.
    - Builds a robust text source (title + raw_dom_text + raw_sections) for extractors to improve mileage/year/price detection.
    - Emits `total_options` count for CSV.

- Fair value step
  - `x987-app/x987/pipeline/steps/fair_value.py`: returns a stub result in MSRP‑only mode (no fair value/deal outputs). No downstream dependency on its outputs when `msrp_only` is active.

- Ranking
  - `x987-app/x987/pipeline/steps/ranking.py`: dynamic dependency based on `pricing_mode`.
    - MSRP‑only: depends on `deduplication`, sorts by `total_options_msrp` desc, writes `asking_price_usd` for FE compatibility.
    - Non‑MSRP: unchanged (depends on fair value).

- Frontend
  - `x987-web/apps/fe/src/App.tsx`: MSRP column default sort order set to `descend`. FE continues to show options list and MSRP total only.

CSV/Contracts
- Transformed CSV minimal fields include: `source_url, listing_url, year, model, trim, price, mileage, exterior, interior, options_list, options_by_category, total_options_msrp`.
- Legacy `total_options_value` is present but blank when `msrp_only` for backward compatibility.
- Fair value / deal fields are not emitted in MSRP‑only ranking output.

Docs
- Phase 1: Soft deprecation. Docs are not fully pruned yet; next PR will remove remaining references to “deal”/“fair value” and update examples to reflect MSRP totals only.

Testing/Validation
- Manual validation: pipeline completes end‑to‑end with MSRP‑only mode; FE loads results, shows MSRP column and options chips; default sort is MSRP highest first.
- Extraction robustness: transformation now composes a better text source for year/price/mileage; verified populated mileage where previously empty.

Breaking/Risk
- Default `msrp_only` may affect external consumers expecting fair value/deal fields. Mitigation: legacy fields are kept as blanks; ranking output omits deal columns by design. We can flip the default back to `current` if we need a longer migration window.

Follow‑ups (Phase 2 cleanup)
- Remove dead code/files and references:
  - `x987-app/x987/extractors/deal.py` and docs mentioning deal/fair value.
  - Prune fair value step entirely and dependent ranking paths once all consumers are migrated.
- Update tests to reflect MSRP‑only behavior (remove deal/spec score assertions; add MSRP aggregation tests).
- Finalize docs with MSRP‑only narrative and CSV examples.

How to test locally
1) Ensure Playwright Chromium is installed: `python -m playwright install chromium`.
2) Run pipeline: `python -m x987 pipeline --headful`.
3) Start API: `pnpm --filter @x987/api dev` (or `npm run dev` in `x987-web/apps/api`).
4) Start FE: `pnpm --filter @x987/fe dev`.
5) Verify FE “MSRP” column sorts descending and options chips render.

Config notes
- `pricing_mode` at top‑level of `config.toml` and `config-v2.toml`.
- `fair_value` table ignored in MSRP‑only and optional in validation.

Acceptance criteria mapping
- No value/spec score/fair value/deal in UI or CSV outputs in MSRP‑only mode: ✅ (legacy fields blank; no fair value/deal emitted in ranking)
- Options MSRP totals compute with per‑generation overrides: ✅
- FE shows MSRP + options only; default sort is MSRP desc: ✅
- Tests: requires follow‑up adjustments (Phase 2): ⚠️ pending
- Docs reflect MSRP‑only: Phase 2 cleanup: ⚠️ pending

