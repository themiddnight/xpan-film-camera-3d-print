// Drives the built public site (dist-public/, served by `vite preview`) and fails on anything a
// visitor would hit: console errors or warnings, sideways scroll, an unresolved {{placeholder}},
// a missing still, a navigator that does not scroll, a phone drag that does not scroll the page.
// Screenshots go to out/verify/. Usage: pnpm build:public && node scripts/verify.mjs
import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const viewerRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const shots = join(viewerRoot, '..', 'out', 'verify')
const site = join(viewerRoot, 'dist-public')
const PORT = 8652
const URL = `http://localhost:${PORT}/`
const LOAD_TIMEOUT_MS = 90_000
const SETTLE_MS = 1500
const FPS_WINDOW_MS = 3000
// A point over the camera on the 375 x 812 layout, above the text card.
const STAGE_Y = 250

const chapters = [...readFileSync(join(viewerRoot, 'src/presentation/chapters.ts'), 'utf8').matchAll(/^ {4}id: '([^']+)'/gm)].map(m => m[1])
const failures = []
const fail = (run, message) => failures.push(`${run}: ${message}`)

if (!existsSync(join(site, 'index.html'))) {
  console.error('dist-public/ is missing. Run: pnpm build:public')
  process.exit(1)
}

const server = spawn('pnpm', ['exec', 'vite', 'preview', '--mode', 'public', '--port', String(PORT), '--strictPort'], { cwd: viewerRoot, stdio: ['ignore', 'ignore', 'inherit'] })
const stop = () => server.kill()
process.on('exit', stop)

async function waitForServer() {
  for (let i = 0; i < 100; i++) {
    try {
      if ((await fetch(URL)).ok) return
    } catch {
      await new Promise(r => setTimeout(r, 200))
    }
  }
  throw new Error('The preview server did not start')
}

// Messages to ignore, each with its reason.
const IGNORED = [
  [/THREE\.Clock/, '@react-three/fiber 9.8.2 still uses THREE.Clock'],
  [/GPU stall due to ReadPixels/, 'the software GL driver headless Chromium uses reports every readback'],
]

function watch(page, run) {
  page.on('console', m => {
    if (!['error', 'warning'].includes(m.type())) return
    if (IGNORED.some(([pattern]) => pattern.test(m.text()))) return
    fail(run, `console ${m.type()}: ${m.text()}`)
  })
  page.on('pageerror', e => fail(run, `page error: ${e.message}`))
  page.on('requestfailed', r => fail(run, `request failed: ${r.url()}`))
  page.on('response', r => { if (r.status() >= 400) fail(run, `${r.status()} ${r.url()}`) })
}

async function checkLayout(page, run) {
  const result = await page.evaluate(() => ({
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    placeholders: document.body.innerText.match(/\{\{[^}]*\}\}/g) ?? [],
    status: document.querySelector('.page-status')?.textContent ?? null,
  }))
  if (result.sideways) fail(run, 'the page scrolls sideways')
  if (result.placeholders.length > 0) fail(run, `unresolved placeholders: ${result.placeholders.join(' ')}`)
  if (result.status) fail(run, `the page shows a status: ${result.status}`)
}

async function waitForLoad(page) {
  const start = Date.now()
  await page.waitForFunction(() => window.presentation && !document.querySelector('.load'), null, { timeout: LOAD_TIMEOUT_MS })
  return Date.now() - start
}

async function shoot(page, name) {
  await page.screenshot({ path: join(shots, `${name}.png`) })
}

async function visitChapters(page, run) {
  for (const id of chapters) {
    await page.evaluate(i => document.querySelector(`[data-chapter="${i}"]`)?.scrollIntoView({ block: 'center' }), id)
    await page.waitForTimeout(SETTLE_MS)
    const active = await page.evaluate(() => window.presentation?.chapter)
    if (active !== id) fail(run, `scrolled to ${id} but the active chapter is ${active}`)
    await shoot(page, `${run}-${id}`)
  }
}

async function frameRate(page) {
  await page.evaluate(() => document.querySelector('[data-chapter="advance"]').scrollIntoView({ block: 'center' }))
  await page.waitForTimeout(SETTLE_MS)
  return page.evaluate(async windowMs => {
    const player = window.presentation.players.get('advance')
    player.restart()
    let frames = 0
    const start = performance.now()
    await new Promise(resolve => {
      const tick = now => {
        frames += 1
        if (now - start < windowMs) requestAnimationFrame(tick)
        else resolve()
      }
      requestAnimationFrame(tick)
    })
    return { fps: Math.round((frames * 1000) / (performance.now() - start)), done: player.getStatus().done }
  }, FPS_WINDOW_MS)
}

