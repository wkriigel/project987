import fs from 'fs'
import path from 'path'
import { ensureVinEnrichedPath, findVinEnrichedJson } from './utils/fsPaths'

export interface VinOptionItem {
  code?: string
  name: string
  price?: number | null
}

export interface VinParsed {
  totalMsrp?: number | null
  options?: VinOptionItem[]
  year?: number | null
  model?: string
  trim?: string
  exterior?: string
  interior?: string
  baseName?: string
  modelTag?: string
  listingUrl?: string
  askingPriceUsd?: number | null
  mileage?: number | null
}

export interface VinDerived {
  normalizedOptions?: string[]
  normalizedMsrp?: number | null
  modelTrimNormalized?: string
}

export interface VinRecord {
  source: 'vinanalytics'
  vin: string
  updatedAt: string
  link: string
  raw: string
  parsed: VinParsed
  derived: VinDerived
}

interface VinStoreFileV1 {
  version: 1
  updatedAt: string
  entries: Record<string, VinRecord>
}

export function loadStore(): VinStoreFileV1 {
  const p = findVinEnrichedJson()
  if (!p || !fs.existsSync(p)) {
    return { version: 1, updatedAt: new Date().toISOString(), entries: {} }
  }
  try {
    const raw = fs.readFileSync(p, 'utf-8')
    const json = JSON.parse(raw)
    if (!json || typeof json !== 'object') throw new Error('invalid JSON')
    const v = Number(json.version) || 1
    if (v !== 1) throw new Error('unsupported version')
    return json as VinStoreFileV1
  } catch {
    return { version: 1, updatedAt: new Date().toISOString(), entries: {} }
  }
}

export function saveStore(store: VinStoreFileV1) {
  const p = ensureVinEnrichedPath()
  const dir = path.dirname(p)
  try { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }) } catch {}
  fs.writeFileSync(p, JSON.stringify(store, null, 2), 'utf-8')
}

export function upsertVinRecord(vin: string, raw: string, parsed: VinParsed): VinRecord {
  const store = loadStore()
  const key = (vin || '').trim().toUpperCase()
  const totalMsrp = typeof parsed.totalMsrp === 'number' ? parsed.totalMsrp : null
  const options = Array.isArray(parsed.options) ? parsed.options : []
  const derived: VinDerived = {
    normalizedMsrp: totalMsrp,
    normalizedOptions: normalizeOptions(options),
    modelTrimNormalized: computeModelTrimNormalized(parsed)
  }
  // Prefer a user-provided listing URL if valid http(s); else fall back to VINAnalytics link
  const candidateLink = safeHttpUrl((parsed as any).listingUrl) || ''
  const rec: VinRecord = {
    source: 'vinanalytics',
    vin: key,
    updatedAt: new Date().toISOString(),
    link: candidateLink || `https://vinanalytics.com/car/${key}/`,
    raw,
    parsed: {
      totalMsrp,
      options,
      year: typeof parsed.year === 'number' ? parsed.year : (parsed.year != null ? Number(parsed.year) || null : undefined),
      model: parsed.model,
      trim: parsed.trim,
      exterior: parsed.exterior,
      interior: parsed.interior,
      baseName: parsed.baseName,
      modelTag: parsed.modelTag,
      listingUrl: candidateLink || undefined,
      askingPriceUsd: typeof parsed.askingPriceUsd === 'number' ? Math.trunc(parsed.askingPriceUsd) : (parsed.askingPriceUsd != null ? (toMoney(parsed.askingPriceUsd) || null) : undefined),
      mileage: typeof parsed.mileage === 'number' ? Math.trunc(parsed.mileage) : (parsed.mileage != null ? (toInt(parsed.mileage) || null) : undefined)
    },
    derived
  }
  store.entries[key] = rec
  store.updatedAt = new Date().toISOString()
  saveStore(store)
  return rec
}

export function getVinRecord(vin: string): VinRecord | undefined {
  const store = maybeRepairStore(loadStore())
  const key = (vin || '').trim().toUpperCase()
  return store.entries[key]
}

export function getAllVinRecords(): Record<string, VinRecord> {
  const store = maybeRepairStore(loadStore())
  return store.entries || {}
}

