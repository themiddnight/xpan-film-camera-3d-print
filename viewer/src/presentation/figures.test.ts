import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { FIGURES, PART_NAMES } from './figures'

const manifest = realManifest()

describe('figure staging', () => {
  it('lists exactly the parts the manifest has, so a new part gets a decision', () => {
    expect([...PART_NAMES].sort()).toEqual(manifest.parts.map(p => p.name).sort())
  })

  it.each(FIGURES.map(f => [f.id, f] as const))('%s shows its framed parts and hides every part it does not name', (_id, figure) => {
    const hidden = new Set(figure.scene?.hide)
    const ghost = new Set(figure.scene?.ghost)
    for (const name of figure.shot.frame) {
      expect(hidden.has(name), `${name} is framed but hidden`).toBe(false)
      expect(ghost.has(name), `${name} is framed but ghosted`).toBe(false)
    }
    for (const name of ghost) expect(hidden.has(name), `${name} is ghosted and hidden`).toBe(false)
    expect(hidden.size, 'a figure draws only what it needs').toBeGreaterThan(PART_NAMES.length / 2)
  })

  it('keeps to the three planned figures', () => {
    expect(FIGURES.map(f => f.id)).toEqual(['transport-cutaway', 'interface-rail', 'interface-m42'])
  })
})
