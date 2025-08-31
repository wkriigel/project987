#!/usr/bin/env node
// Extract Rennbow paint names and hex from an HTML file
// Usage: node scripts/extract_rennbow.cjs path/to/rennbow.html

const fs = require('fs')
const path = require('path')

function usage() {
  console.log('Usage: node scripts/extract_rennbow.cjs path/to/rennbow.html')
}

const file = process.argv[2]
if (!file) { usage(); process.exit(1) }
const html = fs.readFileSync(file, 'utf8')

// Match <td> blocks containing an <img style="background-color: #HEX ..."> and a <h3>NAME</h3>
const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi
const styleHex = /background-color:\s*([^;"']+)/i
const h3Name = /<h3[^>]*>([\s\S]*?)<\/h3>/i

const map = {}
let m
while ((m = tdRegex.exec(html))) {
  const block = m[1]
  const nameMatch = h3Name.exec(block)
  const styleMatch = styleHex.exec(block)
  if (!nameMatch || !styleMatch) continue
  let name = nameMatch[1].replace(/\s+/g, ' ').trim()
  let hex = styleMatch[1].trim()
  // Normalize
  name = name.replace(/\s+\(.*\)\s*$/, '').trim() // drop parenthetical variants from name key
  const key = name.toLowerCase()
  if (!/^#?[0-9a-f]{3,6}$/i.test(hex) && !/^rgb\(/i.test(hex)) continue
  if (hex.startsWith('rgb')) {
    // naive rgb to hex
    const nums = hex.match(/\d+/g)
    if (nums && nums.length >= 3) {
      const [r,g,b] = nums.map(n=>Math.max(0, Math.min(255, parseInt(n,10))))
      hex = '#' + [r,g,b].map(n=>n.toString(16).padStart(2,'0')).join('')
    } else continue
  }
  if (!hex.startsWith('#')) hex = '#' + hex
  hex = hex.toUpperCase()
  map[key] = hex
}

const outPath = path.resolve(__dirname, '../src/design/paint/rennbow-exterior.json')
fs.writeFileSync(outPath, JSON.stringify(map, null, 2))
console.log(`Extracted ${Object.keys(map).length} colors to ${outPath}`)

