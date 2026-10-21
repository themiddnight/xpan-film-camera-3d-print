import { Box3, Matrix4, Plane, Vector3 } from 'three'
import type { Section } from '../types'

/** glTF is Y-up; this maps a glTF file point to camera-design mm (X travel, Y front, Z up). */
export function gltfToWorld(unitScale: number): Matrix4 {
  return new Matrix4().makeRotationX(Math.PI / 2).premultiply(new Matrix4().makeScale(unitScale, unitScale, unitScale))
}

export function sectionPlane(section: Section, bounds: Box3): Plane | null {
  if (section.axis === 'off' || bounds.isEmpty()) return null
  const a = section.axis
  const pos = bounds.min[a] + (bounds.max[a] - bounds.min[a]) * section.t
  const sign = section.flip ? -1 : 1
  // Keeps points with coordinate <= pos (or >= pos when flipped).
  const normal = new Vector3(a === 'x' ? -sign : 0, a === 'y' ? -sign : 0, a === 'z' ? -sign : 0)
  return new Plane(normal, sign * pos)
}

export function sectionPosition(section: Section, bounds: Box3): number | null {
  if (section.axis === 'off' || bounds.isEmpty()) return null
  const a = section.axis
  return bounds.min[a] + (bounds.max[a] - bounds.min[a]) * section.t
}