// Lightweight normalization for key option tags; reuse FE semantics
function normalizeOptions(items: VinOptionItem[]): string[] {
  const tags = new Set<string>()
  for (const it of items) {
    const code = (it.code || '').trim().toUpperCase()
    const name = (it.name || '').toString()
    const low = name.toLowerCase()
    // Priority tokens
    if (low.includes('sport chrono') || /\bchrono\b/.test(low) || code === '640' || code === '639' || code.startsWith('640')) tags.add('Chrono')
    if (low.includes('limited slip') || /\blsd\b/.test(low) || code === '220' || code === '220A') tags.add('LSD')
    if (low.includes('ptv') || code === 'PTV') tags.add('PTV')
    if (low.includes('pasm') || low.includes('active suspension') || code === '475') tags.add('PASM')
    if (low.includes('sport exhaust') || /\bpse\b/.test(low) || code === 'XLF') tags.add('PSE')
    // Keep a few common extras aligned with FE
    if (low.includes('bose')) tags.add('BOSE')
    if (low.includes('heated seat')) tags.add('Heated')
    if (low.includes('ventilated') || low.includes('cooled seat')) tags.add('Cooled')
    if (low.includes('park assist')) tags.add('Park')
  }
  // Ordering preference: Chrono, LSD, PASM, PSE, PTV, then alpha
  const priority = ['Chrono', 'LSD', 'PASM', 'PSE', 'PTV']
  const arr = Array.from(tags)
  arr.sort((a, b) => {
    const ai = priority.indexOf(a)
    const bi = priority.indexOf(b)
    if (ai >= 0 && bi >= 0) return ai - bi
    if (ai >= 0) return -1
    if (bi >= 0) return 1
    return a.localeCompare(b)
  })
  return arr
}

function computeModelTrimNormalized(parsed: VinParsed): string {
  try {
    const m = safeStr(parsed.model)
    let t = safeStr(parsed.trim)
    if (m) return `${m} ${t}`.trim()
    // Fallback: baseName if present
    const baseLabel = safeStr(parsed.baseName)
    if (baseLabel) {
      const mt = deriveModelTrimFromBase(baseLabel)
      if (mt.model) return `${mt.model} ${mt.trim}`.trim()
    }
    // Last resort: scan options for a model/trim cue
    if (Array.isArray(parsed.options)) {
      const mt2 = deriveModelTrimFromAnyOption(parsed.options)
      if (mt2.model) return `${mt2.model} ${mt2.trim}`.trim()
    }
    return `${m} ${t}`.trim()
  } catch { return `${safeStr(parsed.model)} ${safeStr(parsed.trim)}`.trim() }
}

// If older records were saved without model/trim/etc., re-parse their raw JSON/HTML
// and persist the enriched parsed fields so the FE can use them without re‑ingest.
function maybeRepairStore(store: VinStoreFileV1): VinStoreFileV1 {
  try {
    let changed = false
    const entries = store.entries || {}
    for (const key of Object.keys(entries)) {
      const rec = entries[key]
      if (!rec || !rec.raw) continue
      const p = rec.parsed || {}
      const missing = !(p as any).model && !(p as any).trim && !(p as any).baseName && !(p as any).modelTag && (p as any).options
      if (missing) {
        try {
          const reparsed = parseVinAnalyticsBlob(rec.raw, key)
          const totalMsrp = typeof reparsed.totalMsrp === 'number' ? reparsed.totalMsrp : null
          const options = Array.isArray(reparsed.options) ? reparsed.options : []
          const updatedParsed: VinParsed = {
            totalMsrp,
            options,
            year: typeof reparsed.year === 'number' ? reparsed.year : (reparsed.year != null ? Number(reparsed.year) || null : undefined),
            model: reparsed.model,
            trim: reparsed.trim,
            exterior: reparsed.exterior,
            interior: reparsed.interior,
            baseName: reparsed.baseName,
            modelTag: (reparsed as any).modelTag
          }
          rec.parsed = updatedParsed
          rec.derived = {
            normalizedMsrp: totalMsrp,
            normalizedOptions: normalizeOptions(options),
            modelTrimNormalized: computeModelTrimNormalized(updatedParsed)
          }
          rec.updatedAt = new Date().toISOString()
          changed = true
        } catch {}
      }
    }
    if (changed) saveStore(store)
  } catch {}
  return store
}

