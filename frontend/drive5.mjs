import { chromium } from 'playwright'
const OUT = '/Users/sarveshwaran/hangover/docs/screenshots'
import fs from 'fs'
fs.mkdirSync(OUT, { recursive: true })
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })

// report with alignment banner
await page.click('nav >> text=30-Day Report')
await page.click('text=Generate 30-Day Report')
await page.waitForSelector('text=Goal Consistency', { timeout: 240000 })
await page.waitForTimeout(400)
await page.screenshot({ path: `${OUT}/report.png` })

// graph
await page.click('nav >> text=Memory Graph')
await page.waitForSelector('canvas', { timeout: 60000 })
await page.waitForTimeout(8000)
await page.screenshot({ path: `${OUT}/memory-graph.png` })

// reflect + sources
await page.click('nav >> text=Reflect')
await page.waitForSelector('text=Evidence Sources')
await page.screenshot({ path: `${OUT}/reflect-sources.png` })
console.log('screenshots saved')
await browser.close()
