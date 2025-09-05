import type { RankingRecord } from './types'

export function toInt(val: any): number | null {
  if (val == null) return null
  if (typeof val === 'number') return Math.trunc(val)
  const s = String(val).replace(/[^0-9.-]/g, '')
  if (!s || s === '-' || s === '.') return null
  const n = Number(s)
  return Number.isFinite(n) ? Math.trunc(n) : null
}

export function priceK(n: number | null): string {
  if (n == null) return ''
  const k = Math.floor((n + 999) / 1000)
  return `$${k}k`
}

export function milesK(n: number | null): string {
  if (n == null) return ''
  const k = Math.floor((n + 999) / 1000)
  return `${k}k`
}

export function shortHost(url?: string): string {
  if (!url) return ''
  try {
    const u = new URL(url)
    let host = u.host.toLowerCase()
    if (host.startsWith('www.')) host = host.slice(4)
    const parts = host.split('.')
    if (parts.length >= 2) host = parts.slice(-2).join('.')
    return host
  } catch {
    return ''
  }
}

export function normalizeModelTrim(s?: string): string {
  const raw = (s || '').trim()
  if (!raw) return ''
  let t = raw.replace(/\bbase\b/gi, '')
  // Canonical model casing
  t = t.replace(/\bcayman\b/gi, 'Cayman').replace(/\bboxster\b/gi, 'Boxster').replace(/\b911\b/gi, '911')
  // Common special editions
  t = t.replace(/\bblack\s+edition\b/gi, 'BE')
  // Cayman/Boxster S normalization
  t = t.replace(/\b(Cayman|Boxster)\s+s\b/gi, '$1 S')
  // 911: normalize Carrera variants and popular abbreviations
  // Expand C4S/C4/C2 when 911 context exists or Carrera present
  const lower = t.toLowerCase()
  const in911Ctx = /\b911\b/.test(lower) || /\bcarrera\b/.test(lower)
  if (in911Ctx) {
    t = t
      .replace(/\bcarrera\s+4\s*s\b/gi, 'Carrera 4S')
      .replace(/\bcarrera\s+s\b/gi, 'Carrera S')
      .replace(/\bcarrera\s+4\b/gi, 'Carrera 4')
      .replace(/\bcarrera\b/gi, 'Carrera')
      .replace(/\bc4s\b/gi, 'Carrera 4S')
      .replace(/\bc4\b/gi, 'Carrera 4')
      .replace(/\bc2\b/gi, 'Carrera')
      .replace(/\btarga\b/gi, 'Targa')
      .replace(/\bturbo\s*s\b/gi, 'Turbo S')
      .replace(/\bturbo\b/gi, 'Turbo')
      .replace(/\bgt3\s*rs\b/gi, 'GT3 RS')
      .replace(/\bgt2\s*rs\b/gi, 'GT2 RS')
      .replace(/\bgt3\b/gi, 'GT3')
      .replace(/\bgt2\b/gi, 'GT2')
  }
  // Generic trim token normalizations across models
  t = t
    .replace(/\b4\s*s\b/gi, '4S')
    .replace(/\b4\s*gts\b/gi, '4 GTS')
    .replace(/\be[-\s]*hybrid\b/gi, 'E-Hybrid')
    .replace(/\bgts\s*4\.0\b/gi, 'GTS 4.0')
    .replace(/\bturbo\s*s\b/gi, 'Turbo S')
    .replace(/\bgt4\b/gi, 'GT4')
    .replace(/\bgts\b/gi, 'GTS')
  return t.replace(/\s+/g, ' ').trim()
}

export function shortenOption(label: string): string {
  const low = label.toLowerCase().trim()
  if (!low) return ''
  if (low.includes('bose')) return 'BOSE'
  if (low.includes('pcm') && (low.includes('nav') || low.includes('navigation'))) return 'Nav'
  if (low.includes('sport chrono') || /\bchrono\b/.test(low)) return 'Chrono'
  if (low.includes('pasm') || low.includes('adaptive suspension') || low.includes('active suspension')) return 'PASM'
  if (low.includes('sport exhaust') || /\bpse\b/.test(low)) return 'Exhaust'
  if (low.includes('limited slip') || /\blsd\b/.test(low)) return 'LSD'
  // Hide transmissions; PDK/Tiptronic are assumed, not options
  if (/\bpdk\b/.test(low)) return ''
  if (low.includes('heated seat')) return 'Heated'
  if (low.includes('ventilated') || low.includes('cooled seat')) return 'Cooled'
  if (low.includes('sport seat') || low.includes('adaptive sport')) return 'Seats'
  if (low.includes('bi-xenon') || low.includes('xenon') || low.includes('litronic')) return 'Xenon'
  if (low.includes('park assist') || low.includes('parking assist')) return 'Park'
  if (low.includes('wheel')) {
    if (/\b19\b/.test(low)) return '19"'
    if (/\b18\b/.test(low)) return '18"'
    return 'Wheels'
  }
  const token = low.split(/[^a-z0-9]+/).filter(Boolean)[0]
  return token ? token[0].toUpperCase() + token.slice(1) : ''
}

export function optionsCompact(opt: string | string[] | undefined): string {
  if (!opt) return ''
  const arr = Array.isArray(opt) ? opt : String(opt).split(',').map(s => s.trim()).filter(Boolean)
  return arr.map(shortenOption).filter(Boolean).join(', ')
}