// Parser accepts: JSON from bookmarklet, HTML table paste, or TSV/CSV-like text
export function parseVinAnalyticsBlob(blob: string, vinHint?: string): VinParsed & { vin?: string } {
  const raw = (blob || '').trim()
  if (!raw) return { totalMsrp: null, options: [] }
  // Try JSON first
  try {
    const obj = JSON.parse(raw)
    if (obj && typeof obj === 'object') {
      const vin = String((obj as any).vin || vinHint || '').trim().toUpperCase() || undefined
      const total = toMoney((obj as any).totalMsrp)
      const options: VinOptionItem[] = Array.isArray((obj as any).options) ? (obj as any).options.map((o: any) => ({
        code: safeStr(o.code),
        name: safeStr(o.name),
        price: toMoney(o.price)
      })) : []
      const year = toInt((obj as any).year)
      let model = safeStr((obj as any).model)
      let trim = safeStr((obj as any).trim)
      const modelTag = safeStr((obj as any).modelTag)
      const exterior = safeStr((obj as any).exterior)
      const interior = safeStr((obj as any).interior)
      const baseName = safeStr((obj as any).baseName)
      const listingUrl = safeHttpUrl((obj as any).listingUrl) || undefined
      const askingPriceUsd = toMoney((obj as any).askingPriceUsd ?? (obj as any).asking_price_usd ?? (obj as any).priceUsd ?? (obj as any).price)
      const mileage = toInt((obj as any).mileage ?? (obj as any).miles)
      // Simplified: trust v-model (payload) for model/trim. Fallback to BASE if model is missing entirely.
      if (!model) {
        // Try deriving from modelTag (bookmarklet-provided raw label)
        if (modelTag) {
          const mt = deriveModelTrimFromBase(modelTag)
          if (mt.model) { model = mt.model; trim = mt.trim }
        }
      }
      if (!model) {
        const base = options.find(o => codeIsBase(o.code))
        const baseLabel = baseName || (base && base.name) || ''
        if (baseLabel) {
          const mt = deriveModelTrimFromBase(baseLabel)
          if (mt.model) { model = mt.model; trim = mt.trim }
        }
      }
      return { vin, totalMsrp: total, options, year, model, trim, exterior, interior, baseName, modelTag, listingUrl, askingPriceUsd, mileage }
    }
  } catch {}
  // HTML path: look for <table
  if (raw.toLowerCase().includes('<table')) {
    const text = raw
      .replace(/<\/(t[hd]|tr)>/gi, '\n')
      .replace(/<[^>]+>/g, '\t')
      .replace(/&nbsp;/g, ' ')
    return parseTableLike(text)
  }
  // Fallback: treat as TSV/CSV-ish
  return parseTableLike(raw)
}

function parseTableLike(text: string): VinParsed & { vin?: string } {
  const lines = text.split(/\r?\n/).map(s => s.replace(/\s+$/g, '')).filter(s => s.trim())
  if (lines.length === 0) return { totalMsrp: null, options: [] }
  // Try to detect VIN in header lines
  let vin: string | undefined = undefined
  for (const L of lines.slice(0, 5)) {
    const m = L.match(/\b([A-HJ-NPR-Z0-9]{17})\b/i)
    if (m) { vin = m[1].toUpperCase(); break }
  }
  // Identify header row
  const first = splitRow(lines[0])
  let head = first.map(s => s.toLowerCase())
  let start = 1
  // If header row doesn't look like header, search first 3 lines for known headers
  const headerHints = ['code', 'option', 'description', 'msrp', 'price']
  const headerScore = (cols: string[]) => cols.reduce((acc, c) => acc + (headerHints.some(h => c.includes(h)) ? 1 : 0), 0)
  if (headerScore(head) === 0) {
    for (let i = 0; i < Math.min(3, lines.length); i++) {
      const cols = splitRow(lines[i]).map(s => s.toLowerCase())
      if (headerScore(cols) > 0) { head = cols; start = i + 1; break }
    }
  }
  // Find column indices
  const idxCode = head.findIndex(c => /code|opt\s*code/i.test(c))
  const idxName = head.findIndex(c => /option|description|name/i.test(c))
  const idxMsrp = head.findIndex(c => /msrp|price|amount/i.test(c))
  const options: VinOptionItem[] = []
  let exterior: string | undefined
  let interior: string | undefined
  let model: string | undefined
  let trim: string | undefined
  let totalMsrp: number | null = null
  for (let i = start; i < lines.length; i++) {
    const cols = splitRow(lines[i])
    if (cols.length === 0) continue
    // Detect a total row
    const rowText = cols.join(' ').toLowerCase()
    if (/total/.test(rowText)) {
      for (const c of cols) {
        const n = toMoney(c)
        if (n != null) { totalMsrp = n; break }
      }
      continue
    }
    // Capture meta rows from HTML-like tables
    if (!exterior && /^(exterior)\b/i.test(cols[0] || '') && cols[1]) { exterior = safeStr(cols[1]); continue }
    if (!interior && /^(interior)\b/i.test(cols[0] || '') && cols[1]) { interior = safeStr(cols[1]); continue }
    if (/^base$/i.test(cols[0] || '') && cols[1]) {
      const mt = safeStr(cols[1])
      const toks = mt.split(/\s+/)
      if (toks.length >= 1) {
        const fam = toks[0]
        const rest = toks.slice(1).join(' ')
        if (/^911$/i.test(fam)) { model = '911'; trim = rest.trim() }
        else if (/^(Cayman|Boxster)$/i.test(fam)) { model = fam; trim = rest.trim() }
        else { model = mt; trim = '' }
      }
      continue
    }
    const code = idxCode >= 0 ? safeStr(cols[idxCode]) : undefined
    const name = idxName >= 0 ? safeStr(cols[idxName]) : safeStr(cols[0])
    const price = idxMsrp >= 0 ? toMoney(cols[idxMsrp]) : null
    if (name) options.push({ code, name, price })
  }
  return { vin, totalMsrp, options, exterior, interior, model, trim }
}

