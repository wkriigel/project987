export type ThresholdLevel = 'poor' | 'weak' | 'fair' | 'good' | 'excellent'

export type Orientation = 'lowerIsBetter' | 'higherIsBetter'

// One configurable threshold per metric; bands are defined as multiples of threshold
// to produce five semantic levels. "farOver" is always the most desirable.
export type ThresholdSpec =
  | { orientation: 'lowerIsBetter'; threshold: number; farOver: number; justUnder: number; farUnder: number }
  | { orientation: 'higherIsBetter'; threshold: number; farUnder: number; justUnder: number; farOver: number }

export type MetricKey = 'price' | 'miles' | 'msrp'

export const thresholdSpecs: Record<MetricKey, ThresholdSpec> = {
  // Price: lower is better; using 0.8×, 1.2×, 1.6× bands matches:
  // <20k (brightest), 20–25k, 25–30k, 30–40k, ≥40k (darkest) for T=25k
  price: { orientation: 'lowerIsBetter', threshold: 25_000, farOver: 0.8, justUnder: 1.2, farUnder: 1.6 },
  // Miles: lower is better; bands tailored to your request:
  // <40k (brightest), 40–60k, 60–80k, 80–100k, ≥100k (darkest) for T=60k
  miles: { orientation: 'lowerIsBetter', threshold: 60_000, farOver: 2/3, justUnder: 4/3, farUnder: 5/3 },
  // MSRP options: higher is better (more options value)
  // New bands for T=80k:
  // poor: < 68k | weak: 68k–73k | fair: 73k–77k | good: 77k–80k | excellent: ≥ 80k
  // Encoding: threshold=T=80k, farUnder=0.85 (68k), justUnder=0.9125 (73k), farOver=0.9625 (77k)
  msrp: { orientation: 'higherIsBetter', threshold: 80_000, farUnder: 0.85, justUnder: 0.9125, farOver: 0.9625 }
}

export function toLevelFromSpec(value: number | null | undefined, spec: ThresholdSpec): ThresholdLevel {
  if (value == null) return 'fair'
  const T = spec.threshold
  if (spec.orientation === 'lowerIsBetter') {
    const fo = T * spec.farOver // below this is best (brightest)
    const ju = T * spec.justUnder // above this enters mid-dark
    const fu = T * spec.farUnder // beyond this is darkest
    if (value < fo) return 'excellent'
    if (value < T) return 'good'
    if (value < ju) return 'fair'
    if (value < fu) return 'weak'
    return 'poor'
  } else {
    // For higherIsBetter, interpret:
    //  - threshold (T): boundary between good and excellent (excellent: ≥ T)
    //  - farOver: lower bound factor for 'good' (good: [T*farOver, T))
    //  - justUnder: lower bound factor for 'fair'
    //  - farUnder: lower bound factor for 'weak'
    const fu = T * spec.farUnder // poor: < fu
    const ju = T * spec.justUnder // weak: [fu, ju)
    const go = T * (spec as any).farOver // fair: [ju, go), good: [go, T), excellent: ≥ T
    if (value >= T) return 'excellent'
    if (value >= go) return 'good'
    if (value >= ju) return 'fair'
    if (value >= fu) return 'weak'
    return 'poor'
  }
}

export function describeBands(spec: ThresholdSpec): string[] {
  const T = spec.threshold
  const fmtK = (n: number) => n >= 1000 ? `${Math.round(n/100)/10}k` : `${n}`
  if (spec.orientation === 'lowerIsBetter') {
    const fo = T * spec.farOver
    const ju = T * spec.justUnder
    const fu = T * spec.farUnder
    return [
      `excellent: < ${fmtK(fo)}`,
      `good: ${fmtK(fo)}–${fmtK(T)}`,
      `fair: ${fmtK(T)}–${fmtK(ju)}`,
      `weak: ${fmtK(ju)}–${fmtK(fu)}`,
      `poor: ≥ ${fmtK(fu)}`,
    ]
  } else {
    const fu = T * spec.farUnder
    const ju = T * spec.justUnder
    const go = T * (spec as any).farOver
    return [
      `poor: < ${fmtK(fu)}`,
      `weak: ${fmtK(fu)}–${fmtK(ju)}`,
      `fair: ${fmtK(ju)}–${fmtK(go)}`,
      `good: ${fmtK(go)}–${fmtK(T)}`,
      `excellent: ≥ ${fmtK(T)}`,
    ]
  }
}
