import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { inventory } from './parts'
import { tally } from './PartsInventory'

describe('tally', () => {
  const modules = inventory(realManifest())
  const lineOf = (group: string) => tally(modules.find(m => m.group === group)!.lists)

  it.each([
    ['film-back', '30 pieces: 13 printed, 10 made from stock, 7 bought'],
    ['body', '12 pieces: 6 printed, 4 made from stock, 2 bought'],
    ['pinhole', '9 pieces: 5 printed, 3 made from stock, 1 bought'],
  ])('reads the total first, then each kind, for %s', (group, line) => {
    expect(lineOf(group)).toBe(line)
  })

  it('leaves out a kind with no pieces and says "piece" for one', () => {
    expect(tally([{ kind: 'printed', items: [], pieces: 0 }, { kind: 'bought', items: [], pieces: 1 }])).toBe('1 piece: 1 bought')
  })
})
