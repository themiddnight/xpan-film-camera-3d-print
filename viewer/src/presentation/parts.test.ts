import { describe, expect, it } from 'vitest'
import { parseBom } from './bom'
import bomMarkdown from '../../../docs/bom.md?raw'
import { realManifest } from '../test/realManifest'
import { inventory, partStill, type ModuleInventory } from './parts'
import { validateStory } from './validate'
import type { Group, Kind } from '../types'

const modules = inventory(realManifest())
const module = (group: Group): ModuleInventory => modules.find(m => m.group === group)!
const pieces = (group: Group, kind: Kind) => module(group).lists.find(l => l.kind === kind)!.pieces
const everyItem = modules.flatMap(m => m.lists.flatMap(l => l.items))

describe('inventory of the real manifest', () => {
  it('lists the modules rear to front, each with its three kinds in order', () => {
    expect(modules.map(m => m.group)).toEqual(['film-back', 'body', 'pinhole'])
    for (const m of modules) expect(m.lists.map(l => l.kind)).toEqual(['printed', 'stock', 'bought'])
  })

  it.each([
    ['film-back', 13, 10, 7],
    ['body', 6, 4, 2],
    ['pinhole', 5, 3, 1],
  ] as const)('counts the pieces of %s as %i printed, %i stock, %i bought', (group, printed, stock, bought) => {
    expect([pieces(group, 'printed'), pieces(group, 'stock'), pieces(group, 'bought')]).toEqual([printed, stock, bought])
  })

  it('shows a left and right pair as one card with both pieces counted', () => {
    const buttons = everyItem.filter(i => i.part.startsWith('turn_button'))
    expect(buttons).toHaveLength(1)
    expect(buttons[0]).toMatchObject({ label: 'Turn button', count: 2 })
  })

  it('shows each viewfinder pin pair as one card at the size of one 6 mm stub', () => {
    const pins = everyItem.filter(i => i.part.startsWith('viewfinder_') && i.part.includes('_pin_'))
    expect(pins.map(i => i.label)).toEqual(['Viewfinder rear pin', 'Viewfinder front pin'])
    for (const pin of pins) expect(pin).toMatchObject({ count: 2, largestMm: 6 })
  })

  it('names a part from its snake-case name', () => {
    expect(everyItem.map(i => i.label)).toContain('M42 rear cap ring')
  })

  it('leaves out what loads into the camera', () => {
    const shown = everyItem.map(i => i.part)
    for (const loaded of ['cassette', 'film', 'film_roll']) expect(shown).not.toContain(loaded)
  })

  it('gives every card a size and every stock or bought card a bill-of-materials row', () => {
    for (const m of modules) {
      for (const { kind, items } of m.lists) {
        for (const i of items) {
          expect(i.largestMm).toBeGreaterThan(0)
          expect(i.bom !== null).toBe(kind !== 'printed')
        }
      }
    }
  })

  it('points every card at a row that docs/bom.md lists', () => {
    const rows = new Set(parseBom(bomMarkdown).map(r => r.id))
    const cited = everyItem.flatMap(i => (i.bom === null ? [] : [i.bom]))
    expect(cited.length).toBeGreaterThan(0)
    for (const id of cited) expect(rows, `BOM #${id}`).toContain(id)
  })
})

describe('partStill', () => {
  const manifest = realManifest()
  const names = manifest.parts.map(p => p.name)

  it('frames the named part alone and hides every other part', () => {
    const still = partStill(manifest, 'pawl')!
    expect(still.shot.frame).toEqual(['pawl'])
    expect(new Set(still.scene?.hide)).toEqual(new Set(names.filter(n => n !== 'pawl')))
  })

  it('shoots every part from the same direction', () => {
    const directions = new Set(names.map(n => JSON.stringify(partStill(manifest, n)!.shot.direction)))
    expect(directions.size).toBe(1)
  })

  it('is valid staging for every part of the manifest', () => {
    const stills = names.map(n => partStill(manifest, n)!)
    expect(validateStory(manifest, stills, [])).toEqual([])
  })

  it('has no picture for a part the manifest does not have', () => {
    expect(partStill(manifest, 'no_such_part')).toBeNull()
    expect(partStill(manifest, null)).toBeNull()
  })
})
