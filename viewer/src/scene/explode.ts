import { Box3, Vector3 } from 'three'
import type { PartManifest } from '../types'
import { GROUP_OFFSET, LIFT_CLEAR, PART_OFFSET } from './explodeLayout'

/** Each part's offset at full explode, from the layout table. A lifted part needs its own and its reference box. */
export function explodeVectors(
  parts: readonly PartManifest[],
  boxes: Readonly<Record<string, Box3>>,
): Map<string, Vector3> {
  const vectors = new Map<string, Vector3>()
  for (const p of parts) {
    const lift = LIFT_CLEAR[p.name]
    const box = boxes[p.name]
    const above = lift && boxes[lift.above]
    if (lift && box && above) vectors.set(p.name, new Vector3(0, 0, above.max.z - box.min.z + lift.air))
    else vectors.set(p.name, new Vector3(...(PART_OFFSET[p.name] ?? GROUP_OFFSET[p.group])))
  }
  return vectors
}

/** Writes a part's explode offset into `out`. */
export function explodeOffset(out: Vector3, vector: Vector3 | undefined, amount: number): Vector3 {
  return vector ? out.copy(vector).multiplyScalar(amount) : out.set(0, 0, 0)
}

/** The bounds of the named parts (all when `include` is omitted) where they sit at this explode amount. */
export function explodedBounds(
  parts: readonly PartManifest[],
  boxes: Readonly<Record<string, Box3>>,
  amount: number,
  include: (part: PartManifest) => boolean = () => true,
): Box3 {
  const vectors = explodeVectors(parts, boxes)
  const bounds = new Box3()
  const offset = new Vector3()
  for (const p of parts) {
    const box = boxes[p.name]
    if (!box || !include(p)) continue
    bounds.union(box.clone().translate(explodeOffset(offset, vectors.get(p.name), amount)))
  }
  return bounds
}
