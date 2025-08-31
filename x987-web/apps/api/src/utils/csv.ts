import { parse } from 'csv-parse/sync'

export function parseCsvToJson(csv: string): Record<string, any>[] {
  // Robust CSV parsing with headers, relaxed column counts, and empty line skipping
  const content = csv.replace(/^\uFEFF/, '') // strip BOM if present
  const records = parse(content, {
    columns: true,
    skip_empty_lines: true,
    relax_column_count: true,
    relax_quotes: true,
    trim: true
  }) as Record<string, any>[]
  return records
}
