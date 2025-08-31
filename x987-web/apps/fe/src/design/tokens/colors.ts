// Design tokens: color palette generated in OKLCH
// We generate perceptually-even ramps from a few key brand colors.

type Oklch = { L: number; C: number; h: number }

// -- Color utils (sRGB <-> OKLCH) --
const clamp01 = (x: number) => Math.min(1, Math.max(0, x))

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const s = hex.replace('#', '')
  const n = s.length === 3
    ? s.split('').map((c) => c + c).join('')
    : s
  const i = parseInt(n, 16)
  return { r: (i >> 16) & 255, g: (i >> 8) & 255, b: i & 255 }
}

function srgbToLinear(c: number): number {
  c /= 255
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
}

function linearToSrgb(c: number): number {
  return c <= 0.0031308
    ? 12.92 * c
    : 1.055 * Math.pow(c, 1 / 2.4) - 0.055
}

function rgbToOklab({ r, g, b }: { r: number; g: number; b: number }): { L: number; a: number; b: number } {
  const rl = srgbToLinear(r)
  const gl = srgbToLinear(g)
  const bl = srgbToLinear(b)

  const l = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl
  const m = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl
  const s = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl

  const l_ = Math.cbrt(l)
  const m_ = Math.cbrt(m)
  const s_ = Math.cbrt(s)

  return {
    L: 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
    a: 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
    b: 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
  }
}

function oklabToRgb({ L, a, b }: { L: number; a: number; b: number }): { r: number; g: number; b: number } {
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b
  const s_ = L - 0.0894841775 * a - 1.2914855480 * b

  const l = l_ * l_ * l_
  const m = m_ * m_ * m_
  const s = s_ * s_ * s_

  const rl =  4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
  const gl = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
  const bl =  0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

  const r = Math.round(clamp01(linearToSrgb(rl)) * 255)
  const g = Math.round(clamp01(linearToSrgb(gl)) * 255)
  const b2 = Math.round(clamp01(linearToSrgb(bl)) * 255)
  return { r, g, b: b2 }
}

function rgbToHex({ r, g, b }: { r: number; g: number; b: number }): string {
  const to2 = (n: number) => n.toString(16).padStart(2, '0')
  return `#${to2(r)}${to2(g)}${to2(b)}`.toUpperCase()
}

function hexToOklch(hex: string): Oklch {
  const { r, g, b } = hexToRgb(hex)
  const { L, a, b: bb } = rgbToOklab({ r, g, b })
  const C = Math.hypot(a, bb)
  let h = Math.atan2(bb, a) * (180 / Math.PI)
  if (h < 0) h += 360
  return { L, C, h }
}

function oklchToHex({ L, C, h }: Oklch): string {
  const hr = (h * Math.PI) / 180
  const a = Math.cos(hr) * C
  const b = Math.sin(hr) * C
  return rgbToHex(oklabToRgb({ L, a, b }))
}

// -- Ramp generation --
const STEPS = [100, 200, 300, 400, 500, 600, 700, 800, 900] as const

// Distribute L from light to dark, avoiding extreme "dim" tints.
const lightnessFor = (step: (typeof STEPS)[number]) => {
  const idx = STEPS.indexOf(step)
  const t = idx / (STEPS.length - 1) // 0..1
  // Map 0..1 to L 0.90..0.18 (light -> dark)
  return 0.90 - t * (0.90 - 0.18)
}

// Reduce chroma slightly near extremes to stay in gamut.
const chromaAt = (baseC: number, L: number) => {
  const edgeFalloff = 0.85 - Math.abs(L - 0.5) // higher near middle
  const k = Math.max(0.55, Math.min(1.0, edgeFalloff))
  return baseC * k
}

function makeRampFromSeedHex(hex: string, opts?: { neutral?: boolean }): Record<(typeof STEPS)[number], string> {
  const seed = hexToOklch(hex)
  const hue = opts?.neutral ? 0 : seed.h
  const baseC = opts?.neutral ? 0 : Math.min(0.22, seed.C) // keep reasonable chroma
  const ramp: any = {}
  for (const s of STEPS) {
    const L = lightnessFor(s)
    const C = opts?.neutral ? 0 : chromaAt(baseC, L)
    ramp[s] = oklchToHex({ L, C, h: hue })
  }
  return ramp
}

// Key brand colors (from snippet):
// - Mint/Teal:   #40FFCF
// - Orange:      #FF6F11
// - Yellow/Amber:#FFB000
// - Neutral base:#000000

export const palette = {
  gray:   makeRampFromSeedHex('#000000', { neutral: true }),
  teal:   makeRampFromSeedHex('#40FFCF'),
  yellow: makeRampFromSeedHex('#FFB000'),
  orange: makeRampFromSeedHex('#FF6F11'),
  red:    makeRampFromSeedHex('#D0191A'),
  // Shift green toward forest/olive to separate from teal
  green:  makeRampFromSeedHex('#556B2F')
} as const

export type PaletteName = keyof typeof palette
export type Ramp = typeof palette[PaletteName]

export const ramps: [PaletteName, Ramp][] = Object.entries(palette) as any
