import { GROUPS, type Manifest } from '../types'
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
 * Checks every part, group, mechanism, cycle and feature a chapter or figure names against the
 * manifest, so a CAD rename shows up as a message naming the owner, never as a blank stage.
 * An empty list means the story is valid.
 */
export function validateStory(manifest: Manifest, chapters: readonly Chapter[], figures: readonly Figure[]): string[] {
  const errors: string[] = []
  const owners = [
    ...chapters.map(c => ({ owner: `chapter ${c.id}`, id: c.id, staging: c as Staging })),
    ...figures.map(f => ({ owner: `figure ${f.id}`, id: f.id, staging: f as Staging })),
  ]
  const seen = new Set<string>()
  for (const { owner, id, staging } of owners) {
    if (seen.has(owner)) errors.push(`${owner}: duplicate id "${id}"`)
    seen.add(owner)
    errors.push(...stagingErrors(manifest, owner, staging))
  }
  return errors
}
