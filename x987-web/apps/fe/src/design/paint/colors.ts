// Paint chip colors (vehicle paint), separate from app brand palette.
// Source of truth: Rennbow paint chips (priority), then Python app mappings.
import rennbowExterior from './rennbow-exterior.json'

const seedExteriorPaint: Record<string, string> = {
  // Canonicalized lower-case keys
  'arctic silver metallic': '#C9CCCE',
  'classic silver metallic': '#C6C9CB',
  'meteor gray': '#6E7479',
  'gray': '#8F969C',
  'black': '#0C0E10',
  'white': '#E9EAEA',
  'guards red': '#D0191A',
  'red': '#B0201B',
  'carrara white': '#EDEDED',
  'aqua blue metallic': '#2E6C8E',
  'malachite green metallic': '#2C5F51',
  'silver': '#C9CCCE',
  'midnight blue metallic': '#1A2C4E',
  'basalt black metallic': '#0B0F14'
  , 'blue': '#2B66A3'
  , 'maroon': '#721616'
}

export const exteriorPaint: Record<string, string> = {
  // Fall back to seeds (Python mappings) first...
  ...seedExteriorPaint,
  // ...then prefer extracted Rennbow names for any overlaps
  ...(rennbowExterior as Record<string, string>)
}

// Interior palette derived from Python regex mapping, canonicalized to tags
export const interiorPaint: Record<string, string> = {
  'black': '#0E1114',
  'anthracite': '#0E1114',
  'graphite': '#0E1114',
  'charcoal': '#0E1114',
  'sand beige': '#CBB68B',
  'beige': '#CBB68B',
  'tan': '#B48A60',
  'camel': '#B48A60',
  'savanna': '#B48A60',
  'cocoa': '#6B4A2B',
  'espresso': '#6B4A2B',
  'chocolate': '#6B4A2B',
  'brown': '#6B4A2B',
  'stone': '#A7ADB5',
  'platinum gray': '#A7ADB5',
  'platinum grey': '#A7ADB5',
  'gray': '#A7ADB5',
  'grey': '#A7ADB5',
  'red': '#7E1C1C',
  'carmine': '#7E1C1C',
  'bordeaux': '#7E1C1C',
  'blue': '#2F3A56',
  'navy': '#2F3A56',
  'white': '#E8E8E8',
  'ivory': '#E8E8E8',
  'alabaster': '#E8E8E8'
}
