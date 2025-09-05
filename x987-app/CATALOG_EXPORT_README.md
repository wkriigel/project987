Generation Catalog Export (for FE docs)

Purpose
- Provide a single source of truth for FE to display trims and options per generation.

Source of Truth
- Python config: `x987-config/config.toml`
  - `[vehicles.models.*.generations]` → trims per generation
  - `[options_per_generation.<Model>.<Gen>.msrp]` → per-generation option IDs (used to list options)

Exporter
- Python module: `x987-app/x987/catalog/export.py`
- Builds JSON with models → generations → { trims, options, default flags }

Usage
1) From `x987-app` directory:

   python -m x987.catalog.export

2) Output (default path):

   x987-web/apps/api/data/generation_catalog.json

API
- The FE calls `GET /api/catalog/generations` which serves the JSON if present.
- If not present, the API responds with `{ ok: true, source: 'defaults' }` and the FE shows a small “defaults pending” note.

Notes
- Options list per generation is populated only when `options_per_generation` has MSRP entries for that (model, gen). Otherwise FE indicates defaults are used.
- Trims are always sourced from config and marked non-default.

