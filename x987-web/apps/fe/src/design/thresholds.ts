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
  // <4k (darkest), 4–6k, 6–8k, 8–12k, ≥12k (brightest) for T=8k
  msrp: { orientation: 'higherIsBetter', threshold: 8_000, farUnder: 0.5, justUnder: 0.75, farOver: 1.5 }
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
    const fu = T * spec.farUnder // below this is darkest
    const ju = T * spec.justUnder // below T but near threshold
    const fo = T * spec.farOver // above this is brightest
    if (value >= fo) return 'excellent'
    if (value >= T) return 'good'
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
    const fo = T * spec.farOver
    return [
      `poor: < ${fmtK(fu)}`,
      `weak: ${fmtK(fu)}–${fmtK(ju)}`,
      `fair: ${fmtK(ju)}–${fmtK(T)}`,
      `good: ${fmtK(T)}–${fmtK(fo)}`,
      `excellent: ≥ ${fmtK(fo)}`,
    ]
  }
}
