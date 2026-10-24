import { useMemo, useRef, type ReactNode } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Vector3, type Group } from 'three'
import { useViewer, useViewerState } from '../state/viewer'

/** Half the swing each way, in radians, and the seconds one full swing takes. */
const SWING_RAD = 0.42
const SWING_SECONDS = 18
/** How fast the camera settles back to its rest angle once the swing stops, per second. */
const SETTLE_RATE = 3

/**
 * Swings its children slowly about the vertical axis through the centre of every part while `spin`
 * is on, and settles them back to rest when it goes off. A swing rather than a full turn keeps the
 * framed silhouette inside the shot fitted at rest.
 */
export function Turntable({ spin, children }: { spin: boolean; children: ReactNode }) {
  const viewer = useViewer()
  const bounds = useViewerState(viewer.selectBounds)
  const invalidate = useThree(s => s.invalidate)
  const outer = useRef<Group>(null)
  const clock = useRef(0)
  const centre = useMemo(() => bounds?.getCenter(new Vector3()) ?? new Vector3(), [bounds])

  useFrame((_, seconds) => {
    const group = outer.current
    if (!group) return
    if (spin) {
      clock.current += Math.min(seconds, 0.1)
      group.rotation.z = SWING_RAD * Math.sin((clock.current / SWING_SECONDS) * Math.PI * 2)
      invalidate()
    } else if (group.rotation.z !== 0) {
      clock.current = 0
      const next = group.rotation.z * Math.max(0, 1 - SETTLE_RATE * Math.min(seconds, 0.1))
      group.rotation.z = Math.abs(next) < 1e-4 ? 0 : next
      invalidate()
    }
  })

  return (
    <group ref={outer} position={centre}>
      <group position={centre.clone().negate()}>{children}</group>
    </group>
  )
}
