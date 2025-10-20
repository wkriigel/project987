import { useEffect, useMemo, useRef, useState, useCallback } from 'react'
import type React from 'react'
import type { MouseEvent } from 'react'
import { Layout, Tabs, Table, Typography, Space, Spin, Card, ConfigProvider, Input, InputNumber, Select, Segmented, Button, Tooltip } from 'antd'
import { CopyOutlined, StarFilled, StarOutlined, SortAscendingOutlined, SortDescendingOutlined } from '@ant-design/icons'
import axios from 'axios'
import type { ColumnsType } from 'antd/es/table'
import type { RankingRecord, RankingResponse } from './lib/types'
import { priceK, milesK, normalizeModelTrim, shortHost, toInt, optionsCompact } from './lib/format'
import { isEarlyYearDim, isMilesHighlighted, isModelCellHighlighted, isMsrpHighlighted, isPriceHighlighted } from './lib/highlight'
import { roles } from './design/tokens/roles'
import { palette } from './design/tokens/colors'
import { SummaryHeader } from './components/SummaryHeader'
import { HeaderBar } from './components/HeaderBar'
import { Chip } from './components/Chip'
import { ThresholdChip } from './components/ThresholdChip'
import { thresholdSpecs, toLevelFromSpec } from './design/thresholds'
import { tagsForRecord } from './lib/options'
import { PaintChipExterior, PaintChipInterior } from './components/PaintChip'
import { extractPaintFromRecord, parseInteriorTwoTone } from './design/paint/normalize'
import { FilterSelect } from './components/FilterSelect'
import { applyGenerationFilter } from './lib/filters'
import type { GenerationValue } from './lib/filters'
import { generationOptionsAll } from './lib/generation'
import { BookmarkletModal } from './components/BookmarkletModal'

const { Content } = Layout
const { Text, Link } = Typography

