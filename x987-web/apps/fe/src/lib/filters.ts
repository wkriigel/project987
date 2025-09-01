import type { RankingRecord } from './types'
import { normalizeModelTrim, toInt } from './format'
import { findGenerationByKey } from './generation'

export type GenerationValue = string // 'all' | generation keys like 'bx-987.1', '911-996'

export function applyGenerationFilter(data: RankingRecord[], gen: GenerationValue): RankingRecord[] {
  if (!gen || gen === 'all') return data
  const spec = findGenerationByKey(String(gen))
  if (!spec) {
    // Fallback: attempt code-only match across catalog by checking code in label
    const code = String(gen)
    const codeRegex = new RegExp(`(^|[^\\d])${code.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![\\d])`, 'i')
    return (data || []).filter((r) => codeRegex.test(`${r.model || ''} ${r.trim || ''} ${r.year || ''}`))
  }

  return (data || []).filter((r) => {
    const y = toInt(r.year)
    if (y == null) return false
    if (spec.years.min != null && y < spec.years.min) return false
    if (spec.years.max != null && y > spec.years.max) return false

    const mt = normalizeModelTrim(((r.model || '') + ' ' + (r.trim || '')).trim()).toLowerCase()
    const present = (spec.models || []).some(tag => mt.includes(tag))
    return present
  })
}
