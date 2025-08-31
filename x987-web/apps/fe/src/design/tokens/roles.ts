// Semantic (role-based) tokens built on top of the brand palette.
// These help standardize how colors are used across components.

import { palette } from './colors'

export const roles = {
  // Background roles
  bg: {
    page: palette.gray[900],
    surface: palette.gray[800],
    surfaceAlt: palette.gray[700],
    emphasis: palette.gray[600] // used for highlighted cells/chips
  },
  // Threshold chips: five steps per color (two light, three dark)
  threshold: {
    teal: {
      poor: { bg: palette.teal[800], fg: palette.teal[100], alpha: 0.06, alphaFg: 0.45 },
      weak: { bg: palette.teal[700], fg: palette.teal[100], alpha: 0.14, alphaFg: 0.58 },
      fair: { bg: palette.teal[600], fg: palette.teal[100], alpha: 0.28, alphaFg: 0.72 },
      good: { bg: palette.teal[300], fg: palette.teal[900], alpha: 0.60, alphaFg: 0.88 },
      excellent: { bg: palette.teal[200], fg: palette.teal[800], alpha: 1.00, alphaFg: 1.00 }
    },
    green: {
      poor: { bg: palette.green[800], fg: palette.green[100], alpha: 0.06, alphaFg: 0.45 },
      weak: { bg: palette.green[700], fg: palette.green[100], alpha: 0.14, alphaFg: 0.58 },
      fair: { bg: palette.green[600], fg: palette.green[100], alpha: 0.28, alphaFg: 0.72 },
      good: { bg: palette.green[300], fg: palette.green[900], alpha: 0.60, alphaFg: 0.88 },
      excellent: { bg: palette.green[200], fg: palette.green[800], alpha: 1.00, alphaFg: 1.00 }
    }
  },
  // Text roles
  text: {
    primary: '#C9D1D9', // aligned with CLI theme text color
    muted: palette.gray[400],
    subtle: palette.gray[300]
  },
  // Highlight roles (chips/accents)
  highlight: {
    priceBg: palette.gray[600],
    milesBg: palette.gray[600],
    msrpBg: palette.green[600],
    msrpFg: '#C9D1D9'
  },
  // Status roles (FG considered on dark surfaces)
  status: {
    info: palette.teal[400],
    success: palette.green[500],
    warning: palette.yellow[500],
    danger: palette.red[500]
  },
  // Status/accents (examples; expand as needed)
  accent: {
    teal: palette.teal[300],
    yellow: palette.yellow[400],
    orange: palette.orange[500],
    red: palette.red[500],
    green: palette.green[500]
  }
} as const

export type Roles = typeof roles
