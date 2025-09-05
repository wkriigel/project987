import { useEffect, useMemo, useRef, useState } from 'react'
import { Layout, Tabs, Table, Typography, Space, Spin, Card, ConfigProvider, Input, InputNumber, Select, Segmented } from 'antd'
import axios from 'axios'
import type { ColumnsType } from 'antd/es/table'
import type { RankingRecord, RankingResponse } from './lib/types'
import { priceK, milesK, normalizeModelTrim, shortHost, toInt, optionsCompact } from './lib/format'
import { isEarlyYearDim, isMilesHighlighted, isModelCellHighlighted, isMsrpHighlighted, isPriceHighlighted } from './lib/highlight'
import { roles } from './design/tokens/roles'
import { SummaryHeader } from './components/SummaryHeader'
import { Chip } from './components/Chip'
import { ThresholdChip } from './components/ThresholdChip'
import { thresholdSpecs, toLevelFromSpec } from './design/thresholds'
import { facetCounts, tagsForRecord } from './lib/options'
import { PaintChipExterior, PaintChipInterior } from './components/PaintChip'
import { extractPaintFromRecord } from './design/paint/normalize'
import { FilterSelect } from './components/FilterSelect'
import { applyGenerationFilter } from './lib/filters'
import type { GenerationValue } from './lib/filters'
import { generationOptionsAll } from './lib/generation'

const { Header, Content } = Layout
const { Text, Link } = Typography

