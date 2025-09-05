Vehicle Catalog (Models/Trims)

Purpose
- Centralize model/trim detection in a config-driven, generation-aware catalog for scalability.

Where
- Config: `x987-config/config.toml` under `[vehicles]`.
- Code: `x987-app/x987/vehicles.py` loads the catalog and exposes `detect_model_and_trim(text)`.
- Extractors: `x987-app/x987/utils/extractors.py::extract_vehicle_info_unified` uses it.

How to add models/trims
- Add a new block under `[vehicles.models.<ModelKey>]` with:
  - `name`: canonical model name (e.g., "911").
  - `synonyms`: list of strings to recognize the model in text.
  - `[[...generations]]`: each has `code`, `years = { min, max? }`, and nested `[[...generations.trims]]` with `name` and `synonyms`.
  - Optionally, a top-level `[[...trims]]` array as a generic fallback across generations.

Notes
- Year-aware: when a year is present, only trims under the matching generation are considered first.
- Trim matching prefers more specific synonyms first (e.g., "Carrera 4S" before "Carrera").
- Complete coverage added per your list: Boxster/Cayman, 911, Cayenne, Panamera, Macan, Taycan.
