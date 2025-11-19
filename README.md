X987 – Vehicle Listings Analyzer

Overview
- End‑to‑end system to collect, transform, rank and view Porsche listings.
- Python pipeline produces CSVs; a Node API serves them to a React FE.

Project Status
- Paused as of 2025-11-19. See `REPO_STATUS.md` and `RESUME_GUIDE.md` for details and how to resume.

Repo layout
- Python: `x987-app/` (pipeline, scrapers, options, config)
- Config: `x987-config/config.toml` (single canonical config)
- Data: `x987-data/` (results, metadata)
- Web: `x987-web/apps/api` (Express API), `x987-web/apps/fe` (React FE)

Prerequisites
- Python 3.11+
- Node.js 18+
- Playwright Chromium for scraping: `python -m playwright install chromium`

Quick start
1) Generate data (Python pipeline)
   - `cd x987-app`
   - `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\\Scripts\\activate`)
   - `pip install -r requirements.txt`
   - `python -m x987 pipeline --headful` (or `--verbose`)
   - Output: `ranking_main_*.csv` under `x987-app/x987-data/results/`

2) Start API (serves latest CSV automatically)
   - `cd x987-web/apps/api`
   - `npm install && npm run build`
   - `node dist/index.js`
   - Health check: `curl http://localhost:4000/api/health`
   - Data: `curl http://localhost:4000/api/ranking/latest`

3) Start FE (React/Ant Design)
   - `cd x987-web/apps/fe`
   - `npm install && npm run dev`
   - Open the indicated local URL

Configuration
- Edit `x987-config/config.toml` (search URLs, scraping settings, options catalog, vehicles).
- Canonical generation catalog JSON: `x987-data/metadata/generation_catalog.json`.
- API env (optional):
  - `PORT` – API port (default 4000)
  - `RANKING_RESULTS_DIR` – override results directory (auto‑discovery enabled)
  - `RANKING_FILE` – serve a specific CSV file

Troubleshooting
- FE table empty: ensure the pipeline produced CSVs (see step 1).
- API 404 on ranking: API returns a JSON body with `searched` paths. Confirm CSVs exist in one of those.
- Generation catalog missing: add `x987-data/metadata/generation_catalog.json` (API prefers this canonical file).

Standards
- Single canonical config file; no versioned filenames.
- Results auto‑discovered across canonical and legacy directories.
- No committed build artifacts (`dist/`, `storybook-static/`).

Beginner Setup
- New to GitHub projects? Start with `GETTING_STARTED.md` for a step‑by‑step guide.

Archive
- Historical specs and one-off assets live under `archive/`. See `archive/README.md`.
