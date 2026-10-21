import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { Box3, Vector3 } from 'three'
import type { ViewName } from '../types'

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

/** Moves the camera to a named view framing the scene; re-runs when `request` changes. */
export function CameraRig({ view, request, bounds }: { view: ViewName; request: number; bounds: Box3 }) {
  const camera = useThree(s => s.camera)
  const controls = useThree(s => s.controls) as unknown as Controls | null

  useEffect(() => {
    if (bounds.isEmpty() || !controls) return
    const centre = bounds.getCenter(new Vector3())
    const radius = bounds.getSize(new Vector3()).length() * DISTANCE_FACTOR + DISTANCE_MARGIN_MM
    const dir = new Vector3(...VIEW_DIRECTIONS[view]).normalize()
    camera.position.copy(centre).addScaledVector(dir, radius)
    controls.target.copy(centre)
    controls.update()
  }, [view, request, bounds, camera, controls])

  return null
}
