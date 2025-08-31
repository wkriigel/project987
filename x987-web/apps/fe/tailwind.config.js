/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx,mdx}',
    './.storybook/**/*.{ts,tsx,js,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        // Monochrome ramp (aligned with Python THEME grays)
        gray: {
          50:  '#DEE4EC',
          100: '#C2CBD6',
          200: '#A5AFBA',
          300: '#8794A2',
          400: '#6B7785',
          500: '#4D5967',
          600: '#3A4654',
          700: '#252F3A',
          800: '#1A222C',
          900: '#121820'
        },
        // Teal ramp (derived from THEME teal_1..6, expanded)
        teal: {
          50:  '#E6FFFC',
          100: '#BFF9F4',
          200: '#5FFBF1', // teal_1
          300: '#37E9DF', // teal_2
          400: '#19E1D6', // teal_3
          500: '#3FB8B0', // teal_4
          600: '#5E8F91', // teal_5
          700: '#6F7F82', // teal_6
          800: '#3E5D5D',
          900: '#284241'
        },
        // Yellow (for accents; complementary to teal)
        yellow: {
          50:  '#FFFBEA',
          100: '#FFF3C4',
          200: '#FCE588',
          300: '#FADB5F',
          400: '#F7C948',
          500: '#F0B429',
          600: '#DE911D',
          700: '#CB6E17',
          800: '#B44D12',
          900: '#8D2B0B'
        },
        // Orange ramp (aligned with Python oranges, smoothed)
        orange: {
          50:  '#FFF4E6',
          100: '#FFE6CC',
          200: '#FFD7B3',
          300: '#FFC999',
          400: '#FFB87D',
          500: '#FF6A1A', // orange_cayman_s
          600: '#FF8A3D',
          700: '#E05E14',
          800: '#B94A10',
          900: '#8C370C'
        },
        // Red ramp (aligned with Guards Red family)
        red: {
          50:  '#FDECEC',
          100: '#F9D1D1',
          200: '#F3A8A8',
          300: '#EC7F7F',
          400: '#E45757',
          500: '#D0191A', // guards red reference
          600: '#B91718',
          700: '#A01415',
          800: '#7E1011',
          900: '#5C0C0D'
        },
        // Green ramp (used for MSRP highlights and deal-positive cues)
        green: {
          50:  '#E8F5F0',
          100: '#CFE9DE',
          200: '#A8D7C3',
          300: '#7FC4A6',
          400: '#57B189',
          500: '#2B8C68',
          600: '#2B4A40', // msrp_bg (dim green background)
          700: '#226B4F',
          800: '#1B5440',
          900: '#153F31'
        },
        // Existing custom tokens
        msrpBg: '#2B4A40',
        priceBg: '#3A4654'
      }
    },
  },
  plugins: [],
}
