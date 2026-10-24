import { describe, expect, it } from 'vitest'
import { Box3, MathUtils, PerspectiveCamera, Vector3 } from 'three'
import { createViewer, partMode } from '../state/viewer'
import { realManifest } from '../test/realManifest'
import { applyStaging, SHOT_FOV_DEG, shotFor } from './staging'
import type { Staging } from './story'

const manifest = realManifest()
const [first, second, third] = manifest.parts
const mechanism = manifest.mechanisms[0].id
const other = manifest.mechanisms[1].id

function loadedViewer() {
  const viewer = createViewer(manifest, 'http://localhost/manifest.json')
  manifest.parts.forEach((p, i) => {
    const min = new Vector3(i * 10, -i, 0)
    viewer.actions.reportBox(p.name, new Box3(min, min.clone().add(new Vector3(8 + i, 5, 3 + i))))
  })
  return viewer
}

describe('applyStaging', () => {
  it('hides and ghosts the named parts and returns everything else to rest', () => {
    const viewer = loadedViewer()
    viewer.actions.setPartView(third.name, { visible: false })
    viewer.actions.setExplode(0.7)
    viewer.motion.set(other, 0.5)
    viewer.motion.setPlaying(other, true)

    applyStaging(viewer, { shot: { direction: [1, 1, 1], frame: [] }, scene: { hide: [first.name], ghost: [second.name] }, pose: { [mechanism]: 0.4 } })

    const state = viewer.store.getState()
    expect(partMode(state, first)).toBe('hidden')
    expect(partMode(state, second)).toBe('ghost')
    expect(partMode(state, third)).toBe('solid')
    expect(state.explode).toBe(0)
    expect(state.section.axis).toBe('off')
    expect(viewer.motion.get(mechanism)).toBe(0.4)
    expect(viewer.motion.get(other)).toBe(0)
    expect(viewer.motion.isPlaying(other)).toBe(false)
  })
})

describe('shotFor', () => {
  const shot: Staging['shot'] = { direction: [-0.55, 0.75, 0.45], frame: [first.name, second.name] }

  function projectedCorners(aspect: number) {
    const viewer = loadedViewer()
    const placed = shotFor(viewer, shot, aspect)!
    const camera = new PerspectiveCamera(SHOT_FOV_DEG, aspect, 1, 5000)
    camera.up.set(0, 0, 1)
    camera.position.copy(placed.position)
    camera.lookAt(placed.target)
    camera.updateMatrixWorld()
    const box = viewer.store.getState().boxes[first.name].clone().union(viewer.store.getState().boxes[second.name])
    const corners: Vector3[] = []
    for (let i = 0; i < 8; i++) {
      corners.push(new Vector3(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z).project(camera))
    }
    return corners
  }

  it.each([0.5, 1, 2.4])('keeps every corner of the framed parts in frame and fills it at aspect %s', aspect => {
    const corners = projectedCorners(aspect)
    const extent = Math.max(...corners.flatMap(c => [Math.abs(c.x), Math.abs(c.y)]))
    expect(extent).toBeLessThanOrEqual(1)
    expect(extent).toBeGreaterThan(0.6)
  })

  it('stands on the shot direction and honours a fixed distance', () => {
    const viewer = loadedViewer()
    const placed = shotFor(viewer, { ...shot, distance: 300 }, 1)!
    const offset = placed.position.clone().sub(placed.target)
    expect(offset.length()).toBeCloseTo(300)
    expect(MathUtils.radToDeg(offset.angleTo(new Vector3(...shot.direction)))).toBeCloseTo(0)
  })

  it('has no shot until a framed part has loaded', () => {
    const viewer = createViewer(manifest, 'http://localhost/manifest.json')
    expect(shotFor(viewer, shot, 1)).toBeNull()
  })
})
