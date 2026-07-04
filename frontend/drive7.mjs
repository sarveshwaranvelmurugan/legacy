import { chromium } from 'playwright'
const OUT = '/Users/sarveshwaran/hangover/docs/screenshots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 950 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.click('nav >> text=Profile')
await page.waitForSelector('text=/memories since/', { timeout: 300000 })
await page.screenshot({ path: `${OUT}/profile.png`, fullPage: true })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