export function App() {
  const [data, setData] = useState<RankingRecord[]>([])
  const [filename, setFilename] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const ymtInputRef = useRef<HTMLInputElement | null>(null)
  const optionFacets = useMemo(() => facetCounts(data), [data])
  const exteriorFacets = useMemo(() => paintFacetCounts('exterior', data), [data])
  const interiorFacets = useMemo(() => paintFacetCounts('interior', data), [data])
  const [generation, setGeneration] = useState<GenerationValue>('all')
  const [genCatalog, setGenCatalog] = useState<any | null>(null)
  const [genCatalogStatus, setGenCatalogStatus] = useState<'idle'|'loading'|'ready'|'defaults'|'error'>('idle')

  useEffect(() => {
    let mounted = true
    async function load() {
      try {
        setLoading(true)
        const res = await axios.get<RankingResponse>('/api/ranking/latest')
        if (!mounted) return
        setData(res.data.data)
        setFilename(res.data.filename)
      } catch (e: any) {
        const serverMsg = e?.response?.data?.error
        setError(serverMsg || e?.message || 'Failed to load')
      } finally {
        setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  // Helper to find generation meta by key from API catalog
  function findGenMeta(catalog: any, key: string) {
    try {
      const models: any[] = Array.isArray(catalog?.models) ? catalog.models : []
      for (const m of models) {
        const gens: any[] = Array.isArray(m?.generations) ? m.generations : []
        for (const g of gens) {
          if (g?.key === key) return g
        }
      }
    } catch {}
    return undefined
  }

  // Merge generations from catalog for the selected UI key (e.g., 'bx-987.2')
  function getMergedGenerationMeta(catalog: any, selKey: string) {
    const models: any[] = Array.isArray(catalog?.models) ? catalog.models : []
    const dash = selKey.indexOf('-')
    if (dash < 0) return undefined
    const family = selKey.slice(0, dash).toLowerCase()
    let code = selKey.slice(dash + 1)
    // Normalize FE selection codes to JSON codes
    //  - FE uses '982/718' for Boxster/Cayman; JSON uses '982'
    if (code.toLowerCase() === '982/718' || code.toLowerCase() === '982 / 718') code = '982'
    const familiesToModels: Record<string, string[]> = {
      'bx': ['Boxster', 'Cayman'],
      '911': ['911'],
      'cayenne': ['Cayenne'],
      'panamera': ['Panamera'],
      'macan': ['Macan'],
      'taycan': ['Taycan']
    }
    const targetModels = familiesToModels[family] || []
    const trimsSet = new Set<string>()
    const optionsMap = new Map<string, { display: string; msrp?: number }>()
    let anyDefault = true
    for (const m of models) {
      if (!targetModels.includes(String(m?.name || ''))) continue
      const gens: any[] = Array.isArray(m?.generations) ? m.generations : []
      for (const g of gens) {
        if (String(g?.code || '') !== code) continue
        const gtrims: string[] = Array.isArray(g?.trims) ? g.trims : []
        gtrims.forEach(t => { if (t) trimsSet.add(String(t)) })
        const gopts: any[] = Array.isArray(g?.options) ? g.options : []
        if (gopts.length) anyDefault = false
        gopts.forEach((o: any) => {
          const id = (o?.id || o?.display || '').toString()
          if (!id) return
          if (!optionsMap.has(id)) optionsMap.set(id, { display: (o?.display || id), msrp: typeof o?.msrp === 'number' ? o.msrp : undefined })
        })
      }
    }
    return {
      trims: Array.from(trimsSet),
      options: Array.from(optionsMap.values()).map(o => ({ display: o.display, msrp: o.msrp })),
      options_default: anyDefault
    }
  }

  // Load generation catalog (if provided by API); else we show defaults notice
  useEffect(() => {
    let mounted = true
    async function loadCatalog() {
      try {
        setGenCatalogStatus('loading')
        const res = await fetch('/api/catalog/generations')
        const json = await res.json().catch(() => ({}))
        if (!mounted) return
        if (json && json.ok && json.source === 'json') {
          setGenCatalog(json.data || null)
          setGenCatalogStatus('ready')
        } else {
          setGenCatalog(null)
          setGenCatalogStatus('defaults')
        }
      } catch {
        if (!mounted) return
        setGenCatalog(null)
        setGenCatalogStatus('error')
      }
    }
    loadCatalog()
    return () => { mounted = false }
  }, [])

  const columns: ColumnsType<RankingRecord> = useMemo(() => [
    {
      title: 'Year',
      key: 'year',
      width: 90,
      sorter: (a,b) => (toInt(a.year)||0) - (toInt(b.year)||0),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => { try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} } })() as { min?: number; max?: number }
        return (
          <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
            <InputNumber
              placeholder="Min"
              value={curr.min}
              onChange={(val) => { const next = { ...curr, min: val == null ? undefined : Number(val) }; setSelectedKeys([JSON.stringify(next)]); confirm({ closeDropdown: false }) }}
              style={{ width: 120, marginBottom: 8, display: 'block' }}
            />
            <InputNumber
              placeholder="Max"
              value={curr.max}
              onChange={(val) => { const next = { ...curr, max: val == null ? undefined : Number(val) }; setSelectedKeys([JSON.stringify(next)]); confirm({ closeDropdown: false }) }}
              style={{ width: 120, marginBottom: 8, display: 'block' }}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (<span style={{ color: filtered ? '#1677ff' : undefined }}>🗓️</span>),
      onFilter: (value, rec) => {
        let range: { min?: number; max?: number } = {}
        try { range = JSON.parse(String(value)) } catch {}
        const v = toInt(rec.year)
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const y = toInt(r.year)
        const dimYear = isEarlyYearDim(r)
        return <Chip text={y ?? ''} dim={dimYear} />
      }
    },
    {
      title: 'Model/Trim',
      key: 'modeltrim',
      sorter: (a,b) => (
        normalizeModelTrim(((a.model || '') + ' ' + (a.trim || '')).trim()) || ''
      ).localeCompare(
        normalizeModelTrim(((b.model || '') + ' ' + (b.trim || '')).trim()) || ''
      ),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
        <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
          <Input
            ref={ymtInputRef}
            placeholder="Search model/trim"
            value={(selectedKeys as React.Key[])[0] as string}
            onChange={(e) => { const val = e.target.value; setSelectedKeys(val ? [val] : []); confirm({ closeDropdown: false }) }}
            onPressEnter={() => confirm()}
            style={{ marginBottom: 8, display: 'block' }}
          />
          <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
        </div>
      ),
      filterIcon: (filtered: boolean) => (<span style={{ color: filtered ? '#1677ff' : undefined }}>🔎</span>),
      onFilter: (value, rec) => {
        const mt = normalizeModelTrim(((rec.model || '') + ' ' + (rec.trim || '')).trim())
        const s = (mt || '').toLowerCase()
        return s.includes(String(value).toLowerCase())
      },
      onFilterDropdownOpenChange: (open) => { if (open) setTimeout(() => ymtInputRef.current?.select(), 100) },
      render: (_, r) => {
        const mt = normalizeModelTrim(((r.model || '') + ' ' + (r.trim || '')).trim())
        return <span className="text-xs md:text-sm">{mt}</span>
      }
    },
    {
      title: 'Price',
      key: 'price',
      align: 'right',
      sorter: (a,b) => (toInt(a.asking_price_usd)||0) - (toInt(b.asking_price_usd)||0),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => {
          try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} }
        })() as { min?: number; max?: number }
        return (
          <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
            <InputNumber
              placeholder="Min"
              value={curr.min}
              onChange={(val) => {
                const next = { ...curr, min: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <InputNumber
              placeholder="Max"
              value={curr.max}
              onChange={(val) => {
                const next = { ...curr, max: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (
        <span style={{ color: filtered ? '#1677ff' : undefined }}>≤ ≥</span>
      ),
      onFilter: (value, rec) => {
        let range: { min?: number; max?: number } = {}
        try { range = JSON.parse(String(value)) } catch {}
        const v = toInt(rec.asking_price_usd)
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const price = toInt(r.asking_price_usd)
        const text = priceK(price)
        const level = toLevelFromSpec(price, thresholdSpecs.price)
        return <ThresholdChip color="teal" level={level} text={text} size="full" />
      }
    },
    {
      title: 'Miles',
      key: 'miles',
      align: 'right',
      sorter: (a,b) => (toInt(a.mileage)||0) - (toInt(b.mileage)||0),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => {
          try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} }
        })() as { min?: number; max?: number }
        return (
          <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
            <InputNumber
              placeholder="Min"
              value={curr.min}
              onChange={(val) => {
                const next = { ...curr, min: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <InputNumber
              placeholder="Max"
              value={curr.max}
              onChange={(val) => {
                const next = { ...curr, max: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (
        <span style={{ color: filtered ? '#1677ff' : undefined }}>≤ ≥</span>
      ),
      onFilter: (value, rec) => {
        let range: { min?: number; max?: number } = {}
        try { range = JSON.parse(String(value)) } catch {}
        const v = toInt(rec.mileage)
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const miles = toInt(r.mileage)
        const text = milesK(miles)
        const level = toLevelFromSpec(miles, thresholdSpecs.miles)
        return <ThresholdChip color="teal" level={level} text={text} size="full" />
      }
    },
    {
      title: 'MSRP',
      key: 'msrp',
      align: 'right',
      sorter: (a,b) => (toInt(a.total_options_msrp)||0) - (toInt(b.total_options_msrp)||0),
      defaultSortOrder: 'descend',
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => {
          try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} }
        })() as { min?: number; max?: number }
        return (
          <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
            <InputNumber
              placeholder="Min"
              value={curr.min}
              onChange={(val) => {
                const next = { ...curr, min: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <InputNumber
              placeholder="Max"
              value={curr.max}
              onChange={(val) => {
                const next = { ...curr, max: val == null ? undefined : Number(val) }
                setSelectedKeys([JSON.stringify(next)])
                confirm({ closeDropdown: false })
              }}
              style={{ width: 140, marginBottom: 8, display: 'block' }}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (
        <span style={{ color: filtered ? '#1677ff' : undefined }}>≤ ≥</span>
      ),
      onFilter: (value, rec) => {
        let range: { min?: number; max?: number } = {}
        try { range = JSON.parse(String(value)) } catch {}
        const v = toInt(rec.total_options_msrp)
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const msrp = toInt(r.total_options_msrp)
        const text = msrp != null ? priceK(msrp) : ''
        const level = toLevelFromSpec(msrp, thresholdSpecs.msrp)
        return <ThresholdChip color="green" level={level} text={text} size="full" />
      }
    },
    {
      title: 'Options',
      key: 'opts',
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => {
          try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} }
        })() as { tags?: string[]; mode?: 'and' | 'or' }
        const tags = curr.tags || []
        const mode = curr.mode || 'and'
        const onChange = (nextTags: string[]) => {
          setSelectedKeys([JSON.stringify({ tags: nextTags, mode })])
          confirm({ closeDropdown: false })
        }
        const onMode = (nextMode: 'and' | 'or') => {
          setSelectedKeys([JSON.stringify({ tags, mode: nextMode })])
          confirm({ closeDropdown: false })
        }
        return (
          <div style={{ padding: 8, width: 240 }} onKeyDown={(e) => e.stopPropagation()}>
            <div style={{ marginBottom: 8 }}>
              <Segmented
                options={[{ label: 'AND', value: 'and' }, { label: 'OR', value: 'or' }]}
                value={mode}
                onChange={val => onMode(val as 'and' | 'or')}
                size="small"
              />
            </div>
            <Select
              mode="multiple"
              allowClear
              placeholder="Select options"
              value={tags}
              onChange={onChange}
              style={{ width: '100%', marginBottom: 8 }}
              notFoundContent="No options"
              options={optionFacets.map(f => ({ value: f.tag, label: `${f.tag} (${f.count})` }))}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (
        <span style={{ color: filtered ? '#1677ff' : undefined }}>☑︎</span>
      ),
      onFilter: (value, rec) => {
        let payload: { tags?: string[]; mode?: 'and' | 'or' } = {}
        try { payload = JSON.parse(String(value)) } catch {}
        const chosen = payload.tags || []
        const mode = payload.mode || 'and'
        if (chosen.length === 0) return true
        const tags = tagsForRecord(rec)
        if (mode === 'and') return chosen.every(t => tags.has(t))
        return chosen.some(t => tags.has(t))
      },
      render: (_, r) => {
        const txt = optionsCompact(r.options_list)
        return txt || '(no options detected)'
      }
    },
    {
      title: 'Exterior',
      key: 'exterior',
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => { try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} } })() as { tags?: string[] }
        const tags = curr.tags || []
        const onChange = (vals: string[]) => { setSelectedKeys([JSON.stringify({ tags: vals })]); confirm({ closeDropdown: false }) }
        return (
          <div style={{ padding: 8, width: 240 }} onKeyDown={(e) => e.stopPropagation()}>
            <Select
              mode="multiple"
              allowClear
              placeholder="Select exterior colors"
              value={tags}
              onChange={onChange}
              style={{ width: '100%', marginBottom: 8 }}
              options={exteriorFacets.map(f => ({ value: f.key, label: `${f.label} (${f.count})` }))}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (<span style={{ color: filtered ? '#1677ff' : undefined }}>☑︎</span>),
      onFilter: (value, rec) => {
        let payload: { tags?: string[] } = {}
        try { payload = JSON.parse(String(value)) } catch {}
        const chosen = payload.tags || []
        if (chosen.length === 0) return true
        const exInfo = extractPaintFromRecord('exterior', rec)
        const key = (exInfo.name || exInfo.hex || '').toString().trim().toLowerCase()
        return chosen.includes(key)
      },
      render: (_, r) => {
        const exInfo = extractPaintFromRecord('exterior', r)
        const exName = (exInfo.name as any) || ''
        return (
          <PaintChipExterior
            name={exName}
            hex={exInfo.hex}
            label={exName || exInfo.hex || '—'}
            size="md"
            className="w-full min-w-0 overflow-hidden whitespace-nowrap text-ellipsis"
          />
        )
      }
    },
    {
      title: 'Interior',
      key: 'interior',
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        const curr = (() => { try { return JSON.parse((selectedKeys as any)?.[0] || '{}') } catch { return {} } })() as { tags?: string[] }
        const tags = curr.tags || []
        const onChange = (vals: string[]) => { setSelectedKeys([JSON.stringify({ tags: vals })]); confirm({ closeDropdown: false }) }
        return (
          <div style={{ padding: 8, width: 240 }} onKeyDown={(e) => e.stopPropagation()}>
            <Select
              mode="multiple"
              allowClear
              placeholder="Select interior colors"
              value={tags}
              onChange={onChange}
              style={{ width: '100%', marginBottom: 8 }}
              options={interiorFacets.map(f => ({ value: f.key, label: `${f.label} (${f.count})` }))}
            />
            <a onClick={() => { clearFilters?.(); confirm() }}>Reset</a>
          </div>
        )
      },
      filterIcon: (filtered: boolean) => (<span style={{ color: filtered ? '#1677ff' : undefined }}>☑︎</span>),
      onFilter: (value, rec) => {
        let payload: { tags?: string[] } = {}
        try { payload = JSON.parse(String(value)) } catch {}
        const chosen = payload.tags || []
        if (chosen.length === 0) return true
        const inInfo = extractPaintFromRecord('interior', rec)
        const key = (inInfo.name || inInfo.hex || '').toString().trim().toLowerCase()
        return chosen.includes(key)
      },
      render: (_, r) => {
        const inInfo = extractPaintFromRecord('interior', r)
        const inName = (inInfo.name as any) || ''
        return (
          <PaintChipInterior
            name={inName}
            hex={inInfo.hex}
            label={inName || inInfo.hex || '—'}
            size="md"
            className="w-full min-w-0 overflow-hidden whitespace-nowrap text-ellipsis"
          />
        )
      }
    },
    {
      title: 'Source',
      key: 'src',
      render: (_, r) => {
        const url = r.listing_url || r.source_url
        const host = shortHost(url)
        return url ? <a href={url} target="_blank" rel="noreferrer">{host}</a> : ''
      }
    }
  ], [optionFacets])

  const filtered = useMemo(() => applyGenerationFilter(data, generation), [data, generation])
  const genOptions = useMemo(() => generationOptionsAll(data), [data])
  const summary = useMemo(() => {
    const displayed = filtered.filter(r => toInt(r.year) != null)
    const unknown = data.filter(r => toInt(r.year) == null)
    return { displayedCount: displayed.length, unknown }
  }, [data, filtered])

  const [page, setPage] = useState<{ current: number; pageSize: number }>({ current: 1, pageSize: 20 })

  const items = [
    {
      key: 'results',
      label: 'Results',
      children: (
        <div className="p-3">
          <Space direction="vertical" size="middle" className="w-full">
            <SummaryHeader
              displayedCount={summary.displayedCount}
              filename={filename}
              unknownLinks={summary.unknown.map(r => (r.listing_url || r.source_url || "")).filter(Boolean)}
            />

            {/* Top-of-table controls */}
            <div className="flex flex-wrap gap-3 items-end">
              <FilterSelect
                label="Generation"
                value={generation}
                onChange={(v) => setGeneration(String(v) as GenerationValue)}
                className="w-full sm:w-[420px] md:w-[560px]"
                options={genOptions}
              />
            </div>

            {/* Minimal, plain-text generation metadata display */}
            {generation !== 'all' && (
              <div className="mt-2 text-xs md:text-sm">
                {/* Trims line */}
                <div>
                  <strong>Trims:</strong>{' '}
                  {(() => {
                    try {
                      if (genCatalogStatus === 'ready' && genCatalog) {
                        const merged = getMergedGenerationMeta(genCatalog, String(generation))
                        const trims = merged?.trims || []
                        if (trims.length) return trims.join(', ')
                        return '(defaults pending)'
                      }
                      return '(defaults pending)'
                    } catch { return '(defaults pending)' }
                  })()}
                </div>
                {/* Options line */}
                <div>
                  <strong>Options:</strong>{' '}
                  {(() => {
                    try {
                      if (genCatalogStatus === 'ready' && genCatalog) {
                        const merged = getMergedGenerationMeta(genCatalog, String(generation))
                        const opts = (merged?.options || []).map((o: any) => {
                          if (typeof o === 'string') return o
                          const name = (o?.display || o?.id || '').toString().trim()
                          const msrp = typeof o?.msrp === 'number' ? `$${o.msrp.toLocaleString()}` : null
                          return msrp ? `${name} (${msrp})` : name
                        }).filter(Boolean)
                        if (opts.length) {
                          return opts.join(', ')
                        }
                        return '(defaults pending)'
                      }
                      return '(defaults pending)'
                    } catch { return '(defaults pending)' }
                  })()}
                </div>
                {(() => {
                  try {
                    if (genCatalogStatus === 'ready' && genCatalog) {
                      const merged = getMergedGenerationMeta(genCatalog, String(generation))
                      if (merged?.options_default) return <div>(Using defaults for options)</div>
                      return null
                    }
                    return null
                  } catch { return null }
                })()}
                {genCatalogStatus !== 'ready' && (
                  <div>(Using defaults; generation metadata not yet implemented)</div>
                )}
              </div>
            )}

            {loading ? <Spin/> : error ? <Text type="danger">{error}</Text> : (
              <Table
                size="small"
                rowKey={(r) => (
                  r.listing_url ||
                  r.source_url ||
                  `${toInt(r.year) || 0}-${normalizeModelTrim(((r.model || '') + ' ' + (r.trim || '')).trim()) || ''}-${toInt(r.asking_price_usd) || 0}-${toInt(r.mileage) || 0}`
                )}
                columns={columns}
                dataSource={filtered.filter(r => toInt(r.year) != null)}
                pagination={{ current: page.current, pageSize: page.pageSize }}
                onChange={(pag) => setPage({ current: pag?.current ?? 1, pageSize: pag?.pageSize ?? 20 })}
              />
            )}
          </Space>
        </div>
      )
    },
    {
      key: 'controls',
      label: 'Controls',
      children: (
        <div className="p-3">
          <Space direction="vertical" size="middle" className="w-full">
            <Card title="Config (read-only skeleton)">
              <Text type="secondary">This tab will load and edit config.toml. (Scaffolded)</Text>
            </Card>
            <Card title="Generation Catalog (readable)">
              {genCatalogStatus === 'ready' && genCatalog ? (
                <div className="text-xs md:text-sm whitespace-pre-wrap">
                  {Array.isArray(genCatalog?.models) && genCatalog.models.length > 0 ? (
                    genCatalog.models.map((m: any) => (
                      <div key={String(m?.name || Math.random())} style={{ marginBottom: 8 }}>
                        <div><strong>Model:</strong> {String(m?.name || '')}</div>
                        {Array.isArray(m?.generations) && m.generations.length > 0 ? (
                          m.generations.map((g: any) => {
                            const years = g?.years || {}
                            const yr = [years?.min, years?.max].filter((v: any) => v != null).join('-')
                            const trims: string[] = Array.isArray(g?.trims) ? g.trims : []
                            const opts: any[] = Array.isArray(g?.options) ? g.options : []
                            const optsText = opts.length
                              ? opts.map(o => {
                                  const name = (o?.display || o?.id || '').toString().trim()
                                  const msrp = typeof o?.msrp === 'number' ? `$${o.msrp.toLocaleString()}` : null
                                  return msrp ? `${name} (${msrp})` : name
                                }).join(', ')
                              : '(defaults pending)'
                            return (
                              <div key={String(g?.key || `${m?.name}-${g?.code}`)} style={{ marginLeft: 12, marginTop: 4 }}>
                                <div>• {String(g?.code || '')} [{yr}]</div>
                                <div style={{ marginLeft: 12 }}>Trims: {trims.length ? trims.join(', ') : '(none)'}</div>
                                <div style={{ marginLeft: 12 }}>Options: {optsText}</div>
                              </div>
                            )
                          })
                        ) : (
                          <div style={{ marginLeft: 12 }}>(no generations)</div>
                        )}
                      </div>
                    ))
                  ) : (
                    <Text type="secondary">No catalog data</Text>
                  )}
                </div>
              ) : genCatalogStatus === 'defaults' ? (
                <Text type="secondary">(defaults) Run the pipeline to export generation_catalog.json</Text>
              ) : genCatalogStatus === 'loading' ? (
                <Text type="secondary">Loading…</Text>
              ) : (
                <Text type="danger">Failed to load catalog</Text>
              )}
            </Card>
          </Space>
        </div>
      )
    }
  ]

  return (
    <ConfigProvider
      theme={{
        token: {
          colorBgBase: roles.bg.page as string,
          colorBgContainer: roles.bg.surface as string,
          colorTextBase: roles.text.primary as string,
          colorTextSecondary: roles.text.muted as string,
          colorBorder: roles.bg.surfaceAlt as string,
          colorPrimary: roles.accent.teal as string
        },
        components: {
          Table: {
            headerBg: roles.bg.surfaceAlt as string,
            headerColor: roles.text.primary as string,
            rowHoverBg: roles.bg.emphasis as string
          }
        }
      }}
    >
      <Layout style={{ minHeight: '100vh', background: roles.bg.page as string }}>
        <Header style={{ color: roles.text.primary as string, fontWeight: 600, background: roles.bg.surfaceAlt as string }}>x987 Web</Header>
        <Content style={{ background: roles.bg.surface as string }}>
          <Tabs items={items} />
        </Content>
      </Layout>
    </ConfigProvider>
  )
}

function paintFacetCounts(kind: 'exterior'|'interior', data: any[]) {
  const counts = new Map<string, number>()
  for (const r of data || []) {
    const info = extractPaintFromRecord(kind, r)
    const key = (info.name || info.hex || '').toString().trim().toLowerCase()
    if (!key) continue
    counts.set(key, (counts.get(key) || 0) + 1)
  }
  return Array.from(counts.entries())
    .map(([key, count]) => ({ key, label: titleCase(key), count }))
    .sort((a, b) => (b.count - a.count) || a.label.localeCompare(b.label))
}

function titleCase(s: string) {
  return (s || '').split(/\s+/).map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ')
}
