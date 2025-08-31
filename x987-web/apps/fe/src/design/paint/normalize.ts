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
  // map phrases to canonical tokens
  n = n.replace(/sand\s*beige/g, 'sand beige')
  n = n.replace(/platinum\s*grey/g, 'platinum gray')
  return n
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
