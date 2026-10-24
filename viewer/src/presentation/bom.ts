export interface BomRow {
  part: string
  qty: string
  spec: string
  usedFor: string
}

const COLUMNS = { part: 'Part', qty: 'Qty to buy', spec: 'Spec', usedFor: 'Used for' } as const

/** Qty text of a row the bill keeps for the record but nobody needs to buy. */
const NOT_NEEDED = /^not needed$/i

function cells(line: string): string[] {
  return line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim())
}

/**
 * The rows of the Parts table in docs/bom.md, with only the columns a builder needs: part, quantity,
 * spec and what it is used for. Search terms and prices stay out of the public page, as do rows marked
 * "Not needed". Throws when the table or one of those columns is missing, so a reshaped bill is not
 * shown half empty.
 */
export function parseBom(markdown: string): BomRow[] {
  const lines = markdown.split('\n')
  const heading = lines.findIndex(l => /^##\s+Parts\s*$/.test(l))
  const header = lines.findIndex((l, i) => i > heading && heading >= 0 && l.trimStart().startsWith('|'))
  if (header < 0) throw new Error('docs/bom.md has no Parts table')
  const names = cells(lines[header])
  const index = Object.fromEntries(
    Object.entries(COLUMNS).map(([key, name]) => [key, names.indexOf(name)]),
  ) as Record<keyof typeof COLUMNS, number>
  for (const [key, at] of Object.entries(index)) {
    if (at < 0) throw new Error(`docs/bom.md Parts table has no "${COLUMNS[key as keyof typeof COLUMNS]}" column`)
  }
  const rows: BomRow[] = []
  for (const line of lines.slice(header + 2)) {
    if (!line.trimStart().startsWith('|')) break
    const row = cells(line)
    const qty = row[index.qty]
    if (NOT_NEEDED.test(qty)) continue
    rows.push({ part: row[index.part], qty, spec: row[index.spec], usedFor: row[index.usedFor] })
  }
  return rows
}