async function navigatorScrolls(page, run) {
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(SETTLE_MS)
  const target = chapters[chapters.length - 1]
  await page.locator('.strip-tile', { hasText: /Swap the body/ }).click()
  try {
    await page.waitForFunction(id => window.presentation?.chapter === id, target, { timeout: 15_000 })
  } catch {
    fail(run, `the navigator did not scroll to ${target}`)
  }
}

async function touchScroll(page, context, run) {
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(500)
  const client = await context.newCDPSession(page)
  const drag = () => client.send('Input.synthesizeScrollGesture', { x: 190, y: STAGE_Y, yDistance: -400, gestureSourceType: 'touch', speed: 800 })
  await drag()
  await page.waitForTimeout(500)
  const moved = await page.evaluate(() => window.scrollY)
  if (moved < 100) fail(run, `a one-finger drag on the stage scrolled the page ${moved}px`)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.getByRole('button', { name: 'Explore' }).click()
  await page.waitForTimeout(300)
  await drag()
  await page.waitForTimeout(500)
  const explored = await page.evaluate(() => window.scrollY)
  if (explored > 20) fail(run, `with Explore on, a drag on the stage scrolled the page ${explored}px`)
  await client.detach()
}

const RUNS = [
  { name: 'desktop', viewport: { width: 1440, height: 900 } },
  { name: 'phone', viewport: { width: 375, height: 812 }, phone: true },
  { name: 'desktop-reduced', viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' },
  { name: 'desktop-no-webgl', viewport: { width: 1440, height: 900 }, noWebGL: true },
  { name: 'phone-no-webgl', viewport: { width: 375, height: 812 }, phone: true, noWebGL: true },
]

const report = []
try {
  await waitForServer()
  mkdirSync(shots, { recursive: true })
  for (const id of chapters) {
    if (!existsSync(join(site, 'stills', `${id}.png`))) fail('stills', `dist-public/stills/${id}.png is missing. Run: pnpm stills && pnpm build:public`)
  }
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
  for (const run of RUNS) {
    const context = await browser.newContext({
      viewport: run.viewport,
      hasTouch: run.phone ?? false,
      isMobile: run.phone ?? false,
      reducedMotion: run.reducedMotion ?? 'no-preference',
    })
    if (run.noWebGL) {
      await context.addInitScript(() => {
        const original = HTMLCanvasElement.prototype.getContext
        HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
          return /webgl/i.test(type) ? null : original.call(this, type, ...rest)
        }
      })
    }
    const page = await context.newPage()
    watch(page, run.name)
    await page.goto(URL)
    if (run.noWebGL) {
      await page.waitForSelector('.still-fallback', { timeout: LOAD_TIMEOUT_MS })
      await page.waitForTimeout(SETTLE_MS)
      await checkLayout(page, run.name)
      await page.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager' }))
      await page.waitForTimeout(SETTLE_MS)
      const broken = await page.evaluate(() => [...document.querySelectorAll('.fallback-chapter img')].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src')))
      if (broken.length > 0) fail(run.name, `stills did not load: ${broken.join(' ')}`)
      const figures = await page.evaluate(() => document.querySelectorAll('.figure-box').length)
      if (figures > 0) fail(run.name, 'a 3D figure box shows without WebGL')
      await shoot(page, `${run.name}-fallback`)
      await context.close()
      continue
    }
    const loadMs = await waitForLoad(page)
    await page.waitForTimeout(SETTLE_MS)
    await checkLayout(page, run.name)
    await visitChapters(page, run.name)
    const entry = { run: run.name, loadMs }
    if (run.name === 'desktop') {
      entry.advance = await frameRate(page)
      await navigatorScrolls(page, run.name)
    }
    if (run.phone) await touchScroll(page, context, run.name)
    if (run.reducedMotion) {
      const playing = await page.evaluate(() => [...window.presentation.players.values()].some(p => p.getStatus().running || p.getStatus().done > 0))
      if (playing) fail(run.name, 'a motion played by itself under reduced motion')
    }
    await page.evaluate(() => document.querySelector('#maker').scrollIntoView())
    await page.waitForTimeout(SETTLE_MS)
    await checkLayout(page, run.name)
    await shoot(page, `${run.name}-maker`)
    report.push(entry)
    await context.close()
  }
  await browser.close()
} catch (e) {
  fail('verify', e instanceof Error ? e.message : String(e))
} finally {
  stop()
}

for (const r of report) console.log(`${r.run}: loaded in ${r.loadMs} ms${r.advance ? `, ${r.advance.fps} frames per second during the advance motion (software GL, so only a floor)` : ''}`)
if (failures.length > 0) {
  console.error(`\n${failures.length} problem${failures.length === 1 ? '' : 's'}:\n${[...new Set(failures)].map(f => `  ${f}`).join('\n')}`)
  process.exit(1)
}
console.log(`\nAll runs passed. Screenshots are in ${shots}`)
