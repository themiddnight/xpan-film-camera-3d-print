import { useEffect, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { MathUtils, Vector3 } from 'three'
import { useViewer, useViewerState } from '../state/viewer'
import { matches, REDUCED_MOTION } from './media'
import { shotFor } from './staging'
import type { Staging } from './story'

const EASE_MS = 800

interface Controls {
  target: Vector3
  update: () => void
}

interface Tween {
  fromPosition: Vector3
  fromTarget: Vector3
  toPosition: Vector3
  toTarget: Vector3
  start: number
}

/**
 * Moves the view's camera to the shot once every part has loaded or failed, and again whenever the
 * shot or the view's aspect changes. The first placement cuts; later ones ease over EASE_MS, or cut
 * under reduced motion. Orbit controls, when the view has them, keep the eased target.
 */
export function ShotRig({ shot }: { shot: Staging['shot'] }) {
  const viewer = useViewer()
  const bounds = useViewerState(viewer.selectBounds)
  const camera = useThree(s => s.camera)
  const controls = useThree(s => s.controls) as unknown as Controls | null
  const invalidate = useThree(s => s.invalidate)
  const aspect = useThree(s => s.size.width / s.size.height)
  const target = useRef<Vector3 | null>(null)
  const tween = useRef<Tween | null>(null)

  const place = (position: Vector3, look: Vector3) => {
    camera.position.copy(position)
    target.current = (target.current ?? new Vector3()).copy(look)
    if (controls) {
      controls.target.copy(look)
      controls.update()
    } else camera.lookAt(look)
  }

  useEffect(() => {
    if (!bounds || !Number.isFinite(aspect) || aspect <= 0) return
    const goal = shotFor(viewer, shot, aspect)
    if (!goal) return
    if (!target.current || matches(REDUCED_MOTION)) {
      tween.current = null
      place(goal.position, goal.target)
    } else {
      tween.current = {
        fromPosition: camera.position.clone(), fromTarget: target.current.clone(),
        toPosition: goal.position, toTarget: goal.target, start: performance.now(),
      }
    }
    invalidate()
  }, [viewer, shot, bounds, aspect, camera, controls, invalidate])

  useFrame(() => {
    const t = tween.current
    if (!t) return
    const f = Math.min(1, (performance.now() - t.start) / EASE_MS)
    const e = MathUtils.smootherstep(f, 0, 1)
    place(t.fromPosition.clone().lerp(t.toPosition, e), t.fromTarget.clone().lerp(t.toTarget, e))
    if (f < 1) invalidate()
    else tween.current = null
  })

  return null
}
