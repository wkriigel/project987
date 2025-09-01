import type { RankingRecord } from './types'
import { normalizeModelTrim, toInt } from './format'

export type GenerationItem = {
  key: string // unique key for filtering, e.g., 'bx-987.1', '911-996'
  code: string // display code like '987.1'
  label: string // full label with years
  years: { min: number; max?: number }
  models: string[] // normalized model tags used for filtering logic
}

export type GenerationGroup = {
  label: string
  items: GenerationItem[]
}

// Canonical catalog (raw data provided), grouped by model family
export const GENERATION_CATALOG: GenerationGroup[] = [
  {
    label: 'Boxster/Cayman',
    items: [
      { key: 'bx-986', code: '986', label: '986 (1997-2004)', years: { min: 1997, max: 2004 }, models: ['boxster', 'cayman'] },
      { key: 'bx-987.1', code: '987.1', label: '987.1 (2005-2008)', years: { min: 2005, max: 2008 }, models: ['boxster', 'cayman'] },
      { key: 'bx-987.2', code: '987.2', label: '987.2 (2009-2012)', years: { min: 2009, max: 2012 }, models: ['boxster', 'cayman'] },
      { key: 'bx-981', code: '981', label: '981 (2013-2016)', years: { min: 2013, max: 2016 }, models: ['boxster', 'cayman'] },
      { key: 'bx-982/718', code: '982 / 718', label: '982 / 718 (2017-2025)', years: { min: 2017, max: 2025 }, models: ['boxster', 'cayman', '718'] }
    ]
  },
  {
    label: '911',
    items: [
      { key: '911-996', code: '996', label: '996 (1999-2004)', years: { min: 1999, max: 2004 }, models: ['911'] },
      { key: '911-997.1', code: '997.1', label: '997.1 (2005-2008)', years: { min: 2005, max: 2008 }, models: ['911'] },
      { key: '911-997.2', code: '997.2', label: '997.2 (2009-2012)', years: { min: 2009, max: 2012 }, models: ['911'] },
      { key: '911-991.1', code: '991.1', label: '991.1 (2012-2016)', years: { min: 2012, max: 2016 }, models: ['911'] },
      { key: '911-991.2', code: '991.2', label: '991.2 (2017-2019)', years: { min: 2017, max: 2019 }, models: ['911'] },
      { key: '911-992', code: '992', label: '992 (2020-2025)', years: { min: 2020, max: 2025 }, models: ['911'] }
    ]
  },
  {
    label: 'Cayenne',
    items: [
      { key: 'cayenne-955/957', code: '955/957', label: '955/957 (2003-2010)', years: { min: 2003, max: 2010 }, models: ['cayenne'] },
      { key: 'cayenne-958.1', code: '958.1', label: '958.1 (2011-2014)', years: { min: 2011, max: 2014 }, models: ['cayenne'] },
      { key: 'cayenne-958.2', code: '958.2', label: '958.2 (2015-2018)', years: { min: 2015, max: 2018 }, models: ['cayenne'] },
      { key: 'cayenne-9Y0', code: '9Y0', label: '9Y0 (2019-2025)', years: { min: 2019, max: 2025 }, models: ['cayenne'] }
    ]
  },
  {
    label: 'Panamera',
    items: [
      { key: 'panamera-970.1', code: '970.1', label: '970.1 (2010-2013)', years: { min: 2010, max: 2013 }, models: ['panamera'] },
      { key: 'panamera-970.2', code: '970.2', label: '970.2 (2014-2016)', years: { min: 2014, max: 2016 }, models: ['panamera'] },
      { key: 'panamera-971.1', code: '971.1', label: '971.1 (2017-2020)', years: { min: 2017, max: 2020 }, models: ['panamera'] },
      { key: 'panamera-971.2', code: '971.2', label: '971.2 (2021-2025)', years: { min: 2021, max: 2025 }, models: ['panamera'] }
    ]
  },
  {
    label: 'Macan',
    items: [
      { key: 'macan-95B.1', code: '95B.1', label: '95B.1 (2015-2018)', years: { min: 2015, max: 2018 }, models: ['macan'] },
      { key: 'macan-95B.2', code: '95B.2', label: '95B.2 (2019-2023)', years: { min: 2019, max: 2023 }, models: ['macan'] },
      { key: 'macan-95B.3', code: '95B.3', label: '95B.3 (2024-2025 gas)', years: { min: 2024, max: 2025 }, models: ['macan'] },
      { key: 'macan-ev-2025-', code: 'Macan EV', label: 'Macan EV (2025-)', years: { min: 2025 }, models: ['macan'] }
    ]
  },
  {
    label: 'Taycan',
    items: [
      { key: 'taycan-9J1', code: '9J1', label: '9J1 (2020-2025)', years: { min: 2020, max: 2025 }, models: ['taycan'] }
    ]
  }
]

export function generationOptionsMinimal() {
  // For the current UI step: Boxster/Cayman -> 987.1/987.2, and 911 -> 996
  return [
    { label: 'All', value: 'all' },
    {
      label: 'Boxster/Cayman',
      options: GENERATION_CATALOG.find(g => g.label === 'Boxster/Cayman')!.items
        .filter(i => ['987.1', '987.2'].includes(i.code))
        .map(i => ({ label: i.label, value: i.key }))
    },
    {
      label: '911',
      options: GENERATION_CATALOG.find(g => g.label === '911')!.items
        .filter(i => i.code === '996')
        .map(i => ({ label: i.label, value: i.key }))
    }
  ]
}

export function findGenerationByKey(key: string) {
  for (const grp of GENERATION_CATALOG) {
    for (const item of grp.items) {
      if (item.key === key) return item
    }
  }
  return undefined
}

function countForGenerationItem(item: GenerationItem, data: RankingRecord[]): number {
  let count = 0
  for (const r of data || []) {
    const y = toInt(r.year)
    if (y == null) continue
    if (item.years.min != null && y < item.years.min) continue
    if (item.years.max != null && y > item.years.max) continue
    const mt = normalizeModelTrim(((r.model || '') + ' ' + (r.trim || '')).trim()).toLowerCase()
    if (!item.models.some(tag => mt.includes(tag))) continue
    count++
  }
  return count
}

function formatYears(y: { min: number; max?: number }) {
  return y.max != null ? `${y.min}-${y.max}` : `${y.min}-`
}

export function generationOptionsAll(data: RankingRecord[]) {
  const withCounts = GENERATION_CATALOG.map(group => ({
    label: group.label,
    options: group.items.map(item => ({
      label: `${item.code} [${formatYears(item.years)}] (${countForGenerationItem(item, data)})`,
      value: item.key
    }))
  }))

  const total = (data || []).reduce((acc, r) => acc + (toInt(r.year) != null ? 1 : 0), 0)
  return [
    { label: `All (${total})`, value: 'all' },
    ...withCounts
  ]
}
