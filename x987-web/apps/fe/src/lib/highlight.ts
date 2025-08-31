import { toInt } from './format'
import type { RankingRecord } from './types'

export function isMilesHighlighted(rec: RankingRecord): boolean {
  const miles = toInt(rec.mileage)
  return miles != null && miles < 70000
}

export function isPriceHighlighted(rec: RankingRecord): boolean {
  const price = toInt(rec.asking_price_usd)
  const miles = toInt(rec.mileage)
  if (price == null || miles == null) return false
  // Mirror CLI idea: bright tiers under 25k and low miles
  return price < 25000 && miles < 90000
}

export function hasComboPasmExhaustLsd(rec: RankingRecord): boolean {
  const text = Array.isArray(rec.options_list)
    ? rec.options_list.join(' ').toLowerCase()
    : String(rec.options_list || '').toLowerCase()
  return (
    text.includes('pasm') || text.includes('adaptive suspension')
  ) && (
    text.includes('pse') || text.includes('sport exhaust') || text.includes('xlf')
  ) && (
    text.includes('lsd') || text.includes('limited slip') || text.includes('220')
  )
}

export function isMsrpHighlighted(rec: RankingRecord): boolean {
  const msrp = toInt(rec.total_options_msrp)
  return (msrp != null && msrp > 3999) || hasComboPasmExhaustLsd(rec)
}

export function isModelCellHighlighted(rec: RankingRecord): boolean {
  const y = toInt(rec.year)
  return (y != null && y >= 2009) && isPriceHighlighted(rec) && isMilesHighlighted(rec) && isMsrpHighlighted(rec)
}

export function isEarlyYearDim(rec: RankingRecord): boolean {
  const y = toInt(rec.year)
  return y != null && (y === 2005 || y === 2006 || y === 2007 || y === 2008)
}

