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

export function findResultsDir(): string | null {
  // Allow explicit override
  const envDir = process.env.RANKING_RESULTS_DIR
  if (envDir && fs.existsSync(envDir)) return envDir
  // Default: prefer the active app results dir to avoid confusion with old paths
  return ascendCandidates([
    path.join('x987-app', 'x987-data', 'results')
  ])
}

export function findConfigPath(): string | null {
  return ascendCandidates([
    path.join('x987-config', 'config.toml')
  ])
}

export function findGenerationCatalogJson(): string | null {
  // Look for a generated JSON catalog that FE can consume
  return ascendCandidates([
    path.join('x987-web', 'apps', 'api', 'data', 'generation_catalog.json'),
    path.join('x987-data', 'metadata', 'generation_catalog.json'),
    path.join('x987-data', 'metadata', 'generations.json')
  ])
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
