# x987-web

Isolated web frontend for Project987. This app reads the ranking CSV output and renders an interactive table with sorting, filtering, and a summary header. It also provides a separate Controls tab to view and edit config options.

This folder is completely isolated from the Python CLI app — it has its own tooling and dependencies and cannot affect the CLI.

## Structure

```
x987-web/
  apps/
    fe/      # React + Vite + TypeScript frontend (Ant Design + Tailwind + FontAwesome)
    api/     # Express + TypeScript API (reads latest ranking CSV, reads/writes config)
  .storybook/  # Storybook configuration (component examples)
```

## Dev Setup

1) Install dependencies (from `x987-web/` root):
```
npm install
```

2) Run both servers in dev mode (API at 4000, FE at 5173):
```
npm run dev
```

3) Open the app:
```
http://localhost:5173
```

4) Storybook (component catalog):
```
npm run storybook
```

## API Endpoints (apps/api)

- `GET /api/health` → basic health probe
- `GET /api/ranking/latest` → returns JSON from the latest `ranking_main_*.csv` and its filename
- `GET /api/config` → returns TOML text of `x987-config/config.toml`
- `PUT /api/config` → writes TOML with a timestamped backup (basic validation)

### API Env Vars
- `RANKING_FILE` → absolute path to a CSV to serve (overrides auto-discovery)
- `RANKING_RESULTS_DIR` → absolute path to a results directory to search for ranking CSVs

Examples:
```
RANKING_FILE=/Users/you/Project987/x987-app/x987-data/results/ranking_main_20250828_164928.csv npm run dev:api
```
or
```
RANKING_RESULTS_DIR=/Users/you/Project987/x987-app/x987-data/results npm run dev:api
```

## Notes

- Data is read from the repo’s existing folders. The API attempts these locations for results, in order:
  - `x987-data/results/`
  - `x987-app/x987-data/results/`
- Config is read from `x987-config/config.toml` at the repo root.
- The frontend mirrors the CLI view’s rules (column order, abbreviations, highlight thresholds) and adds multi-sort, filters, and CSV upload fallback.
