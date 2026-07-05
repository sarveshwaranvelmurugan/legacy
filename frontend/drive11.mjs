import { chromium } from 'playwright'
const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 950 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })

// chat a message
await page.fill('input[placeholder*="say anything"]', 'say just the word hello')
await page.click('button:has-text("Send")')
await page.waitForSelector('div:has-text("legacy") >> text=/hello/i', { timeout: 120000 })

// switch to every tab, then come back — history must survive
for (const t of ['Profile', 'Quests', 'Insights', 'Memory Graph', 'Chat']) {
  await page.click(`nav >> text=${t}`)
  await page.waitForTimeout(1200)
}
const chatSurvived = await page.locator('text=say just the word hello').count()
console.log('chat history survived tab tour:', chatSurvived > 0 ? 'YES' : 'NO')

// quests + profile rendered while we toured
await page.click('nav >> text=Quests')
await page.waitForSelector('text=Character Sheet', { timeout: 60000 })
await page.click('nav >> text=Profile')
await page.waitForSelector('text=What Legacy Knows About You', { timeout: 60000 })
console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
