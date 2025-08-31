import React from 'react'

export type ChipProps = {
  text?: string | number
  children?: React.ReactNode
  bg?: string
  color?: string
  dim?: boolean
  size?: 'sm' | 'md' | 'full'
  title?: string
  className?: string
  style?: React.CSSProperties
}

const sizeClass = (s: 'sm' | 'md' | 'full') => (
  s === 'md' ? 'px-2 py-0.5 text-sm'
  : s === 'full' ? 'w-full px-2 py-0.5 text-sm'
  : 'px-8 py-1 text-xs'
)

export function Chip({ text, children, bg, color, dim, size = 'sm', title, className, style }: ChipProps) {
  const st: React.CSSProperties = { ...(style || {}) }
  if (bg) st.backgroundColor = bg
  if (color) st.color = color
  if (dim) st.opacity = 0.7
  const display = size === 'full' ? 'flex' : 'inline-flex'
  const base = `${display} items-center justify-center rounded align-middle text-center ` + sizeClass(size)
  return (
    <span className={base + (className ? ' ' + className : '')} style={st} title={title}>
      {children ?? text}
    </span>
  )
}
