/** A piece of a maker document: prose, or a place where a component is mounted. */
export type Block =
  | { kind: 'markdown'; text: string }
  | { kind: 'figure'; id: string }
  | { kind: 'drawing'; id: string }
  | { kind: 'spec'; section: string }
  | { kind: 'bom' }
  | { kind: 'parts' }
  | { kind: 'unknown'; ref: string }

export interface Doc {
  id: string
  markdown: string
}

/** A component placeholder stands alone on its line: `{{figure:<id>}}`, `{{drawing:<id>}}`, `{{spec:<section>}}`, `{{bom}}` or `{{parts}}`. */
const BLOCK_LINE = /^\{\{(figure|drawing|spec|bom|parts)(?::([^}]*))?\}\}[ \t]*$/
/** Any placeholder left in prose once spec values are filled. */
const ANY_REF = /\{\{[^}]*\}\}/g
const VALUE_REF = /\{\{(?:value|number):[^}]+\}\}/g

/** Splits a document at its component placeholders. A placeholder missing its argument becomes `unknown`. */
export function splitBlocks(markdown: string): Block[] {
  const blocks: Block[] = []
  let prose: string[] = []
  const flush = () => {
    const text = prose.join('\n').trim()
    if (text) blocks.push({ kind: 'markdown', text })
    prose = []
  }
  for (const line of markdown.split('\n')) {
    const match = BLOCK_LINE.exec(line)
    if (!match) {
      prose.push(line)
      continue
    }
    flush()
    const [ref, kind, arg] = match
    if (kind === 'bom' && arg === undefined) blocks.push({ kind: 'bom' })
    else if (kind === 'parts' && arg === undefined) blocks.push({ kind: 'parts' })
    else if (kind === 'figure' && arg) blocks.push({ kind: 'figure', id: arg })
    else if (kind === 'drawing' && arg) blocks.push({ kind: 'drawing', id: arg })
    else if (kind === 'spec' && arg) blocks.push({ kind: 'spec', section: arg })
    else blocks.push({ kind: 'unknown', ref })
  }
  flush()
  return blocks
}

/** A document's `## ` title and the blocks that follow it. */
export function splitDoc(markdown: string): { title: string | null; blocks: Block[] } {
  const blocks = splitBlocks(markdown)
  const first = blocks[0]
  const match = first?.kind === 'markdown' ? /^## ([^\n]+)\n?/.exec(first.text) : null
  if (!match || first.kind !== 'markdown') return { title: null, blocks }
  const rest = first.text.slice(match[0].length).trim()
  return { title: match[1].trim(), blocks: rest ? [{ kind: 'markdown', text: rest }, ...blocks.slice(1)] : blocks.slice(1) }
}

/** Placeholders in prose that nothing handles, such as a misspelled kind or an inline `{{figure:x}}`. */
export function strayRefs(prose: string): string[] {
  return prose.replace(VALUE_REF, '').match(ANY_REF) ?? []
}