function splitRow(line: string): string[] {
  if (line.includes('\t')) return line.split('\t').map(s => s.trim()).filter(Boolean)
  // Heuristic split on multiple spaces if no tabs
  return line.split(/\s{2,}|,\s*/).map(s => s.trim()).filter(Boolean)
}

function safeStr(v: any): string {
  if (v == null) return ''
  const s = String(v).trim()
  return s
}

function toMoney(v: any): number | null {
  if (v == null) return null
  if (typeof v === 'number' && Number.isFinite(v)) return Math.round(v)
  const s = String(v)
  const n = Number(s.replace(/[^0-9.-]/g, ''))
  return Number.isFinite(n) ? Math.round(n) : null
}

function toInt(v: any): number | null {
  if (v == null) return null
  if (typeof v === 'number' && Number.isFinite(v)) return Math.trunc(v)
  const n = Number(String(v).replace(/[^0-9.-]/g, ''))
  return Number.isFinite(n) ? Math.trunc(n) : null
}

function safeHttpUrl(v: any): string | null {
  try {
    const s = safeStr(v)
    if (!s) return null
    const u = new URL(s)
    if (u.protocol === 'http:' || u.protocol === 'https:') return u.toString()
    return null
  } catch { return null }
}

function deriveModelTrimFromBase(baseName: string): { model: string; trim: string } {
  const s = safeStr(baseName)
  // Try 911 first
  let m = s.match(/^(?:Porsche\s*)?(911)\s*(.*)$/i)
  if (m) return { model: '911', trim: safeStr(m[2]) }
  // Cayman/Boxster family
  m = s.match(/^(?:Porsche\s*)?(Cayman|Boxster)\s*(.*)$/i)
  if (m) return { model: m[1], trim: safeStr(m[2]) }
  return { model: '', trim: '' }
}

function deriveModelTrimFromAnyOption(options: VinOptionItem[]): { model: string; trim: string } {
  try {
    for (const o of options || []) {
      const name = safeStr(o?.name || o?.code)
      if (!name) continue
      const m = name.match(/(?:Porsche\s*)?(911|Cayman|Boxster)\s+(GT\d\s*RS|GT\d(?:\s*\.\d)?|GTS\s*4\.0|GTS|Turbo\s*S?|Targa|Spyder|R)\b/i)
      if (m) {
        return { model: m[1], trim: m[2].replace(/\s+/g, ' ').trim() }
      }
    }
  } catch {}
  return { model: '', trim: '' }
}

function codeIsBase(code?: string): boolean {
  const s = safeStr(code).toUpperCase().replace(/[^A-Z0-9]/g, '')
  return s === 'BASE'
}

function isGenericTrim(v: any): boolean {
  const s = safeStr(v).toLowerCase()
  if (!s) return true
  return s === 'base' || s === 'standard' || s === 'std'
}
