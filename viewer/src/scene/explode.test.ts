import { describe, expect, it } from 'vitest'
import { Box3, Vector3 } from 'three'
import { realManifest } from '../test/realManifest'
import { explodeVectors } from './explode'
import { LIFT_CLEAR, PART_OFFSET } from './explodeLayout'

const manifest = realManifest()
const names = new Set(manifest.parts.map(p => p.name))
const box = (min: [number, number, number], max: [number, number, number]) => new Box3(new Vector3(...min), new Vector3(...max))

describe('explode layout', () => {
  it('names only parts the CAD exports', () => {
    for (const name of [...Object.keys(PART_OFFSET), ...Object.keys(LIFT_CLEAR), ...Object.values(LIFT_CLEAR).map(l => l.above)]) {
      expect(names, name).toContain(name)
    }
  })

  it('stacks the body, the lens mount and the pinhole on the optical axis, in that order', () => {
    const v = explodeVectors(manifest.parts, {})
    const stack = ['pinhole_body', 'm42_shim_ring', 'm42_rear_cap_ring', 'm42_body_cap', 'shutter_housing'].map(n => v.get(n)!)
    for (const s of stack) expect([s.x, s.z]).toEqual([0, 0])
    for (let i = 1; i < stack.length; i++) expect(stack[i].y).toBeGreaterThan(stack[i - 1].y)
  })

  it('lifts the dark slide straight up until it clears the shell', () => {
    const v = explodeVectors(manifest.parts, {
      dark_slide: box([-35, 1, -15], [35, 2, 43]),
      shell: box([-77, -4, -37], [97, 30, 39]),
    }).get('dark_slide')!
    expect([v.x, v.y]).toEqual([0, 0])
    expect(-15 + v.z).toBe(39 + LIFT_CLEAR.dark_slide.air)
  })
})
