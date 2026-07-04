import { chromium } from 'playwright'
const OUT = '/Users/sarveshwaran/hangover/docs/screenshots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 1050 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.click('nav >> text=Quests')
await page.waitForSelector('text=Your Journey')
await page.waitForTimeout(2500)  // let the draw-in animation finish
// hover a mid-journey point to show the tooltip
const svg = page.locator('svg').first()
const box = await svg.boundingBox()
await page.mouse.move(box.x + box.width * 0.7, box.y + box.height * 0.5)
await page.waitForTimeout(400)
await page.screenshot({ path: `${OUT}/quests.png`, fullPage: true })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
