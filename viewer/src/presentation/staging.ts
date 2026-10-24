import { Box3, MathUtils, Vector3 } from 'three'
import { explodedBounds } from '../scene/explode'
import type { Viewer } from '../state/viewer'
import { GROUPS, type PartView, type Section } from '../types'
import type { Staging } from './story'

/** Vertical field of view of every staged camera. */
export const SHOT_FOV_DEG = 30
/** Room around the framed parts, as a fraction of the half-frame. */
const FIT_MARGIN = 1.12

const SHOWN: PartView = { visible: true, ghost: false }
const NO_SECTION: Section = { axis: 'off', t: 0.5, flip: false }

/**
 * Puts the viewer in the state a staging describes. Everything it does not name returns to rest:
 * parts shown, no explode, no section, mechanisms at 0 and none playing. Cycles are left alone.
 */
export function applyStaging(viewer: Viewer, staging: Staging): void {
  const { manifest, motion, store } = viewer
  const scene = staging.scene ?? {}
  const parts: Record<string, PartView> = Object.fromEntries(manifest.parts.map(p => [p.name, SHOWN]))
  for (const name of scene.ghost ?? []) parts[name] = { visible: true, ghost: true }
  for (const name of scene.hide ?? []) parts[name] = { visible: false, ghost: false }
  store.update(s => ({
    ...s,
    parts,
    groups: Object.fromEntries(GROUPS.map(g => [g, SHOWN])) as typeof s.groups,
    filter: 'all',
    explode: scene.explode ?? 0,
    section: scene.section ?? NO_SECTION,
    focus: null,
  }))
  for (const m of manifest.mechanisms) {
    motion.setPlaying(m.id, false)
    motion.set(m.id, staging.pose?.[m.id] ?? 0)
  }
}

/**
 * Where the camera stands to frame the shot's parts and groups, fitted from their rest-pose boxes at
 * the viewer's explode amount so every box corner lands inside the frame at this aspect. Null while
 * none of the framed parts has loaded.
 */
export function shotFor(viewer: Viewer, shot: Staging['shot'], aspect: number): { position: Vector3; target: Vector3 } | null {
  const { boxes, explode } = viewer.store.getState()
  const framed = new Box3()
  for (const p of viewer.manifest.parts) {
    const box = boxes[p.name]
    if (box && (shot.frame.includes(p.name) || shot.frame.includes(p.group))) framed.union(box)
  }
  if (framed.isEmpty()) return null
  const bounds = explodedBounds(framed, explode)
  const target = bounds.getCenter(new Vector3())

  const back = new Vector3(...shot.direction).normalize()
  // Camera up is world Z; a shot straight down or up takes Y as up instead.
  const worldUp = Math.abs(back.z) > 0.999 ? new Vector3(0, 1, 0) : new Vector3(0, 0, 1)
  const right = new Vector3().crossVectors(worldUp, back).normalize()
  const up = new Vector3().crossVectors(back, right)
  const tanV = Math.tan(MathUtils.degToRad(SHOT_FOV_DEG) / 2) / FIT_MARGIN
  const tanH = tanV * aspect

  let distance = 0
  const corner = new Vector3()
  for (let i = 0; i < 8; i++) {
    corner.set(i & 1 ? bounds.max.x : bounds.min.x, i & 2 ? bounds.max.y : bounds.min.y, i & 4 ? bounds.max.z : bounds.min.z).sub(target)
    const depth = corner.dot(back)
    distance = Math.max(distance, depth + Math.abs(corner.dot(right)) / tanH, depth + Math.abs(corner.dot(up)) / tanV)
  }
  return { position: back.multiplyScalar(shot.distance ?? distance).add(target), target }
}
