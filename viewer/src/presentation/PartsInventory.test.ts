import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { inventory } from './parts'
import { tally } from './PartsInventory'

describe('tally', () => {
  const modules = inventory(realManifest())
  const lineOf = (group: string) => tally(modules.find(m => m.group === group)!.lists)

  it.each([
    ['film-back', '30 pieces · 13 print · 10 make · 7 buy'],
    ['body', '12 pieces · 6 print · 4 make · 2 buy'],
    ['pinhole', '9 pieces · 5 print · 3 make · 1 buy'],
  ])('reads the total first, then each kind, for %s', (group, line) => {
    expect(lineOf(group)).toBe(line)
  })

  it('leaves out a kind with no pieces and says "piece" for one', () => {
    expect(tally([{ kind: 'printed', items: [], pieces: 0 }, { kind: 'bought', items: [], pieces: 1 }])).toBe('1 piece · 1 buy')
  })
})
