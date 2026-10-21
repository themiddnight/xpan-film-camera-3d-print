import { Box3, Vector3 } from 'three'
import { GROUPS, type Group, type PartManifest } from '../types'

/** How far each group sits in front of the one behind it, at full explode. */
const GROUP_STEP_MM = 70
/** How far a part moves away from its group's centre, at full explode. */
const PART_SPREAD_MM = 30

/** Unit direction from each group's centre to each part's centre; parts at the centre go up. */
export function spreadDirections(
  parts: readonly PartManifest[],
  boxes: Readonly<Record<string, Box3>>,
): Map<string, Vector3> {
  const groupBox = new Map<Group, Box3>()
  for (const p of parts) {
    const box = boxes[p.name]
    if (box) groupBox.set(p.group, (groupBox.get(p.group) ?? new Box3()).union(box))
  }
  const directions = new Map<string, Vector3>()
  for (const p of parts) {
    const box = boxes[p.name]
    const group = groupBox.get(p.group)
    if (!box || !group) continue
    const dir = box.getCenter(new Vector3()).sub(group.getCenter(new Vector3()))
    if (dir.lengthSq() < 1e-6) dir.set(0, 0, 1)
    directions.set(p.name, dir.normalize())
  }
  return directions
}

/** Writes a part's explode offset into `out`: its group steps forward along Y, then it spreads out. */
export function explodeOffset(out: Vector3, group: Group, direction: Vector3 | undefined, amount: number): Vector3 {
  out.set(0, GROUPS.indexOf(group) * GROUP_STEP_MM * amount, 0)
  if (direction) out.addScaledVector(direction, PART_SPREAD_MM * amount)
  return out
}

/** The rest-pose bounds grown to hold the scene at this explode amount, for framing the camera. */
export function explodedBounds(rest: Box3, amount: number): Box3 {
  const spread = PART_SPREAD_MM * amount
  const box = rest.clone()
  box.min.addScalar(-spread)
  box.max.addScalar(spread)
  box.max.y += (GROUPS.length - 1) * GROUP_STEP_MM * amount
  return box
}
