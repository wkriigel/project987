Getting Started – Beginner-Friendly Guide

Goal
- Run the full X987 app locally: Python pipeline → Node API → React UI.

What You Need
- Git (to clone the repo)
- Python 3.11 or newer (check: `python3 --version` or `python --version`)
- Node.js 18 or newer and npm (check: `node --version`, `npm --version`)

1) Clone the Repo
- macOS/Linux:
  - `git clone https://github.com/your-org/Project987.git`
  - `cd Project987`
- Windows:
  - Use Git for Windows or GitHub Desktop to clone, then `cd` into the folder in Terminal or PowerShell.

2) Set Up Python
- Create a virtual environment:
  - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
  - Windows PowerShell: `py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1`
    - If activation is blocked, run PowerShell as Administrator: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then retry activation.
- Install Python dependencies:
  - `cd x987-app`
  - `pip install -r requirements.txt`
- Install Playwright Chromium (required for scraping):
  - `python -m playwright install chromium`
  - Linux only (installs system libraries Playwright needs): `python -m playwright install-deps`

3) Check Your Environment (Optional but Recommended)
- `python -m x987 doctor`
  - You should see a success message. If not, read the error; typical fixes are re-running Playwright install or confirming Python version.

4) Run the Pipeline (Generates Data)
- From `x987-app` (with your venv activated):
  - `python -m x987 pipeline --headful`
  - First run can take several minutes (browser opens for scraping). Subsequent runs are faster.
- Where to find results:
  - CSVs appear under `x987-app/x987-data/results/` (e.g., `ranking_main_YYYYMMDD_HHMMSS.csv`).

5) Start the API (Serves the CSVs)
- Open a new terminal window/tab and go to the repo root.
- `cd x987-web/apps/api`
- `npm install && npm run build`
- `node dist/index.js`
- Expected output: “x987 API listening on http://localhost:4000”.
- Quick test: `curl http://localhost:4000/api/health` (should return `{ ok: true }`).
  - If you see a 404 for ranking later, it means the API can’t find CSVs yet — ensure step 4 completed successfully.

6) Start the Frontend (UI)
- In another terminal tab:
- `cd x987-web/apps/fe`
- `npm install && npm run dev`
- Open the local URL printed by Vite (usually http://localhost:5173). The UI will call the API at port 4000.

7) What “Done” Looks Like
- You can visit the UI, see rows, filter/sort, and details load.
- The API returns JSON at:
  - `http://localhost:4000/api/health`
  - `http://localhost:4000/api/ranking/latest`

Common Issues and Fixes
- Python not found or old version:
  - Try `python3` instead of `python`. On Windows use `py -3.11`.
- Playwright errors (browser fails to launch):
  - Re-run `python -m playwright install chromium`.
  - On Linux also run `python -m playwright install-deps`.
- No CSVs / FE shows no data:
  - Ensure step 4 completed; check `x987-app/x987-data/results/` has files.
- API port in use (4000):
  - Stop the other process or run `PORT=4001 node dist/index.js` and use that port.
- FE can’t reach API:
  - Make sure the API terminal shows it’s listening. Restart FE after API is up.
- Windows PowerShell venv activation blocked:
  - Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once, then re-activate.

Next Steps
- Tweak search URLs and options in `x987-config/config.toml`.
- Add a generation catalog at `x987-data/metadata/generation_catalog.json` to enrich the UI.

Where to Get Help
- See `REPO_STATUS.md` and `RESUME_GUIDE.md` for context and a shorter “resume” flow.
