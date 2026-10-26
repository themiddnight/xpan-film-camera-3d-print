import { GROUPS, GROUP_LABELS, KINDS, type Group, type Kind, type Manifest, type PartManifest } from '../types'
import type { Chapter, ShotDirection } from './story'

/** One card of the inventory: a part, or a left/right pair shown as one. */
export interface InventoryItem {
  /** Name for the card, such as "M42 rear cap ring". */
  label: string
  /** Manifest name of the first member, which the card's thumbnail shows. */
  part: string
  /** Pieces the item stands for, across its members. */
  count: number
  /** Longest side of the part's bounding box, in mm. */
  largestMm: number
  /** The `#` of the docs/bom.md row, for stock and bought items. */
  bom: string | null
}

export interface KindList {
  kind: Kind
  items: readonly InventoryItem[]
  /** Pieces in this list, so the module's count line adds up what the builder handles. */
  pieces: number
}

export interface ModuleInventory {
  group: Group
  label: string
  /** One list per kind, in KINDS order; a kind with nothing to show has no items. */
  lists: readonly KindList[]
}

const SIDE = /_(left|right)$/

/**
 * What a builder needs for each module, from the manifest alone: the parts that belong to the
 * camera, by module and then by how they are got. A `<base>_left`/`<base>_right` pair is one item.
 */
export function inventory(manifest: Manifest): ModuleInventory[] {
  const parts = manifest.parts.filter(p => p.inventory)
  const names = new Set(parts.map(p => p.name))
  const itemName = (name: string) => {
    const base = name.replace(SIDE, '')
    const other = name.endsWith('_left') ? `${base}_right` : `${base}_left`
    return base !== name && names.has(other) ? base : name
  }
  return GROUPS.map(group => ({
    group,
    label: GROUP_LABELS[group],
    lists: KINDS.map(kind => {
      const items = new Map<string, InventoryItem>()
      for (const p of parts.filter(q => q.group === group && q.kind === kind)) {
        const key = itemName(p.name)
        const have = items.get(key)
        items.set(key, have ? { ...have, count: have.count + p.count } : item(p, key))
      }
      const list = [...items.values()]
      return { kind, items: list, pieces: list.reduce((n, i) => n + i.count, 0) }
    }),
  }))
}

function item(p: PartManifest, key: string): InventoryItem {
  const words = key.replaceAll('_', ' ')
  return {
    label: words.charAt(0).toUpperCase() + words.slice(1),
    part: p.name,
    count: p.count,
    largestMm: Math.max(...p.size_mm),
    bom: p.bom,
  }
}

/** The one view every part thumbnail is shot from, so the cards read as a set: from the front, left and above. */
export const THUMBNAIL_DIRECTION: ShotDirection = [-1, 1, 1]

/**
 * The staging `?part=<name>` renders through the still pipeline: that one part, framed alone from
 * THUMBNAIL_DIRECTION, every other part hidden. Null for a name the manifest does not have.
 */
export function partStill(manifest: Manifest, name: string | null): Chapter | null {
  if (name === null || !manifest.parts.some(p => p.name === name)) return null
  return {
    id: `part-${name}`,
    title: name,
    text: '',
    shot: { direction: THUMBNAIL_DIRECTION, frame: [name] },
    scene: { hide: manifest.parts.filter(p => p.name !== name).map(p => p.name) },
  }
}
