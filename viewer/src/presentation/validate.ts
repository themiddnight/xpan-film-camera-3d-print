import { GROUPS, SPEC_SECTIONS, type Manifest } from '../types'
import { splitBlocks, strayRefs, type Doc } from './maker'
import { specRefs } from './spec'
import type { Chapter, Figure, Staging } from './story'

function stagingErrors(manifest: Manifest, owner: string, staging: Staging): string[] {
  const parts = new Set(manifest.parts.map(p => p.name))
  const mechanisms = new Set(manifest.mechanisms.map(m => m.id))
  const cycles = new Set(manifest.cycles.map(c => c.id))
  const features = new Set(manifest.features.map(f => f.id))
  const errors: string[] = []
  const unknown = (what: string, name: string) => errors.push(`${owner}: unknown ${what} "${name}"`)

  for (const name of staging.shot.frame) {
    if (!parts.has(name) && !GROUPS.some(g => g === name)) unknown('part', name)
  }
  for (const name of [...(staging.scene?.hide ?? []), ...(staging.scene?.ghost ?? [])]) {
    if (!parts.has(name)) unknown('part', name)
  }
  for (const id of Object.keys(staging.pose ?? {})) {
    if (!mechanisms.has(id)) unknown('mechanism', id)
  }
  const scene = staging.scene
  if (scene?.explodeByScroll && scene.explode !== undefined) {
    errors.push(`${owner}: explodeByScroll and explode are set together`)
  }
  for (const name of scene?.remove?.parts ?? []) {
    if (!parts.has(name) && !GROUPS.some(g => g === name)) unknown('part', name)
  }
  if (scene?.remove && scene.remove.slide.every(v => v === 0)) {
    errors.push(`${owner}: remove.slide is zero`)
  }
  const motion = staging.motion
  if (motion && 'cycle' in motion) {
    if (!cycles.has(motion.cycle)) unknown('cycle', motion.cycle)
  } else if (motion) {
    for (const key of motion.keys) {
      for (const id of Object.keys(key.values)) {
        if (!mechanisms.has(id)) unknown('mechanism', id)
      }
    }
  }
  for (const id of staging.pins ?? []) {
    if (!features.has(id)) unknown('feature', id)
  }
  return errors
}

/**
 * Checks every part, group, mechanism, cycle, feature and spec a chapter or figure names against the
 * manifest, so a CAD rename shows up as a message naming the owner, never as a blank stage.
 * An empty list means the story is valid.
 */
export function validateStory(manifest: Manifest, chapters: readonly Chapter[], figures: readonly Figure[]): string[] {
  const errors: string[] = []
  const owners = [
    ...chapters.map(c => ({ owner: `chapter ${c.id}`, id: c.id, staging: c as Staging, copy: `${c.title} ${c.text}` })),
    ...figures.map(f => ({ owner: `figure ${f.id}`, id: f.id, staging: f as Staging, copy: f.caption })),
  ]
  const seen = new Set<string>()
  const specs = new Set(manifest.spec_sheet.map(s => s.id))
  for (const { owner, id, staging, copy } of owners) {
    if (seen.has(owner)) errors.push(`${owner}: duplicate id "${id}"`)
    seen.add(owner)
    errors.push(...stagingErrors(manifest, owner, staging))
    for (const ref of specRefs(copy)) if (!specs.has(ref)) errors.push(`${owner}: unknown spec "${ref}"`)
  }
  return errors
}

/**
 * Checks every component placeholder and spec value in the maker documents: figures and drawings must
 * exist, spec tables must name a real section, values must name a spec entry, and nothing else in
 * braces may be left over. Messages read `document <id>: unknown figure "<name>"`.
 */
export function validateDocs(manifest: Manifest, docs: readonly Doc[], figures: readonly Figure[], drawings: readonly { id: string }[]): string[] {
  const errors: string[] = []
  const specs = new Set(manifest.spec_sheet.map(s => s.id))
  const figureIds = new Set(figures.map(f => f.id))
  const drawingIds = new Set(drawings.map(d => d.id))
  for (const { id, markdown } of docs) {
    const unknown = (what: string, name: string) => errors.push(`document ${id}: unknown ${what} "${name}"`)
    for (const block of splitBlocks(markdown)) {
      switch (block.kind) {
        case 'figure': if (!figureIds.has(block.id)) unknown('figure', block.id); break
        case 'drawing': if (!drawingIds.has(block.id)) unknown('drawing', block.id); break
        case 'spec': if (!SPEC_SECTIONS.some(s => s === block.section)) unknown('spec table', block.section); break
        case 'unknown': unknown('placeholder', block.ref); break
        case 'bom': break
        case 'markdown':
          for (const ref of specRefs(block.text)) if (!specs.has(ref)) unknown('spec', ref)
          for (const ref of strayRefs(block.text)) unknown('placeholder', ref)
          break
      }
    }
  }
  return errors
}
