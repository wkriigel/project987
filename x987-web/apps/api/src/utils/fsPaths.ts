import path from 'path';
import fs from 'fs';

function ascendCandidates(relatives: string[]): string | null {
  for (let i = 0; i < 6; i++) {
    const base = path.resolve(process.cwd(), Array(i).fill('..').join(path.sep) || '.')
    for (const rel of relatives) {
      const p = path.join(base, rel)
      if (fs.existsSync(p)) return p
    }
  }
  return null
}

export function listAscendCandidates(relatives: string[]): string[] {
  const out: string[] = []
  for (let i = 0; i < 6; i++) {
    const base = path.resolve(process.cwd(), Array(i).fill('..').join(path.sep) || '.')
    for (const rel of relatives) {
      out.push(path.join(base, rel))
    }
  }
  return out
}

export function findResultsDir(): string | null {
  // Allow explicit override
  const envDir = process.env.RANKING_RESULTS_DIR
  if (envDir && fs.existsSync(envDir)) return envDir
  // Default: prefer the active app results dir to avoid confusion with old paths
  return ascendCandidates([
    // Canonical top-level data directory
    path.join('x987-data', 'results'),
    // Legacy (older paths kept as fallback)
    path.join('x987-app', 'x987-data', 'results')
  ])
}

export function resultsDirCandidates(): string[] {
  const rels = [
    path.join('x987-data', 'results'),
    path.join('x987-app', 'x987-data', 'results')
  ]
  const envDir = process.env.RANKING_RESULTS_DIR
  const list = listAscendCandidates(rels)
  return envDir ? [envDir, ...list] : list
}

export function findConfigPath(): string | null {
  return ascendCandidates([
    path.join('x987-config', 'config.toml')
  ])
}

export function findGenerationCatalogJson(): string | null {
  // Look for a generated JSON catalog that FE can consume
  return ascendCandidates([
    // Canonical path first
    path.join('x987-data', 'metadata', 'generation_catalog.json'),
    // Fallbacks (legacy paths)
    path.join('x987-web', 'apps', 'api', 'data', 'generation_catalog.json'),
    path.join('x987-data', 'metadata', 'generations.json')
  ])
}

export function findVinEnrichedJson(): string | null {
  // Prefer top-level metadata location; fallback to local API data dir
  return ascendCandidates([
    path.join('x987-data', 'metadata', 'vin_enriched.json'),
    path.join('x987-web', 'apps', 'api', 'data', 'vin_enriched.json')
  ])
}

export function ensureVinEnrichedPath(): string {
  // Write path preference: top-level metadata directory
  const preferredDir = ascendCandidates([
    path.join('x987-data', 'metadata')
  ]) || path.resolve(process.cwd(), 'x987-data', 'metadata')
  try {
    if (!fs.existsSync(preferredDir)) {
      fs.mkdirSync(preferredDir, { recursive: true })
    }
  } catch {}
  return path.join(preferredDir, 'vin_enriched.json')
}

export function findLatestRankingCsv(dir: string): string | null {
  const all = fs.readdirSync(dir).filter(f => f.toLowerCase().endsWith('.csv')).sort()
  // Prefer ranking_main_*
  const main = all.filter(f => /^ranking_main_\d{8}_\d{6}\.csv$/i.test(f))
  if (main.length) return path.join(dir, main[main.length - 1])
  // Fallback: any ranking_*.csv
  const ranking = all.filter(f => /^ranking_.*\.csv$/i.test(f))
  if (ranking.length) return path.join(dir, ranking[ranking.length - 1])
  // Fallback: transformed_data_*
  const transformed = all.filter(f => /^transformed_data_\d{8}_\d{6}\.csv$/i.test(f))
  if (transformed.length) return path.join(dir, transformed[transformed.length - 1])
  return null
}
