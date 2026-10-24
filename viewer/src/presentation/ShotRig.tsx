import { useEffect, useLayoutEffect, useMemo, useRef, type RefObject } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { MathUtils, PerspectiveCamera, Vector3 } from 'three'
import { useViewer, useViewerState } from '../state/viewer'
import { matches, REDUCED_MOTION } from './media'
import { SHOT_FOV_DEG, shotFor } from './staging'
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

interface Region {
  x: number
  y: number
  w: number
  h: number
}

/** Where `focus` sits inside `track`, in px; the whole track when there is no focus element. */
function measure(track: HTMLElement | null, focus: HTMLElement | null, width: number, height: number): Region {
  if (!track || !focus) return { x: 0, y: 0, w: width, h: height }
  const t = track.getBoundingClientRect()
  const f = focus.getBoundingClientRect()
  return { x: f.left - t.left, y: f.top - t.top, w: f.width, h: f.height }
}

/**
 * Makes the camera draw over the whole view while it frames the shot in `region`: the vertical field
 * of view grows so the region gets SHOT_FOV_DEG, and the view offset moves the centre of the picture
 * to the centre of the region. Parts outside the shot then run on past the region instead of being cut.
 */
function aimAtRegion(camera: PerspectiveCamera, region: Region, width: number, height: number) {
  const tan = Math.tan(MathUtils.degToRad(SHOT_FOV_DEG) / 2) * (height / region.h)
  camera.fov = MathUtils.radToDeg(2 * Math.atan(tan))
  camera.setViewOffset(width, height, width / 2 - (region.x + region.w / 2), height / 2 - (region.y + region.h / 2), width, height)
  camera.updateProjectionMatrix()
}

/**
 * Moves the view's camera to the shot once every part has loaded or failed, and again whenever the
 * shot or the view's aspect changes. The first placement cuts; later ones ease over EASE_MS, or cut
 * under reduced motion. Orbit controls, when the view has them, keep the eased target. With `focus`,
 * an element inside `track`, the shot is framed in that element's rect and the picture still fills
 * the track.
 */
export function ShotRig({ shot, track, focus }: {
  shot: Staging['shot']
  track?: RefObject<HTMLElement | null>
  focus?: RefObject<HTMLElement | null>
}) {
  const viewer = useViewer()
  const bounds = useViewerState(viewer.selectBounds)
  const camera = useThree(s => s.camera)
  const controls = useThree(s => s.controls) as unknown as Controls | null
  const invalidate = useThree(s => s.invalidate)
  const size = useThree(s => s.size)
  const region = useMemo(
    () => measure(track?.current ?? null, focus?.current ?? null, size.width, size.height),
    [track, focus, size],
  )
  const aspect = region.w / region.h

  useLayoutEffect(() => {
    if (!(camera instanceof PerspectiveCamera) || region.h <= 0) return
    aimAtRegion(camera, region, size.width, size.height)
    invalidate()
  }, [camera, region, size, invalidate])
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
