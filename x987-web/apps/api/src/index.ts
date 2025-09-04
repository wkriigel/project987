import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { parseCsvToJson } from './utils/csv';
import { findResultsDir, findConfigPath, findLatestRankingCsv, findGenerationCatalogJson } from './utils/fsPaths';

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, time: new Date().toISOString() });
});

app.get('/api/ranking/latest', (_req, res) => {
  // Allow explicit file override
  const override = process.env.RANKING_FILE
  if (override && fs.existsSync(override)) {
    try {
      const csv = fs.readFileSync(override, 'utf-8')
      const data = parseCsvToJson(csv)
      return res.json({ filename: path.basename(override), path: override, count: data.length, data })
    } catch (e: any) {
      return res.status(500).json({ error: e?.message || 'read/parse error', file: override })
    }
  }
  const dir = findResultsDir();
  if (!dir) return res.status(404).json({ error: 'results directory not found' });
  const file = findLatestRankingCsv(dir);
  if (!file) return res.status(404).json({ error: 'no ranking CSV found', searched: dir });
  try {
    console.log('[x987-api] Results dir:', dir);
    console.log('[x987-api] Using file:', file);
    const csv = fs.readFileSync(file, 'utf-8');
    const data = parseCsvToJson(csv);
    res.json({ filename: path.basename(file), path: file, count: data.length, data });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'read/parse error', file });
  }
});

app.get('/api/config', (_req, res) => {
  const cfg = findConfigPath();
  if (!cfg) return res.status(404).json({ error: 'config.toml not found' });
  try {
    const toml = fs.readFileSync(cfg, 'utf-8');
    res.json({ path: cfg, toml });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'config read error' });
  }
});

app.put('/api/config', (req, res) => {
  const cfg = findConfigPath();
  if (!cfg) return res.status(404).json({ error: 'config.toml not found' });
  const body = req.body || {};
  const toml = typeof body.toml === 'string' ? body.toml : null;
  if (!toml) return res.status(400).json({ error: 'toml string required' });
  try {
    const dir = path.dirname(cfg);
    const backupName = `config.backup_${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14)}.toml`;
    fs.copyFileSync(cfg, path.join(dir, backupName));
    fs.writeFileSync(cfg, toml, 'utf-8');
    res.json({ ok: true, backup: backupName });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'config write error' });
  }
});

// Generation catalog for FE: trims and options per generation
// Source of truth: a generated JSON file produced from Python config (if available).
// If not present, respond with a defaults flag so FE can show placeholder text.
app.get('/api/catalog/generations', (_req, res) => {
  const p = findGenerationCatalogJson();
  if (!p) return res.json({ ok: true, source: 'defaults', data: { models: [] } });
  try {
    const raw = fs.readFileSync(p, 'utf-8');
    const data = JSON.parse(raw);
    return res.json({ ok: true, source: 'json', path: p, data });
  } catch (e: any) {
    return res.status(500).json({ ok: false, error: e?.message || 'catalog read error' });
  }
});

const PORT = process.env.PORT ? Number(process.env.PORT) : 4000;

export function startServer(port: number = PORT) {
  const server = app.listen(port, () => {
    console.log(`x987 API listening on http://localhost:${port}`);
  });
  server.on('error', (err) => {
    console.error('API server error:', err);
  });
  return server;
}

// Only start the server when this file is executed directly
// (In tests, we import { app } and call startServer on an ephemeral port.)
// eslint-disable-next-line @typescript-eslint/no-var-requires
const reqAny: any = typeof require !== 'undefined' ? require : null;
if (reqAny && reqAny.main === module) {
  startServer(PORT);
}

export { app };
