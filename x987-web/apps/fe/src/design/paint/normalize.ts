import { exteriorPaint, interiorPaint } from './colors'

const trim = (s?: string) => (s || '').trim().toLowerCase()

const exteriorAliases: Record<string, string> = {
  'arctic silver': 'arctic silver metallic',
  'classic silver': 'classic silver metallic',
  'meteor grey': 'meteor gray',
  'carrera white': 'carrara white',
  'aquablue metallic': 'aqua blue metallic',
  'midnight blue': 'midnight blue metallic',
  'basalt black': 'basalt black metallic',
  // User-specified canonical mappings to Rennbow entries
  'red': 'guards red',
  'blue': 'aqua blue metallic',
  'gray': 'meteor grey metallic',
  'grey': 'meteor grey metallic',
  'meteor gray': 'meteor grey metallic',
  'meteor gray metallic': 'meteor grey metallic',
  'yellow': 'speed yellow'
}

const removeWords = (name: string, words: string[]) => {
  let out = name
  for (const w of words) out = out.replace(new RegExp(`\\b${w}\\b`, 'g'), '').replace(/\s+/g, ' ').trim()
  return out
}

export function normalizeExteriorName(name?: string): string {
  let n = trim(name)
  if (!n) return ''
  // prefer explicit alias map first
  n = exteriorAliases[n] || n
  // drop common suffixes but keep known metallics as-is if mapped
  if (!exteriorPaint[n]) {
    n = removeWords(n, ['metallic', 'met.'])
  }
  // re-apply alias after stripping
  n = exteriorAliases[n] || n
  return n
}

export function normalizeInteriorName(name?: string): string {
  let n = trim(name)
  if (!n) return ''
  // standardize spellings
  n = n.replace(/grey/g, 'gray')
  // normalize common phrases
  n = n.replace(/sand\s*beige/g, 'sand beige')
  n = n.replace(/platinum\s*grey/g, 'platinum gray')
  n = n.replace(/platinum\s*gray/g, 'platinum gray')
  n = n.replace(/luxor\s*beige/g, 'luxor beige')
  n = n.replace(/agate\s*gray/g, 'agate gray')
  n = n.replace(/pebble\s*gray/g, 'pebble gray')
  n = n.replace(/amber\s*orange/g, 'amber orange')
  return n
}

// Reduce verbose interior descriptions to a canonical color label
export function simplifyInteriorColorLabel(name?: string): string {
  let s = trim(name)
  if (!s) return ''
  s = s.toLowerCase()
  s = s.replace(/grey/g, 'gray')
  // Prefer first part before '/' when two-tone is listed
  if (s.includes('/')) s = s.split('/')[0]
  // Drop common non-color tokens
  const drop = [
    'partial','standard','leather','lthr','lth','natural','package','int','interior','sports','sport','seats','seat','stitch','stitching','contrast','contrasting','with','w','and','in'
  ]
  for (const w of drop) s = s.replace(new RegExp(`\\b${w}\\b`, 'g'), ' ')
  s = s.replace(/\s+/g, ' ').trim()
  // Expand standalone roots to canonical names
  const roots: Record<string, string> = {
    'agate': 'agate gray',
    'pebble': 'pebble gray',
    'platinum': 'platinum gray',
    'amber': 'amber orange'
  }
  if (roots[s]) s = roots[s]
  // Known multi-word priorities first
  const known = [
    'luxor beige','sand beige','agate gray','pebble gray','platinum gray','amber orange',
    'espresso','cocoa','camel','savanna','tan','brown','stone',
    'black','gray','beige','red','blue','white','ivory','alabaster'
  ]
  const n = normalizeInteriorName(s)
  for (const k of known) {
    const re = new RegExp(`(^|[^a-z])${k}([^a-z]|$)`, 'i')
    if (re.test(n)) return k
  }
  // Fallback: if string ends with a basic hue, prefer that
  const basic = ['black','gray','beige','brown','tan','red','blue','white']
  for (const b of basic) {
    if (new RegExp(`\\b${b}\\b`, 'i').test(n)) return b
  }
  return n
}

