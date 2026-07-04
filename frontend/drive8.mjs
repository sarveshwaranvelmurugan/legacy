import { chromium } from 'playwright'
const OUT = '/Users/sarveshwaran/hangover/docs/screenshots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.click('nav >> text=Quests')
await page.waitForSelector('text=Character Sheet')
await page.waitForSelector('text=/Lv \\d/', { timeout: 120000 })
// prove the github commit quest — we just pushed, receipts exist
const commitCard = page.locator('div', { hasText: 'Commit hangover repo' }).locator('button:has-text("Prove it")')
await commitCard.first().click()
await page.waitForSelector('text=/✓ /', { timeout: 240000 })
await page.waitForTimeout(500)
await page.screenshot({ path: `${OUT}/quests.png`, fullPage: true })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
