import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { Vector3 } from 'three'
import { useViewer, useViewerState } from '../state/viewer'
import type { ViewName } from '../types'
import { explodedBounds } from './explode'

const VIEW_DIRECTIONS: Record<ViewName, [number, number, number]> = {
  iso: [-0.55, 0.75, 0.45],
  front: [0, 1, 0.0001],
  rear: [0, -1, 0.0001],
  top: [0.0001, 0.0001, 1],
}
const DISTANCE_FACTOR = 2.0
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
    const framed = explodedBounds(bounds, viewer.store.getState().explode)
    const centre = framed.getCenter(new Vector3())
    const radius = framed.getSize(new Vector3()).length() * DISTANCE_FACTOR + DISTANCE_MARGIN_MM
    const dir = new Vector3(...VIEW_DIRECTIONS[view]).normalize()
    camera.position.copy(centre).addScaledVector(dir, radius)
    controls.target.copy(centre)
    controls.update()
  }, [view, request, bounds, camera, controls, viewer.store])

  return null
}
