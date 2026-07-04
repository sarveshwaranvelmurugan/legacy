import { chromium } from 'playwright'
const OUT = '/Users/sarveshwaran/hangover/docs/screenshots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))

await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.waitForSelector('text=Talk to the AI that actually knows you')

await page.fill('input[placeholder*="say anything"]', "what's my favourite bike? one line.")
await page.click('button:has-text("Send")')
await page.waitForSelector('text=/Hunter 350/', { timeout: 240000 })

await page.fill('input[placeholder*="say anything"]', 'nice. is it good for a 12km daily commute?')
await page.click('button:has-text("Send")')
await page.waitForTimeout(1000)
await page.waitForSelector('div.animate-pulse', { state: 'detached', timeout: 240000 })
await page.screenshot({ path: `${OUT}/chat.png` })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
