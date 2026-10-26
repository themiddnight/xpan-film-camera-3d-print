import { describe, expect, it } from 'vitest'
import bomMarkdown from '../../../docs/bom.md?raw'
import { realManifest } from '../test/realManifest'
import { parseBom } from './bom'
import { DOCS } from './content'
import { splitBlocks, splitDoc } from './maker'

/** Names with digits in them that the copy may type: the lens mount and the film format. */
const NAMES_WITH_DIGITS = /\bM42\b|\b135 film\b/g

describe('maker documents', () => {
  it('type no digits outside spec references and the names of the mount and the film format', () => {
    for (const { id, markdown } of DOCS) {
      const typed = markdown.replace(/\{\{[^}]+\}\}/g, '').replace(NAMES_WITH_DIGITS, '')
      expect(typed, id).not.toMatch(/\d/)
    }
  })

  it('open with a title and use no title elsewhere', () => {
    for (const { id, markdown } of DOCS) {
      expect(splitDoc(markdown).title, id).not.toBeNull()
      expect(markdown.match(/^## /gm)?.length, id).toBe(1)
    }
  })

  it('carry the draft note in the interface and the pending note in printing', () => {
    const text = (id: string) => DOCS.find(d => d.id === id)!.markdown
    expect(text('interface')).toContain('Draft. Not locked until a test print confirms it.')
    expect(text('printing').match(/Coming after the test print\./g)).toHaveLength(2)
  })

  it('show a spec value only for an id in the spec sheet', () => {
    const ids = new Set(realManifest().spec_sheet.map(s => s.id))
    for (const { id, markdown } of DOCS) {
      for (const [, , ref] of markdown.matchAll(/\{\{(value|number):([^}]+)\}\}/g)) {
        expect(ids.has(ref), `${id}: ${ref}`).toBe(true)
      }
    }
  })
})

describe('splitBlocks', () => {
  it('splits prose around each placeholder line, in order', () => {
    expect(splitBlocks('One.\n\n{{figure:a}}\n\nTwo.\n{{spec:specs}}\n{{bom}}\n')).toEqual([
      { kind: 'markdown', text: 'One.' },
      { kind: 'figure', id: 'a' },
      { kind: 'markdown', text: 'Two.' },
      { kind: 'spec', section: 'specs' },
      { kind: 'bom' },
    ])
  })

  it('leaves a placeholder inside a sentence as prose', () => {
    expect(splitBlocks('See {{figure:a}} here.')).toEqual([{ kind: 'markdown', text: 'See {{figure:a}} here.' }])
  })
})

describe('splitDoc', () => {
  it('takes the title from the first heading and keeps the rest', () => {
    expect(splitDoc('## Title\n\nBody.\n\n{{bom}}')).toEqual({
      title: 'Title',
      blocks: [{ kind: 'markdown', text: 'Body.' }, { kind: 'bom' }],
    })
  })
})

describe('parseBom', () => {
  const rows = parseBom(bomMarkdown)

  it('reads every Parts row of docs/bom.md except those marked not needed', () => {
    const table = bomMarkdown.split('## Parts')[1].split('\n## ')[0]
    const all = table.split('\n').filter(l => /^\|\s*\d/.test(l))
    const skipped = all.filter(l => /\|\s*Not needed\s*\|/i.test(l))
    expect(skipped.length).toBeGreaterThan(0)
    expect(rows).toHaveLength(all.length - skipped.length)
  })

  it('keeps number, part, quantity, spec and use, and nothing about search terms or prices', () => {
    for (const row of rows) {
      expect(Object.keys(row)).toEqual(['id', 'part', 'qty', 'spec', 'usedFor'])
      for (const text of Object.values(row)) expect(text.length).toBeGreaterThan(0)
    }
    const shown = JSON.stringify(rows)
    expect(shown).not.toMatch(/[฿฀-๿]/)
    expect(shown).not.toMatch(/Lazada|Shopee/)
  })

  it('reads the first row as written', () => {
    expect(rows[0]).toMatchObject({ id: '1', part: 'Stainless 304 round rod', qty: '1m (or 2 x 500mm)', spec: 'Ø3.0mm, cut to length' })
  })

  it('keeps a lettered number as written', () => {
    expect(rows.map(r => r.id)).toContain('7b')
  })

  it('throws when the table is reshaped', () => {
    expect(() => parseBom('## Parts\n\n| # | Part | Used for |\n|---|---|---|\n| 1 | a | b |')).toThrow('Qty to buy')
    expect(() => parseBom('## Parts\n\n| Part | Qty to buy | Spec | Used for |\n|---|---|---|---|\n| a | 1 | b | c |')).toThrow('"#"')
    expect(() => parseBom('nothing here')).toThrow('no Parts table')
  })
})