export function parseInteriorTwoTone(name?: string): { primary: string; secondary?: string; label: string } {
  const raw = (name || '').trim()
  if (!raw) return { primary: '', label: '' }
  let s = raw
  // Normalize separators
  s = s.replace(/[\u2013\u2014]/g, '-')
  // If explicit two-tone separator exists, split; else treat as single
  let left = s
  let right: string | undefined
  const slashIdx = s.indexOf('/')
  if (slashIdx >= 0) {
    left = s.slice(0, slashIdx)
    right = s.slice(slashIdx + 1)
  }
  const p = simplifyInteriorColorLabel(left)
  const s2 = right ? simplifyInteriorColorLabel(right) : ''
  const primary = p || normalizeInteriorName(left) || left
  const secondary = s2 || undefined
  const label = secondary ? `${primary} / ${secondary}` : primary
  return { primary, secondary, label }
}

export function toPaintHex(kind: 'exterior'|'interior', name?: string): string | null {
  const norm = kind === 'exterior' ? normalizeExteriorName(name) : normalizeInteriorName(name)
  if (!norm) return null
  if (kind === 'exterior') {
    // exact match first, then try with " metallic" suffix
    const exact = exteriorPaint[norm] || exteriorPaint[`${norm} metallic`]
    if (exact) return exact
    // generic fallback based on keywords when CSV uses broad names
    const generic: Record<string, string> = {
      blue: '#2B66A3',
      maroon: '#721616',
      green: '#0A430F',
      red: '#FF0000',
      yellow: '#FFC601',
      orange: '#FF8A00',
      white: '#FFFFFF',
      black: '#000000',
      grey: '#5A5A5A',
      gray: '#5A5A5A',
      silver: '#CCCCCC',
      beige: '#D6CCBB',
      brown: '#5C4836',
      purple: '#62416B',
      violet: '#764283'
    }
    for (const k of Object.keys(generic)) {
      if (norm.includes(k)) return generic[k]
    }
    return null
  }
  return interiorPaint[norm] || null
}

// Decide on black/white text based on relative luminance
function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const s = hex.replace('#', '')
  const n = s.length === 3 ? s.split('').map(c => c + c).join('') : s
  const i = parseInt(n, 16)
  return { r: (i >> 16) & 255, g: (i >> 8) & 255, b: i & 255 }
}
function srgbToLin(c: number) { c/=255; return c<=0.04045? c/12.92 : Math.pow((c+0.055)/1.055, 2.4) }
function luminance(hex?: string | null): number {
  if (!hex) return 0
  const { r, g, b } = hexToRgb(hex)
  const R = srgbToLin(r), G = srgbToLin(g), B = srgbToLin(b)
  return 0.2126*R + 0.7152*G + 0.0722*B
}
export function bestTextColorForPair(hex1?: string | null, hex2?: string | null): '#000'|'#fff' {
  const L = (luminance(hex1) + luminance(hex2)) / 2
  // threshold ~0.4 tends to work on dark UIs
  return L > 0.4 ? '#000' : '#fff'
}

export const bestTextColor = (hex?: string | null) => bestTextColorForPair(hex, hex)

// Heuristics to extract paint props from an arbitrary record (CSV/API variations)
export function extractPaintFromRecord(
  kind: 'exterior' | 'interior',
  rec: Record<string, any>
): { name?: string; hex?: string } {
  const lc = (s: string) => s.toLowerCase()
  const entries = Object.entries(rec || {})
  const nameKeys = [
    `${kind}_color_name`, `${kind}_name`, `${kind}`, `${kind}_color`, `${kind}_paint`, `${kind}Color`, `${kind}Colour`, `${kind}Paint`
  ]
  const hexKeys = [
    `${kind}_hex`, `${kind}_color_hex`, `${kind}_paint_hex`, `${kind}Hex`
  ]
  let name: string | undefined
  let hex: string | undefined
  for (const [k, v] of entries) {
    const key = lc(k)
    if (!name && nameKeys.some(nk => lc(nk) === key)) {
      if (typeof v === 'string' && v.trim()) name = v.trim()
    }
    if (!hex && hexKeys.some(hk => lc(hk) === key)) {
      const s = typeof v === 'string' ? v.trim() : String(v || '').trim()
      if (s && s.startsWith('#')) hex = s
    }
  }
  return { name, hex }
}
