import React from 'react'

export function ColorSwatch({ hex, label, token }: { hex: string; label?: string; token?: string }) {
  return (
    <div className="flex flex-col items-start gap-1 w-28">
      <div className="h-10 w-full rounded border border-gray-200" style={{ backgroundColor: hex }} />
      <div className="text-[10px] leading-tight">
        {token && <div className="text-gray-700 font-medium">{token}</div>}
        <div className="text-gray-500">{(hex || '').toUpperCase()}</div>
        {label && <div className="text-gray-400">{label}</div>}
      </div>
    </div>
  )
}
