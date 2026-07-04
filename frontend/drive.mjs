// Legacy end-to-end browser drive: reflect -> nodes, report -> all sections,
// hypothesis respond -> recalibration. Screenshots to scratchpad/shots/.
import { chromium } from 'playwright'
import fs from 'fs'

const SHOTS = '/private/tmp/claude-501/-Users-sarveshwaran-hangover/13315d04-54fa-44a5-a2b7-a838bb1185b5/scratchpad/shots'
fs.mkdirSync(SHOTS, { recursive: true })

const errors = []
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', (e) => errors.push(String(e)))

const shot = (name, opts = {}) => page.screenshot({ path: `${SHOTS}/${name}.png`, ...opts })

// 1. Landing / Reflect tab
await page.goto('http://localhost:5199', { waitUntil: 'networkidle' })
await page.waitForSelector('text=What did you actually do today?')
await shot('01-reflect-empty')

// 2. Submit a reflection
await page.fill('textarea', 'Skipped leetcode again today but spent 5 hours polishing the hackathon frontend. I also finally read one chapter of DDIA before bed. Still zero mock interviews.')
await page.click('text=Remember this')
await page.waitForSelector('text=node(s) extracted', { timeout: 60000 })
await shot('02-reflect-nodes')

// 3. Report tab -> generate
await page.click('nav >> text=30-Day Report')
await shot('03-report-empty')
await page.click('text=Generate 30-Day Report')
await page.waitForSelector('text=Goal Consistency', { timeout: 240000 })
await page.waitForTimeout(500)
await shot('04-report-top')
await shot('04b-report-full', { fullPage: true })

// 4. Respond to a pending hypothesis if present
const partially = page.locator('button:has-text("Partially")')
if (await partially.count()) {
  await page.fill('input[placeholder*="missing context"]', 'Fair, but the hackathon IS my strategy to get noticed by companies.')
  await partially.first().click()
  await page.waitForSelector('text=Graph recalibrated', { timeout: 120000 })
  await shot('05-recalibrated')
  console.log('hypothesis responded: OK')
} else {
  console.log('no pending hypothesis button found')
}

// 5. The open question section
await page.locator('text=The Question You\'re Avoiding').scrollIntoViewIfNeeded()
await shot('06-open-question')

console.log('console errors:', errors.length ? errors : 'none')
await browser.close()
