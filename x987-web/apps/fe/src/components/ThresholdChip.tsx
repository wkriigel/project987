import React from 'react'
import { roles } from '../design/tokens/roles'
import { Chip } from './Chip'

type ThresholdLevel = 'poor' | 'weak' | 'fair' | 'good' | 'excellent'
type ThresholdColor = 'teal' | 'green'

export type ThresholdChipProps = {
  text: string | number
  color: ThresholdColor
  level: ThresholdLevel
  size?: 'sm' | 'md' | 'full'
  title?: string
  className?: string
}

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const s = hex.replace('#', '')
  const n = s.length === 3 ? s.split('').map(c => c + c).join('') : s
  const i = parseInt(n, 16)
  return { r: (i >> 16) & 255, g: (i >> 8) & 255, b: i & 255 }
}

export function ThresholdChip({ text, color, level, size, title, className }: ThresholdChipProps) {
  const cfg = (roles.threshold as any)[color][level] as { bg: string; fg: string; alpha?: number; alphaFg?: number }
  const { r, g, b } = hexToRgb(cfg.bg)
  const alpha = cfg.alpha ?? 1
  const bg = `rgba(${r}, ${g}, ${b}, ${alpha})`
  const fgRgb = hexToRgb(cfg.fg)
  const textAlpha = cfg.alphaFg ?? 1
  const fg = `rgba(${fgRgb.r}, ${fgRgb.g}, ${fgRgb.b}, ${textAlpha})`
  return <Chip text={text} bg={bg} color={fg} size={size} title={title} className={className} />
}
