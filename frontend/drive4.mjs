import { chromium } from 'playwright'
const SHOTS = '/private/tmp/claude-501/-Users-sarveshwaran-hangover/13315d04-54fa-44a5-a2b7-a838bb1185b5/scratchpad/shots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 950 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))

await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.waitForSelector('text=Evidence Sources')
await page.locator('button:has-text("Sync")').first().click()
await page.waitForSelector('text=/verified evidence node/', { timeout: 180000 })
await page.screenshot({ path: `${SHOTS}/08-sources-synced.png`, fullPage: true })

await page.click('nav >> text=Memory Graph')
await page.waitForSelector('canvas', { timeout: 60000 })
await page.waitForTimeout(8000)
await page.screenshot({ path: `${SHOTS}/09-memory-graph.png` })

console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
