import { useMemo, useRef, type ReactNode } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Vector3, type Group } from 'three'
import { useViewer, useViewerState } from '../state/viewer'

/** How fast the turntable closes on its target angle, per second, so a scroll jump still eases. */
const FOLLOW_RATE = 8

/**
 * Turns its children about the vertical axis through the centre of every part to the angle `angle`
 * returns, read every frame. A small angle keeps the framed silhouette inside the shot fitted at rest.
 */
export function Turntable({ angle, children }: { angle: () => number; children: ReactNode }) {
  const viewer = useViewer()
  const bounds = useViewerState(viewer.selectBounds)
  const invalidate = useThree(s => s.invalidate)
  const outer = useRef<Group>(null)
  const centre = useMemo(() => bounds?.getCenter(new Vector3()) ?? new Vector3(), [bounds])

  useFrame((_, seconds) => {
    const group = outer.current
    if (!group) return
    const goal = angle()
    const gap = goal - group.rotation.z
    if (gap === 0) return
    group.rotation.z = Math.abs(gap) < 1e-4 ? goal : group.rotation.z + gap * Math.min(1, FOLLOW_RATE * Math.min(seconds, 0.1))
    invalidate()
  })

  return (
    <group ref={outer} position={centre}>
      <group position={centre.clone().negate()}>{children}</group>
    </group>
  )
}
