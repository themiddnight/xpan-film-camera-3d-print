import type { Vec3 } from '../types'

/** From the part toward the camera, in camera mm (X travel, Y front, Z up): a true isometric view from the front, left and above. */
export const VIEW_DIRECTION: Vec3 = [-1, 1, 1]

/** CSS pixels per mm of the camera: one scale for every drawing on the page, small enough for the shell to fit a phone. */
export const PX_PER_MM = 2.2

/** Pixels drawn per CSS pixel, so the page downsizes the picture and the ink stays smooth. */
export const SS = 3

/** Margin around a part, so the ink at its edge is never cut off. */
export const PAD_MM = 2

const cross = (a: Vec3, b: Vec3): Vec3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
const dot = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
const unit = (a: Vec3): Vec3 => {
  const n = Math.hypot(...a)
  return [a[0] / n, a[1] / n, a[2] / n]
}

const TOWARD_CAMERA = unit(VIEW_DIRECTION)
/** The picture's horizontal and vertical axes in camera mm, as a camera with Z up and this view direction has them. */
const RIGHT = unit(cross([0, 0, 1], TOWARD_CAMERA))
const UP = cross(TOWARD_CAMERA, RIGHT)

/** The mm a box of this size covers in the drawing: the span of its eight corners along the picture's two axes. */
export function projectedSizeMm(size: Vec3): { width: number; height: number } {
  let right = 0
  let up = 0
  // The span is the sum over the three edges of how far each reaches along the axis.
  for (let axis = 0; axis < 3; axis++) {
    const edge: Vec3 = [axis === 0 ? size[0] : 0, axis === 1 ? size[1] : 0, axis === 2 ? size[2] : 0]
    right += Math.abs(dot(edge, RIGHT))
    up += Math.abs(dot(edge, UP))
  }
  return { width: right, height: up }
}

/** The CSS size of a part's drawing, from its manifest `placed_size_mm` alone: the renderer draws at exactly this size times SS. */
export function drawingSize(size: Vec3): { width: number; height: number } {
  const mm = projectedSizeMm(size)
  return { width: Math.round((mm.width + 2 * PAD_MM) * PX_PER_MM), height: Math.round((mm.height + 2 * PAD_MM) * PX_PER_MM) }
}
