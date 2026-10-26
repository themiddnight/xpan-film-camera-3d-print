import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { drawingSize, PAD_MM, PX_PER_MM } from './partDrawing'
import type { Vec3 } from '../types'

const padPx = 2 * PAD_MM * PX_PER_MM

/** The picture axes of a true isometric view from the front, left and above, written out by hand. */
const across = ([x, y]: Vec3) => (-x - y) / Math.SQRT2
const upward = ([x, y, z]: Vec3) => (x - y + 2 * z) / Math.sqrt(6)

describe('drawingSize', () => {
  it('draws a cube s wide as s·√2 across and 4s/√6 tall, plus the margin, at the page scale', () => {
    const s = 20
    const { width, height } = drawingSize([s, s, s])
    expect(width).toBe(Math.round(s * Math.SQRT2 * PX_PER_MM + padPx))
    expect(height).toBe(Math.round(((4 * s) / Math.sqrt(6)) * PX_PER_MM + padPx))
  })

  it('matches the span of the eight corners projected by hand, for a thin and a long box', () => {
    for (const size of [[175, 34.48, 76.3], [3, 3, 30], [12, 0.8, 0.8]] as const) {
      const corners = [0, 1, 2, 3, 4, 5, 6, 7].map((i): Vec3 => [i & 1 ? size[0] : 0, i & 2 ? size[1] : 0, i & 4 ? size[2] : 0])
      const span = (f: (p: Vec3) => number) => Math.max(...corners.map(f)) - Math.min(...corners.map(f))
      const { width, height } = drawingSize(size)
      expect(width).toBe(Math.round((span(across) + 2 * PAD_MM) * PX_PER_MM))
      expect(height).toBe(Math.round((span(upward) + 2 * PAD_MM) * PX_PER_MM))
    }
  })

  it('draws a part twice as long along X wider, and one twice as tall taller', () => {
    expect(drawingSize([40, 10, 10]).width).toBeGreaterThan(drawingSize([20, 10, 10]).width)
    expect(drawingSize([10, 10, 40]).height).toBeGreaterThan(drawingSize([10, 10, 20]).height)
  })

  it('draws a rod the same width along X as along Y, since the view is symmetric between them', () => {
    expect(drawingSize([30, 3, 3]).width).toBe(drawingSize([3, 30, 3]).width)
  })

  it('does not widen the picture for height along Z, which stands upright in the view', () => {
    expect(drawingSize([10, 10, 80]).width).toBe(drawingSize([10, 10, 5]).width)
  })

  it('gives whole CSS pixels, so the card can state them as attributes', () => {
    const { width, height } = drawingSize([7.3, 4.1, 11.9])
    expect(Number.isInteger(width) && Number.isInteger(height)).toBe(true)
  })

  it('fits the largest part of the camera on a 375 px phone with room for the page margin', () => {
    const widest = Math.max(...realManifest().parts.filter(p => p.inventory).map(p => drawingSize(p.placed_size_mm).width))
    expect(widest).toBeLessThanOrEqual(343)
  })
})
