import { chromium } from 'playwright'
const SHOTS = '/private/tmp/claude-501/-Users-sarveshwaran-hangover/13315d04-54fa-44a5-a2b7-a838bb1185b5/scratchpad/shots'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.click('nav >> text=30-Day Report')
await page.click('text=Generate 30-Day Report')
await page.waitForSelector('text=Goal Consistency', { timeout: 240000 })
await page.waitForTimeout(400)
await page.screenshot({ path: `${SHOTS}/07-final-report.png`, fullPage: true })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
