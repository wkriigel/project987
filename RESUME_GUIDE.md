Resume Guide – X987

Audience
- Engineers and AI agents needing an end-to-end path to pick up work quickly.

Environment
- Python 3.11+, Node 18+, recent npm.
- One-time: `python -m playwright install chromium` for scraping.

1) Configure
- Edit `x987-config/config.toml`:
  - `[search].urls`: sources to scrape
  - `[scraping]`: concurrency, polite delay, caps
  - `[storage]`: `sqlite` (default) or `files`
  - `[options]`: MSRP catalog and detection patterns

2) Run Pipeline (Python)
- `cd x987-app`
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python -m x987 pipeline --headful` (add `--verbose` as needed)
- Outputs appear under `x987-app/x987-data/results/`.

3) Start API
- `cd x987-web/apps/api`
- `npm install && npm run build`
- `node dist/index.js`
- Health: `curl http://localhost:4000/api/health`
- Data: `curl http://localhost:4000/api/ranking/latest`

4) Start FE
- `cd x987-web/apps/fe`
- `npm install && npm run dev`
- Open the printed local URL.

5) Optional: Generation Catalog
- Provide `x987-data/metadata/generation_catalog.json` to enrich FE with trims/options per generation.

Operational Notes
- Logging: Python via `x987.utils.log` (INFO default); Node logs prefixed `[x987-api]`.
- Storage: default SQLite db at `x987-data/x987.db` (ignored by git).
- Do not commit logs or build artifacts; `.gitignore` covers common cases.

Next Work Candidates
- Enable/implement fair value model (currently MSRP-only).
- Expand options catalog values and patterns.
- Add integration tests for end-to-end scraping to ranking output.
