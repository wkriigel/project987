import React from 'react'
import { Chip } from './Chip'
import { bestTextColor, toPaintHex } from '../design/paint/normalize'

export type PaintChipProps = {
  kind: 'exterior' | 'interior'
  name?: string
  hex?: string
  label?: string
  size?: 'sm' | 'md' | 'full'
  className?: string
}

export function PaintChip({ kind, name, hex, label, size = 'sm', className }: PaintChipProps) {
  const bgHex = hex || toPaintHex(kind, name) || (kind === 'exterior' ? '#444' : '#222')
  const raw = label ?? (name || '')
  const text = toTitleCase(raw)
  const base = bestTextColor(bgHex)
  const color = base === '#000' ? 'rgba(0,0,0,0.55)' : 'rgba(255,255,255,0.55)'
  const cls = (className ? className + ' ' : '') + 'normal-case'
  return <Chip text={text} color={color} size={size} className={cls} style={{ backgroundColor: bgHex }} />
}

export const PaintChipExterior = (p: Omit<PaintChipProps, 'kind'>) => <PaintChip kind="exterior" {...p} />
export const PaintChipInterior = (p: Omit<PaintChipProps, 'kind'>) => <PaintChip kind="interior" {...p} />

function toTitleCase(s: string): string {
  const ACRONYMS = new Set(['GT', 'GTS', 'RS', 'PCCB', 'PDK', 'LE', '4S'])
  const str = (s || '').trim()
  if (!str) return ''
  return str
    .split(/\s+/)
    .map((word) => transformWord(word, ACRONYMS))
    .join(' ')
}

function transformWord(word: string, ACRONYMS: Set<string>): string {
  // Preserve surrounding punctuation (parentheses, quotes, punctuation)
  const m = word.match(/^([\("'\[{]*)(.*?)([\)"'\]\}\.,;:!]*)$/)
  let lead = '', core = word, trail = ''
  if (m) { lead = m[1]; core = m[2]; trail = m[3] }

  // Split on hyphen or slash to title-case parts but keep delimiters
  const parts = core.split(/([\-/])/)
  const titled = parts.map((p) => {
    if (p === '-' || p === '/') return p
    if (!p) return p
    const alnumUpper = p.replace(/[^a-z0-9]/gi, '').toUpperCase()
    if (ACRONYMS.has(alnumUpper)) return alnumUpper
    // 4s, 50th variants: numbers + letters -> keep numbers, upper the rest
    const numMatch = p.match(/^(\d+)([a-z]+)$/i)
    if (numMatch) return numMatch[1] + numMatch[2].toUpperCase()
    // Default: capital first, rest lower
    return p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()
  }).join('')

  return lead + titled + trail
}
