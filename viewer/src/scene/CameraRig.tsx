import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { Box3, Vector3 } from 'three'
import { useViewer, useViewerState } from '../state/viewer'
import type { ViewName } from '../types'
import { explodedBounds } from './explode'

const VIEW_DIRECTIONS: Record<ViewName, [number, number, number]> = {
  iso: [-0.55, 0.75, 0.45],
  front: [0, 1, 0.0001],
  rear: [0, -1, 0.0001],
  top: [0.0001, 0.0001, 1],
  mechanism: [0.5, -0.7, 0.62],
}
const DISTANCE_FACTOR = 2.0
/** The mechanism view frames a few small parts, so it comes in closer than the whole-camera views. */
const MECHANISM_DISTANCE_FACTOR = 1.5
const DISTANCE_MARGIN_MM = 20

interface Controls {
  target: Vector3
  update: () => void
}

/** Moves the camera to the named view, framing the scene, whenever the view or its request counter changes. */
export function CameraRig() {
  const viewer = useViewer()
  const view = useViewerState(s => s.view)
  const request = useViewerState(s => s.viewRequest)
  const bounds = useViewerState(viewer.selectBounds)
  const camera = useThree(s => s.camera)
  const controls = useThree(s => s.controls) as unknown as Controls | null

  useEffect(() => {
    if (!bounds || bounds.isEmpty() || !controls) return
    // The explode amount at the moment of the request sets the framing; moving the slider does not move the camera.
    const state = viewer.store.getState()
    let framed = explodedBounds(viewer.manifest.parts, state.boxes, state.explode)
    let factor = DISTANCE_FACTOR
    if (view === 'mechanism') {
      const parts = new Box3()
      for (const name of state.framed) if (state.boxes[name]) parts.union(state.boxes[name])
      if (!parts.isEmpty()) {
        framed = parts
        factor = MECHANISM_DISTANCE_FACTOR
      }
    }
    const centre = framed.getCenter(new Vector3())
    const radius = framed.getSize(new Vector3()).length() * factor + DISTANCE_MARGIN_MM
    const dir = new Vector3(...VIEW_DIRECTIONS[view]).normalize()
    camera.position.copy(centre).addScaledVector(dir, radius)
    controls.target.copy(centre)
    controls.update()
  }, [view, request, bounds, camera, controls, viewer.store])

  return null
}
