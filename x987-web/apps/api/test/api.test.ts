import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { startServer } from '../src/index'
import fs from 'fs'
import path from 'path'
import os from 'os'

let server: any
let port: number
let tmpDir: string

function url(p: string) {
  return `http://127.0.0.1:${port}${p}`
}

beforeAll(async () => {
  // Create temp directory with a ranking CSV
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'x987-results-'))
  const csvPath = path.join(tmpDir, 'ranking_main_20250101_000000.csv')
  const csv = `year,model,trim,asking_price_usd,mileage,total_options_msrp,options_list,listing_url
` +
              `2010,Cayman,S,$35000,52000,5000,"PASM, PSE, LSD",https://example.com/1
`
  fs.writeFileSync(csvPath, csv)

  process.env.RANKING_RESULTS_DIR = tmpDir
  server = startServer(0) // ephemeral port
  await new Promise<void>((resolve) => server.on('listening', resolve))
  port = (server.address().port) as number
})

afterAll(() => {
  try { server && server.close() } catch {}
  try { fs.rmSync(tmpDir, { recursive: true, force: true }) } catch {}
})

describe('API', () => {
  it('health returns ok', async () => {
    const res = await fetch(url('/api/health'))
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.ok).toBe(true)
  })

  it('ranking returns data', async () => {
    const res = await fetch(url('/api/ranking/latest'))
    const body = await res.json()
    expect(res.status).toBe(200)
    expect(body.count).toBeGreaterThan(0)
    expect(Array.isArray(body.data)).toBe(true)
    expect(body.data[0].year).toBe('2010')
  })
})
