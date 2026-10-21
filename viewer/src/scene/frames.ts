import { Box3, Matrix4, Plane } from 'three'
import type { Section } from '../types'

/** glTF is Y-up; this maps a glTF file point to camera-design mm (X travel, Y front, Z up). */
export function gltfToWorld(unitScale: number): Matrix4 {
  return new Matrix4().makeRotationX(Math.PI / 2).premultiply(new Matrix4().makeScale(unitScale, unitScale, unitScale))
}

/**
 * Writes the section plane into `plane` and returns true, or returns false when there is no section.
 * Parts hold this one Plane, so moving the slider updates it without touching any part.
 */
export function writeSectionPlane(plane: Plane, section: Section, bounds: Box3): boolean {
  const pos = sectionPosition(section, bounds)
  if (pos === null || section.axis === 'off') return false
  const a = section.axis
  const sign = section.flip ? -1 : 1
  // Keeps points with coordinate <= pos (or >= pos when flipped).
  plane.normal.set(a === 'x' ? -sign : 0, a === 'y' ? -sign : 0, a === 'z' ? -sign : 0)
  plane.constant = sign * pos
  return true
}

export function sectionPosition(section: Section, bounds: Box3): number | null {
  if (section.axis === 'off' || bounds.isEmpty()) return null
  const a = section.axis
  return bounds.min[a] + (bounds.max[a] - bounds.min[a]) * section.t
}
