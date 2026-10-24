import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { CHAPTERS } from './chapters'
import { fillCopy, formatNumber } from './spec'

describe('formatNumber', () => {
  it.each([[166.6667, '167'], [66.5, '66.5'], [21.1676, '21.2'], [2.7083, '2.71'], [0.3, '0.3'], [14, '14']])('shows %s as %s', (value, shown) => {
    expect(formatNumber(value)).toBe(shown)
  })
})

describe('chapter copy', () => {
  const manifest = realManifest()

  it('fills every spec reference from the spec sheet', () => {
    const entry = manifest.spec_sheet.find(s => s.id === 'frame_width')!
    expect(fillCopy(manifest, 'A {{value:frame_width}} frame, {{number:frame_width}} wide.'))
      .toBe(`A ${formatNumber(entry.value)} ${entry.unit} frame, ${formatNumber(entry.value)} wide.`)
  })

  it('types no digits outside spec references, except the 135 film format name', () => {
    for (const c of CHAPTERS) {
      const typed = `${c.title} ${c.text}`.replace(/\{\{[^}]+\}\}/g, '').replace(/\b135 film\b/g, '')
      expect(typed, c.id).not.toMatch(/\d/)
    }
  })
})
