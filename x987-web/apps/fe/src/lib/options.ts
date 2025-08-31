import type { RankingRecord } from './types'
import { shortenOption } from './format'

export function tagsForRecord(rec: RankingRecord): Set<string> {
  const raw = rec.options_list
  const items = Array.isArray(raw)
    ? raw
    : String(raw || '')
        .split(/[,\n]/)
        .map(s => s.trim())
        .filter(Boolean)
  const tags = new Set<string>()
  for (const it of items) {
    const tag = shortenOption(it)
    if (tag) tags.add(tag)
  }
  return tags
}

export function facetCounts(data: RankingRecord[]): { tag: string; count: number }[] {
  const counts = new Map<string, number>()
  for (const rec of data) {
    for (const tag of tagsForRecord(rec)) {
      counts.set(tag, (counts.get(tag) || 0) + 1)
    }
  }
  return Array.from(counts.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => (b.count - a.count) || a.tag.localeCompare(b.tag))
}