export function App() {
  const [data, setData] = useState<RankingRecord[]>([])
  const [filename, setFilename] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const ymtInputRef = useRef<HTMLInputElement | null>(null)
  const [generation, setGeneration] = useState<GenerationValue>('bx-987.2')
  const [newCount, setNewCount] = useState<number>(0)
  const [recentCount, setRecentCount] = useState<number>(0)
  const [genCatalog, setGenCatalog] = useState<any | null>(null)
  const [genCatalogStatus, setGenCatalogStatus] = useState<'idle'|'loading'|'ready'|'defaults'|'error'>('idle')
  const [vinMap, setVinMap] = useState<Record<string, any>>({})
  const [bmOpen, setBmOpen] = useState(false)
  const [tableFilters, setTableFilters] = useState<Record<string, any[] | null>>({})
  // Favorites (persisted across pipeline updates via localStorage)
  const FAV_STORE_KEY = 'x987_favorites_v1'
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    try {
      const raw = localStorage.getItem(FAV_STORE_KEY)
      const arr: string[] = raw ? JSON.parse(raw) : []
      return new Set(arr.filter(Boolean))
    } catch { return new Set() }
  })
  useEffect(() => {
    try { localStorage.setItem(FAV_STORE_KEY, JSON.stringify(Array.from(favorites))) } catch {}
  }, [favorites])
  // One-time action: mark specific VINs as favorites (simulates manual starring once)
  useEffect(() => {
    try {
      const DONE_KEY = 'x987_seed_favs_once'
      if (localStorage.getItem(DONE_KEY) === '1') return
      const seedVins = [
        'WP0AB2A88BU780484',
        'WP0AB29829U780608',
        'WP0AB2A83EK192718',
        'WP0CB2A87DS130360',
        'WP0CB2A8XES141001',
        'WP0CB2A84ES140670',
        'WP0AB2A89FK182065'
      ]
      setFavorites(prev => {
        const next = new Set(prev)
        seedVins.forEach(v => { const k = `VIN:${String(v || '').trim().toUpperCase()}`; if (k) next.add(k) })
        return next
      })
      localStorage.setItem(DONE_KEY, '1')
    } catch {/* ignore */}
  }, [])
  // New filters
  const [body, setBody] = useState<'all'|'Boxster'|'Cayman'>('all')
  const [maxPrice, setMaxPrice] = useState<number | null>(50000)
  const [sortState, setSortState] = useState<{ key?: string; order?: 'ascend' | 'descend' }>({})
  const [favOnly, setFavOnly] = useState<boolean>(false)

  // Facets reflect VIN-enriched data and current filters (top + column)
  const optionFacets = useMemo(() => {
    const base = applyTopLevelFilters(data, generation, body, maxPrice, vinMap)
    const scoped = applyColumnFiltersToRows(base, tableFilters, vinMap)
    return optionFacetCountsEnriched(scoped, vinMap)
  }, [data, generation, body, maxPrice, vinMap, tableFilters])
  const exteriorFacets = useMemo(() => {
    const base = applyTopLevelFilters(data, generation, body, maxPrice, vinMap)
    const scoped = applyColumnFiltersToRows(base, tableFilters, vinMap)
    return paintFacetCountsEnriched('exterior', scoped, vinMap)
  }, [data, generation, body, maxPrice, vinMap, tableFilters])
  const interiorFacets = useMemo(() => {
    const base = applyTopLevelFilters(data, generation, body, maxPrice, vinMap)
    const scoped = applyColumnFiltersToRows(base, tableFilters, vinMap)
    return paintFacetCountsEnriched('interior', scoped, vinMap)
  }, [data, generation, body, maxPrice, vinMap, tableFilters])

  useEffect(() => {
    let mounted = true
    async function load() {
      try {
        setLoading(true)
        const res = await axios.get<RankingResponse>('/api/ranking/latest')
        if (!mounted) return
        const rows = res.data.data
        setData(rows)
        setFilename(res.data.filename)
        // Compute new counts for summary
        try {
          const now = Date.now()
          const twoDaysMs = 2 * 24 * 60 * 60 * 1000
          const isNew = (v: any) => String(v).toLowerCase() === 'true' || String(v) === '1'
          const firstSeenIsRecent = (ts: any) => {
            try { return (now - new Date(String(ts)).getTime()) <= twoDaysMs } catch { return false }
          }
          setNewCount(rows.filter((r: any) => isNew(r.is_new)).length)
          setRecentCount(rows.filter((r: any) => firstSeenIsRecent(r.first_seen_at)).length)
        } catch {}
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

  // Listen for cross-tab save notifications to refresh vinMap and update UI
  useEffect(() => {
    let bc: BroadcastChannel | null = null
    try {
      bc = new BroadcastChannel('x987-vin')
      bc.onmessage = (ev: MessageEvent) => {
        try {
          const msg = ev.data || {}
          if (msg && msg.type === 'vinSaved') {
            const rec = msg.record
            const v: string = String(msg.vin || rec?.vin || '').trim().toUpperCase()
            if (v) setVinMap((prev) => ({ ...prev, [v]: rec }))
          }
        } catch {}
      }
    } catch {}
    const onStorage = (e: StorageEvent) => {
      try {
        if (e.key === 'x987_vin_saved' && e.newValue) {
          const payload = JSON.parse(e.newValue)
          const v: string = String(payload?.vin || '').trim().toUpperCase()
          if (v) {
            fetch(`/api/vin/${encodeURIComponent(v)}`)
              .then(res => res.json().catch(() => ({})))
              .then(json => {
                if (json && json.ok && json.record) {
                  setVinMap((prev) => ({ ...prev, [v]: json.record }))
                }
              }).catch(() => {})
          }
        }
      } catch {}
    }
    window.addEventListener('storage', onStorage)
    return () => {
      try { bc && bc.close() } catch {}
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  // Load all VIN enriched records for client-side join
  useEffect(() => {
    let mounted = true
    async function loadVin() {
      try {
        const res = await fetch('/api/vin')
        const json = await res.json().catch(() => ({}))
        if (!mounted) return
        if (json && json.ok && json.entries) setVinMap(json.entries)
      } catch { /* ignore */ }
    }
    loadVin()
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
      title: '',
      key: 'fav',
      width: 48,
      align: 'center',
      render: (_: any, r: any) => {
        try {
          const vin = String(r?.vin || r?.VIN || '').trim().toUpperCase()
          const enriched = vin ? vinMap[vin] : null
          const k = (() => {
            const v = String(enriched?.parsed?.vin || vin || '').trim().toUpperCase()
            if (v) return `VIN:${v}`
            const cu = String(r?.canonical_url || '').trim()
            if (cu) return `URL:${cu}`
            const lu = String(r?.listing_url || '').trim()
            if (lu) return `URL:${lu}`
            const su = String(r?.source_url || '').trim()
            if (su) return `SRC:${su}`
            const y = toInt(r?.year) || 0
            const mt = normalizeModelTrim(`${String(r?.model||'')} ${String(r?.trim||'')}`.trim())
            const p = toInt(r?.asking_price_usd) || 0
            const m = toInt(r?.mileage) || 0
            return `ROW:${y}-${mt}-${p}-${m}`
          })()
          const isFav = favorites.has(k)
          const onToggle = (e: MouseEvent) => {
            try { e.stopPropagation() } catch {}
            setFavorites(prev => {
              const next = new Set(prev)
              if (next.has(k)) next.delete(k); else next.add(k)
              return next
            })
          }
          return (
            <Button type="text" size="small" aria-label={isFav ? 'Unfavorite' : 'Favorite'} onClick={onToggle}
              icon={isFav ? <StarFilled style={{ color: '#f1c40f' }} /> : <StarOutlined style={{ color: '#999' }} />}
            />
          )
        } catch { return null }
      }
    },
    {
      title: 'Year',
      key: 'year',
      width: 64,
      sortOrder: (sortState as any)?.key === 'year' ? (sortState as any)?.order : undefined,
      sorter: (a,b) => {
        const va = String((a as any).vin || (a as any).VIN || '').trim().toUpperCase()
        const vb = String((b as any).vin || (b as any).VIN || '').trim().toUpperCase()
        const ea = va && vinMap[va] ? toInt(vinMap[va]?.parsed?.year) : toInt((a as any).year)
        const eb = vb && vinMap[vb] ? toInt(vinMap[vb]?.parsed?.year) : toInt((b as any).year)
        return (ea || 0) - (eb || 0)
      },
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
        const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const v = enriched?.parsed?.year != null ? toInt(enriched.parsed.year) : toInt((rec as any).year)
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const y = enriched?.parsed?.year != null ? toInt(enriched.parsed.year) : toInt((r as any).year)
        const dimYear = isEarlyYearDim(r)
        return <Chip text={y ?? ''} dim={dimYear} />
      }
    },
    {
      title: 'Model',
      key: 'modeltrim',
      sortOrder: (sortState as any)?.key === 'modeltrim' ? (sortState as any)?.order : undefined,
      sorter: (a,b) => {
        const va = String((a as any).vin || (a as any).VIN || '').trim().toUpperCase()
        const vb = String((b as any).vin || (b as any).VIN || '').trim().toUpperCase()
        const la = computeModelTrimLabel(a as any, va && vinMap[va] ? vinMap[va] : null)
        const lb = computeModelTrimLabel(b as any, vb && vinMap[vb] ? vinMap[vb] : null)
        return la.localeCompare(lb)
      },
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
        <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
          <Input
            ref={ymtInputRef}
            placeholder="Search model"
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
        const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const mt = computeModelTrimLabel(rec as any, enriched)
        const s = (mt || '').toLowerCase()
        return s.includes(String(value).toLowerCase())
      },
      onFilterDropdownOpenChange: (open) => { if (open) setTimeout(() => ymtInputRef.current?.select(), 100) },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const mt = computeModelTrimLabel(r as any, enriched)
        const usingVA = Boolean(String(enriched?.parsed?.model || '').trim())
        const showSource = (() => {
          try {
            const sp = new URLSearchParams(location.search)
            if (sp.get('debug_src') === '1') return true
            return localStorage.getItem('x987_debug_src') === '1'
          } catch { return false }
        })()
        return (
          <span className="text-xs md:text-sm">
            {mt}
            {showSource ? (
              <span style={{ marginLeft: 6, opacity: 0.6 }}>({usingVA ? 'VA' : 'PIPE'})</span>
            ) : null}
          </span>
        )
      }
    },
    {
      title: 'Price',
      key: 'price',
      align: 'right',
      sortOrder: (sortState as any)?.key === 'price' ? (sortState as any)?.order : undefined,
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
      sortOrder: (sortState as any)?.key === 'miles' ? (sortState as any)?.order : undefined,
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
      sortOrder: (sortState as any)?.key === 'msrp' ? (sortState as any)?.order : undefined,
      sorter: (a,b) => {
        const va = String((a as any).vin || (a as any).VIN || '').trim().toUpperCase()
        const vb = String((b as any).vin || (b as any).VIN || '').trim().toUpperCase()
        const ea = va && vinMap[va] ? toInt(vinMap[va]?.parsed?.totalMsrp) : toInt((a as any).total_options_msrp)
        const eb = vb && vinMap[vb] ? toInt(vinMap[vb]?.parsed?.totalMsrp) : toInt((b as any).total_options_msrp)
        return (ea || 0) - (eb || 0)
      },
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
        const v = (() => {
          try {
            const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
            const enriched = vin ? vinMap[vin] : null
            return enriched?.parsed?.totalMsrp != null ? toInt(enriched.parsed.totalMsrp) : toInt((rec as any).total_options_msrp)
          } catch { return toInt((rec as any).total_options_msrp) }
        })()
        if (v == null) return false
        if (range.min != null && v < range.min) return false
        if (range.max != null && v > range.max) return false
        return true
      },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const msrp = enriched?.parsed?.totalMsrp != null ? toInt(enriched.parsed.totalMsrp) : toInt(r.total_options_msrp)
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
        const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const tags = enriched ? new Set<string>(Array.isArray(enriched?.derived?.normalizedOptions) ? enriched.derived.normalizedOptions : []) : tagsForRecord(rec)
        if (mode === 'and') return chosen.every(t => tags.has(t))
        return chosen.some(t => tags.has(t))
      },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        if (enriched) {
          const node = renderEnrichedOptions(enriched)
          return enriched?.link ? (
            <a href={enriched.link} target="_blank" rel="noreferrer">{node || '(no options)'}</a>
          ) : (node || '(no options)')
        }
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
        const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const name = String(enriched?.parsed?.exterior || extractPaintFromRecord('exterior', rec).name || '')
        const key = name.trim().toLowerCase()
        return chosen.includes(key)
      },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const exName = String(enriched?.parsed?.exterior || '') || (extractPaintFromRecord('exterior', r).name as any) || ''
        return (
          <PaintChipExterior
            name={exName}
            hex={undefined}
            label={exName || '—'}
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
        const vin = String((rec as any).vin || (rec as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const name = String(enriched?.parsed?.interior || extractPaintFromRecord('interior', rec).name || '')
        const key = name.trim().toLowerCase()
        return chosen.includes(key)
      },
      render: (_, r) => {
        const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const rawIn = String(enriched?.parsed?.interior || '') || (extractPaintFromRecord('interior', r).name as any) || ''
        const two = parseInteriorTwoTone(rawIn)
        const displayLabel = titleCase(two.label || rawIn)
        const chipName = (two.secondary || two.primary || '').toString()
        return (
          <PaintChipInterior
            name={chipName}
            hex={undefined}
            label={displayLabel || '—'}
            size="md"
            className="w-full min-w-0 overflow-hidden whitespace-nowrap text-ellipsis"
          />
        )
      }
    },
    {
      title: 'VIN',
      key: 'vin',
      width: 160,
      align: 'left',
      render: (_: any, r: any) => {
        const vin = String(r?.vin || r?.VIN || '').trim()
        if (!vin) return ''
        const vinUp = vin.toUpperCase()
        const url = `https://vinanalytics.com/car/${encodeURIComponent(vinUp)}/`
        const onClick = (e: any) => { try { e.stopPropagation() } catch {} }
        return <a href={url} onClick={onClick} target="_blank" rel="noreferrer" className="font-mono text-xs">{vinUp}</a>
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
  ], [optionFacets, vinMap, sortState, favorites])

  const filtered = useMemo(() => {
    // Apply generation filter first
    let rows = applyGenerationFilter(data, generation)
    // Apply body filter (Cab/Coupe): All / Boxster / Cayman
    if (body !== 'all') {
      const target = body.toLowerCase()
      rows = rows.filter((r: any) => {
        try {
          const vin = String(r?.vin || r?.VIN || '').trim().toUpperCase()
          const enriched = vin ? vinMap[vin] : null
          const mt = computeModelTrimLabel(r, enriched)
          return (mt || '').toLowerCase().startsWith(target)
        } catch { return false }
      })
    }
    // Apply max price filter (asking_price_usd)
    if (maxPrice != null) {
      rows = rows.filter((r: any) => {
        const p = toInt((r as any).asking_price_usd)
        return p != null && p <= maxPrice
      })
    }
    // Apply favorites filter
    if (favOnly) {
      rows = rows.filter((r: any) => {
        try {
          const vin = String(r?.vin || r?.VIN || '').trim().toUpperCase()
          const enriched = vin ? vinMap[vin] : null
          const k = (() => {
            const v = String(enriched?.parsed?.vin || vin || '').trim().toUpperCase()
            if (v) return `VIN:${v}`
            const cu = String(r?.canonical_url || '').trim()
            if (cu) return `URL:${cu}`
            const lu = String(r?.listing_url || '').trim()
            if (lu) return `URL:${lu}`
            const su = String(r?.source_url || '').trim()
            if (su) return `SRC:${su}`
            const y = toInt(r?.year) || 0
            const mt = normalizeModelTrim(`${String(r?.model||'')} ${String(r?.trim||'')}`.trim())
            const p = toInt(r?.asking_price_usd) || 0
            const m = toInt(r?.mileage) || 0
            return `ROW:${y}-${mt}-${p}-${m}`
          })()
          return favorites.has(k)
        } catch { return false }
      })
    }
    return rows
  }, [data, generation, body, maxPrice, vinMap, favOnly, favorites])
  
  const sorted = useMemo(() => {
    const rows = [...filtered]
    const key = (sortState as any)?.key
    const order = (sortState as any)?.order
    if (!key || !order) return rows
    const dir = order === 'ascend' ? 1 : -1
    const num = (v: any) => {
      try { return typeof v === 'number' ? v : toInt(v) || 0 } catch { return 0 }
    }
    if (key === 'year') {
      rows.sort((a: any, b: any) => {
        const va = String(a?.vin || a?.VIN || '').trim().toUpperCase()
        const vb = String(b?.vin || b?.VIN || '').trim().toUpperCase()
        const ya = va && vinMap[va] ? toInt(vinMap[va]?.parsed?.year) : toInt(a?.year)
        const yb = vb && vinMap[vb] ? toInt(vinMap[vb]?.parsed?.year) : toInt(b?.year)
        return ((ya || 0) - (yb || 0)) * dir
      })
      return rows
    }
    if (key === 'modeltrim') {
      rows.sort((a: any, b: any) => {
        const va = String(a?.vin || a?.VIN || '').trim().toUpperCase()
        const vb = String(b?.vin || b?.VIN || '').trim().toUpperCase()
        const la = computeModelTrimLabel(a, va && vinMap[va] ? vinMap[va] : null)
        const lb = computeModelTrimLabel(b, vb && vinMap[vb] ? vinMap[vb] : null)
        return la.localeCompare(lb) * dir
      })
      return rows
    }
    if (key === 'price') {
      rows.sort((a: any, b: any) => (num(a?.asking_price_usd) - num(b?.asking_price_usd)) * dir)
      return rows
    }
    if (key === 'miles') {
      rows.sort((a: any, b: any) => (num(a?.mileage) - num(b?.mileage)) * dir)
      return rows
    }
    if (key === 'msrp') {
      rows.sort((a: any, b: any) => {
        const va = String(a?.vin || a?.VIN || '').trim().toUpperCase()
        const vb = String(b?.vin || b?.VIN || '').trim().toUpperCase()
        const ea = va && vinMap[va] ? toInt(vinMap[va]?.parsed?.totalMsrp) : toInt(a?.total_options_msrp)
        const eb = vb && vinMap[vb] ? toInt(vinMap[vb]?.parsed?.totalMsrp) : toInt(b?.total_options_msrp)
        return ((ea || 0) - (eb || 0)) * dir
      })
      return rows
    }
    return rows
  }, [filtered, sortState, vinMap])
  const genOptions = useMemo(() => generationOptionsAll(data), [data])
  const summary = useMemo(() => {
    const displayed = filtered.filter(r => toInt(r.year) != null)
    const unknown = data.filter(r => toInt(r.year) == null)
    return { displayedCount: displayed.length, unknown }
  }, [data, filtered])

  // Fallback: if selected generation has no matches, revert to 'all'
  useEffect(() => {
    try {
      const displayedCount = filtered.filter(r => toInt(r.year) != null).length
      if (generation !== 'all' && displayedCount === 0) {
        setGeneration('all')
      }
    } catch { /* ignore */ }
  }, [generation, filtered])

  const [page, setPage] = useState<{ current: number; pageSize: number }>({ current: 1, pageSize: 250 })

  const handleExportFilteredJson = useCallback(() => {
    try {
      const rowsBase = filtered.filter(r => toInt(r.year) != null)
      const afterTable = applyTableFilters(rowsBase as any[], columns as any[], tableFilters)
      const out = afterTable.map((r: any) => {
        try {
          const vin = String((r?.vin || r?.VIN || '')).trim().toUpperCase()
          const enr = vin ? vinMap[vin] : null
          return { ...r, _enriched: enr || undefined }
        } catch { return r }
      })
      const payload = JSON.stringify(out, null, 2)
      const blob = new Blob([payload], { type: 'application/json;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const base = filename ? String(filename) : 'ranking'
      const ts = new Date().toISOString().replace(/[:]/g, '-')
      a.download = `${base.replace(/\.[a-z0-9]+$/i, '')}-filtered-${ts}.json`
      a.href = url
      document.body.appendChild(a)
      a.click()
      setTimeout(() => {
        try { document.body.removeChild(a) } catch {}
        try { URL.revokeObjectURL(url) } catch {}
      }, 0)
    } catch (e) {
      try { console.error('Export failed', e) } catch {}
    }
  }, [filtered, columns, tableFilters, vinMap, filename])

  // Debug logging: enable via ?debug_rows=1 or localStorage.x987_debug_rows='1'
  useEffect(() => {
    const isDebug = (() => {
      try {
        const sp = new URLSearchParams(location.search)
        if (sp.get('debug_rows') === '1') return true
        return localStorage.getItem('x987_debug_rows') === '1'
      } catch { return false }
    })()
    if (!isDebug) return
    try {
      const rows: any[] = (filtered && filtered.length ? filtered : data) as any[]
      console.groupCollapsed(`[x987-debug] Rows ${rows.length}`)
      rows.forEach((r: any) => {
        const vin = String(r?.vin || r?.VIN || '').trim().toUpperCase()
        const enriched = vin ? vinMap[vin] : null
        const pipModel = String(r?.model || '')
        const pipTrim = String(r?.trim || '')
        const vaModel = String(enriched?.parsed?.model || '')
        const vaTrim = String(enriched?.parsed?.trim || '')
        const modelTag = String(enriched?.parsed?.modelTag || '')
        const baseName = String(enriched?.parsed?.baseName || '')
        const chosen = computeModelTrimLabel(r, enriched)
        const source = vaModel ? 'vinanalytics' : 'pipeline'
        console.log('[row]', vin || '(no VIN)', {
          pipeline: { model: pipModel, trim: pipTrim },
          vinanalytics: { model: vaModel, trim: vaTrim, modelTag, baseName },
          chosen: { label: chosen, source }
        })
      })
      console.groupEnd()
    } catch { /* ignore */ }
  }, [data, filtered, vinMap])

  const items = [
    {
      key: 'results',
      label: 'Results',
      children: (
        <div className="p-3">
          <Space direction="vertical" size="middle" className="w-full">
            {/* moved summary header to Controls tab */}

            {/* Top-of-table controls */}
            <div className="flex flex-wrap gap-3 items-end">
              <FilterSelect
                label="Generation"
                value={generation}
                onChange={(v) => setGeneration(String(v) as GenerationValue)}
                className="w-full sm:w-[420px] md:w-[560px]"
                options={genOptions}
              />
              <FilterSelect
                label="Cab/Coupe"
                value={body}
                onChange={(v) => setBody(String(v) as any)}
                className="w-full sm:w-[220px]"
                options={[
                  { label: 'All', value: 'all' },
                  { label: 'Boxster', value: 'Boxster' },
                  { label: 'Cayman', value: 'Cayman' }
                ]}
              />
              <FilterSelect
                label="Max Price"
                value={maxPrice == null ? 'none' : maxPrice}
                onChange={(v) => {
                  if (String(v) === 'none') setMaxPrice(null)
                  else setMaxPrice(Number(v) || null)
                }}
                className="w-full sm:w-[220px]"
                options={[
                  { label: 'None', value: 'none' },
                  ...Array.from({ length: 10 }, (_, i) => (i + 1) * 10000).map(v => ({ label: `$${(v/1000)}k`, value: v }))
                ]}
              />
              <Button
                onClick={() => setSortState({ key: 'msrp', order: 'descend' })}
                icon={<SortDescendingOutlined />}
              >
                MSRP
              </Button>
              <Button type={favOnly ? 'primary' : 'default'} onClick={() => setFavOnly(v => !v)} icon={favOnly ? <StarFilled /> : <StarOutlined />}>
                Favorites Only
              </Button>
            </div>

            {/* Generation summary moved to Controls tab */}

            {loading ? <Spin/> : error ? <Text type="danger">{error}</Text> : (
              <Table
                size="small"
                rowKey={(r) => (
                  (r as any).vin || (r as any).VIN ||
                  r.listing_url ||
                  r.source_url ||
                  `${toInt(r.year) || 0}-${normalizeModelTrim(((r.model || '') + ' ' + (r.trim || '')).trim()) || ''}-${toInt(r.asking_price_usd) || 0}-${toInt(r.mileage) || 0}`
                )}
                columns={columns}
                dataSource={sorted.filter(r => toInt(r.year) != null)}
                rowClassName={(r) => {
                  try {
                    const vin = String((r as any).vin || (r as any).VIN || '').trim().toUpperCase()
                    const enriched = vin && vinMap[vin] ? true : false
                    // Build the same favorites key heuristic used by the star column
                    const enrichedRec = vin ? vinMap[vin] : null
                    const k = (() => {
                      const v = String(enrichedRec?.parsed?.vin || vin || '').trim().toUpperCase()
                      if (v) return `VIN:${v}`
                      const cu = String((r as any).canonical_url || '').trim()
                      if (cu) return `URL:${cu}`
                      const lu = String((r as any).listing_url || '').trim()
                      if (lu) return `URL:${lu}`
                      const su = String((r as any).source_url || '').trim()
                      if (su) return `SRC:${su}`
                      const y = toInt((r as any).year) || 0
                      const mt = normalizeModelTrim(`${String((r as any).model||'')} ${String((r as any).trim||'')}`.trim())
                      const p = toInt((r as any).asking_price_usd) || 0
                      const m = toInt((r as any).mileage) || 0
                      return `ROW:${y}-${mt}-${p}-${m}`
                    })()
                    const fav = favorites.has(k)
                    if (enriched && fav) return 'row-enriched row-favorite'
                    if (enriched) return 'row-enriched'
                    if (fav) return 'row-favorite'
                    return ''
                  } catch { return '' }
                }}
                pagination={{ current: page.current, pageSize: page.pageSize }}
                onChange={(pag, _filters, sorter: any) => {
                  setPage({ current: pag?.current ?? 1, pageSize: pag?.pageSize ?? page.pageSize })
                  try { setTableFilters(_filters as any) } catch {}
                  try {
                    const k = Array.isArray(sorter) ? sorter[0]?.columnKey : sorter?.columnKey
                    const order = Array.isArray(sorter) ? sorter[0]?.order : sorter?.order
                    setSortState({ key: k as any, order: order as any })
                  } catch {}
                }}
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
            <SummaryHeader
              displayedCount={summary.displayedCount}
              newCount={newCount}
              recentCount={recentCount}
              filename={filename}
              unknownLinks={summary.unknown.map(r => (r.listing_url || r.source_url || "")).filter(Boolean)}
            />
            {generation !== 'all' && (
              <div className="mt-2 text-xs md:text-sm">
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
        <HeaderBar
          title="x987"
          subtitle="Web"
          onExport={handleExportFilteredJson}
          onBookmarklet={() => setBmOpen(true)}
        />
        <Content style={{ background: roles.bg.surface as string }}>
          <Tabs
            items={items}
            type="line"
            size="large"
            tabBarGutter={16}
            tabBarStyle={{ margin: '8px 12px 0' }}
          />
        </Content>
      </Layout>
      <BookmarkletModal open={bmOpen} onClose={() => setBmOpen(false)} />
    </ConfigProvider>
  )
}

// Build a filtered snapshot matching current Table filters
function applyTableFilters(
  rows: any[],
  columns: any[],
  filters: Record<string, any[] | null>
): any[] {
  try {
    if (!rows || !rows.length) return rows
    const active = (columns || []).filter((c: any) => (
      c && c.key && typeof c.onFilter === 'function' && filters && Array.isArray(filters[c.key]) && (filters[c.key] as any[]).length > 0
    ))
    if (!active.length) return rows
    return rows.filter((rec: any) => {
      for (const col of active) {
        const vals = (filters[col.key] || []) as any[]
        // AntD semantics: OR within a column's selected values
        const ok = vals.some((v) => {
          try { return col.onFilter(v, rec) } catch { return false }
        })
        if (!ok) return false
      }
      return true
    })
  } catch { return rows }
}

// Apply top-of-table filters (generation, body, price) to a dataset
function applyTopLevelFilters(
  data: any[],
  generation: any,
  body: 'all'|'Boxster'|'Cayman',
  maxPrice: number | null,
  vinMap: Record<string, any>
): any[] {
  try {
    let rows = applyGenerationFilter(data, generation)
    if (body !== 'all') {
      const target = String(body || '').toLowerCase()
      rows = rows.filter((r: any) => {
        try {
          const vin = String(r?.vin || r?.VIN || '').trim().toUpperCase()
          const enriched = vin ? vinMap[vin] : null
          const mt = computeModelTrimLabel(r, enriched)
          return (mt || '').toLowerCase().startsWith(target)
        } catch { return false }
      })
    }
    if (maxPrice != null) {
      rows = rows.filter((r: any) => {
        const p = toInt((r as any).asking_price_usd)
        return p != null && p <= maxPrice
      })
    }
    return rows
  } catch { return data || [] }
}

// Apply active column filters without needing AntD column definitions
function applyColumnFiltersToRows(
  rows: any[],
  filters: Record<string, any[] | null>,
  vinMap: Record<string, any>
): any[] {
  try {
    if (!filters) return rows
    return (rows || []).filter((rec: any) => {
      const vin = String((rec?.vin || rec?.VIN || '')).trim().toUpperCase()
      const enriched = vin ? vinMap[vin] : null

      // Helper: parse first JSON payload for a key
      const parsePayload = (key: string): any => {
        try {
          const arr = (filters as any)[key]
          if (!Array.isArray(arr) || arr.length === 0) return undefined
          const v = arr[0]
          return typeof v === 'string' ? JSON.parse(v) : v
        } catch { return undefined }
      }

      // Year range
      if (Array.isArray(filters.year) && filters.year.length) {
        const payload = parsePayload('year') || {}
        const v = (() => {
          try { return enriched?.parsed?.year != null ? toInt(enriched.parsed.year) : toInt(rec.year) } catch { return toInt(rec.year) }
        })()
        if (v == null) return false
        if (payload.min != null && v < payload.min) return false
        if (payload.max != null && v > payload.max) return false
      }

      // Model/Trim search
      if (Array.isArray(filters.modeltrim) && filters.modeltrim.length) {
        const needle = String(filters.modeltrim[0] || '').toLowerCase()
        const mt = computeModelTrimLabel(rec, enriched).toLowerCase()
        if (!mt.includes(needle)) return false
      }

      // Price range
      if (Array.isArray(filters.price) && filters.price.length) {
        const payload = parsePayload('price') || {}
        const v = toInt(rec.asking_price_usd)
        if (v == null) return false
        if (payload.min != null && v < payload.min) return false
        if (payload.max != null && v > payload.max) return false
      }

      // Miles range
      if (Array.isArray(filters.miles) && filters.miles.length) {
        const payload = parsePayload('miles') || {}
        const v = toInt(rec.mileage)
        if (v == null) return false
        if (payload.min != null && v < payload.min) return false
        if (payload.max != null && v > payload.max) return false
      }

      // MSRP (Opt $) range
      if (Array.isArray(filters.msrp) && filters.msrp.length) {
        const payload = parsePayload('msrp') || {}
        const v = (() => {
          try { return enriched?.parsed?.totalMsrp != null ? toInt(enriched.parsed.totalMsrp) : toInt(rec.total_options_msrp) } catch { return toInt(rec.total_options_msrp) }
        })()
        if (v == null) return false
        if (payload.min != null && v < payload.min) return false
        if (payload.max != null && v > payload.max) return false
      }

      // Options tags (VIN-enriched preferred; no fallback if enriched exists)
      if (Array.isArray(filters.opts) && filters.opts.length) {
        const payload = parsePayload('opts') || {}
        const chosen: string[] = Array.isArray(payload.tags) ? payload.tags : []
        const mode: 'and' | 'or' = (payload.mode === 'or') ? 'or' : 'and'
        if (chosen.length) {
          const tags = enriched
            ? new Set<string>(Array.isArray(enriched?.derived?.normalizedOptions) ? enriched.derived.normalizedOptions : [])
            : tagsForRecord(rec)
          const ok = mode === 'and' ? chosen.every(t => tags.has(t)) : chosen.some(t => tags.has(t))
          if (!ok) return false
        }
      }

      // Exterior colors
      if (Array.isArray(filters.exterior) && filters.exterior.length) {
        const payload = parsePayload('exterior') || {}
        const chosen: string[] = Array.isArray(payload.tags) ? payload.tags : []
        if (chosen.length) {
          const name = String(enriched?.parsed?.exterior || extractPaintFromRecord('exterior', rec).name || '')
          const key = name.trim().toLowerCase()
          if (!chosen.includes(key)) return false
        }
      }

      // Interior colors
      if (Array.isArray(filters.interior) && filters.interior.length) {
        const payload = parsePayload('interior') || {}
        const chosen: string[] = Array.isArray(payload.tags) ? payload.tags : []
        if (chosen.length) {
          const name = String(enriched?.parsed?.interior || extractPaintFromRecord('interior', rec).name || '')
          const key = name.trim().toLowerCase()
          if (!chosen.includes(key)) return false
        }
      }

      return true
    })
  } catch { return rows }
}

// Counts option tags using VIN-enriched normalizedOptions when available; else falls back
function optionFacetCountsEnriched(
  data: any[],
  vinMap: Record<string, any>
): { tag: string; count: number }[] {
  const counts = new Map<string, number>()
  try {
    for (const rec of (data || [])) {
      const vin = String((rec?.vin || rec?.VIN || '')).trim().toUpperCase()
      const enriched = vin ? vinMap[vin] : null
      const tags: Set<string> = (() => {
        if (enriched) {
          const arr: any[] = Array.isArray(enriched?.derived?.normalizedOptions) ? enriched.derived.normalizedOptions : []
          return new Set<string>(arr.filter((v) => typeof v === 'string' && v.trim()))
        }
        return tagsForRecord(rec as any)
      })()
      for (const t of tags) counts.set(t, (counts.get(t) || 0) + 1)
    }
  } catch { /* ignore */ }
  return Array.from(counts.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => (b.count - a.count) || a.tag.localeCompare(b.tag))
}

function paintFacetCountsEnriched(kind: 'exterior'|'interior', data: any[], vinMap: Record<string, any>) {
  const counts = new Map<string, number>()
  for (const r of data || []) {
    try {
      const vin = String((r?.vin || r?.VIN || '')).trim().toUpperCase()
      const enriched = vin ? vinMap[vin] : null
      const name = String(
        (kind === 'exterior' ? enriched?.parsed?.exterior : enriched?.parsed?.interior) ||
        extractPaintFromRecord(kind, r).name || ''
      )
      const key = name.trim().toLowerCase()
      if (!key) continue
      counts.set(key, (counts.get(key) || 0) + 1)
    } catch { /* ignore row */ }
  }
  return Array.from(counts.entries())
    .map(([key, count]) => ({ key, label: titleCase(key), count }))
    .sort((a, b) => (b.count - a.count) || a.label.localeCompare(b.label))
}

function titleCase(s: string) {
  return (s || '').split(/\s+/).map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ')
}

function computeModelTrimLabel(rec: any, enriched: any | null): string {
  try {
    // Simplified: only use enriched v-model (parsed.model/trim). Otherwise, fall back to scraped.
    const model = String(enriched?.parsed?.model || '').trim()
    const trim = String(enriched?.parsed?.trim || '').trim()
    if (model) return normalizeModelTrim(`${model} ${trim}`.trim())
    return normalizeModelTrim(`${String(rec?.model || '')} ${String(rec?.trim || '')}`.trim())
  } catch { return normalizeModelTrim(String(rec?.model || '')) }
}

function isGenericTrim(v: any): boolean {
  const s = String(v || '').trim().toLowerCase()
  if (!s) return true
  return s === 'base' || s === 'standard' || s === 'std'
}

// (unused legacy helpers removed)

function renderEnrichedOptions(enriched: any): React.ReactNode {
  try {
    const derived: string[] = Array.isArray(enriched?.derived?.normalizedOptions) ? enriched.derived.normalizedOptions : []
    const opts: any[] = Array.isArray(enriched?.parsed?.options) ? enriched.parsed.options : []
    const names = opts.map(o => String(o?.name || o?.code || '')).filter(Boolean)
    // Preferred order and key chip set
    const priority = ['Chrono', 'LSD', 'PASM', 'PTV', 'PSE']
    const normalized = [...new Set(derived.length ? derived : names)].map(s => {
      const sl = s.toLowerCase()
      if (sl.includes('exhaust')) return 'PSE'
      return s
    })
    const hasPTV = normalized.some(s => s.toLowerCase().includes('ptv'))
    const showPriority = hasPTV ? priority.filter(k => k.toLowerCase() !== 'lsd') : priority
    const chips = showPriority
      .filter(k => normalized.some(s => s.toLowerCase().includes(k.toLowerCase())))
      .map(k => {
        // Make 'Chrono' a bit brighter than other option chips
        const isChrono = k.toLowerCase() === 'chrono'
        const bg = isChrono ? (palette.gray[500] as string) : (roles.bg.emphasis as string)
        return <Chip key={k} text={k} bg={bg} color={roles.text.primary as string} />
      })
    // Packages (exclude Chrono packages)
    const packages = opts
      .filter(o => (/package/i.test(String(o?.name || '')) || /^[P][A-Z0-9]{1,3}$/i.test(String(o?.code || ''))))
      .filter(o => !/chrono/i.test(String(o?.name || '')) && !/^64(0|0A|0LC|0SP)?$/i.test(String(o?.code || '')) && String(o?.code || '').toUpperCase() !== '639')
      .map(o => String(o?.name || o?.code || ''))
      .filter(Boolean)
    const extrasText = packages.length ? optionsCompact(packages) : ''
    return (
      <span className="inline-flex items-center gap-1 flex-wrap">
        {chips}
        {extrasText ? <span style={{ marginLeft: chips.length ? 6 : 0 }}>{extrasText}</span> : null}
      </span>
    )
  } catch { return '' }
}
