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
  t = t.replace(/\bcayman\b/gi, 'Cayman').replace(/\bboxster\b/gi, 'Boxster')
  t = t.replace(/\bblack\s+edition\b/gi, 'BE')
  t = t.replace(/\b(Cayman|Boxster)\s+s\b/gi, '$1 S')
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
  if (/\bpdk\b/.test(low)) return 'PDK'
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

