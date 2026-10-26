import { useEffect, useLayoutEffect, useRef, type RefObject } from 'react'
import { useFrame } from '@react-three/fiber'
import type { Box3, Group, Material } from 'three'
import { partMode, useViewer, useViewerState, type PartMode } from '../state/viewer'
import type { Kind, PartManifest } from '../types'

const GHOST_OPACITY = 0.25
export const INSIDE_SHADE = 0.35
/** Edges drawn where faces meet at more than this angle, and every part's silhouette. */
export const OUTLINE_ANGLE_DEG = 30
export const OUTLINE_COLOR = '#8E9194'
/** How far part colours move toward white, so black outlines show on black PETG. */
export const SURFACE_LIFT = 0
/** Stock and bought parts read as metal; the colour still comes from the manifest. */
export const SURFACE: Record<Kind, { metalness: number; roughness: number }> = {
  printed: { metalness: 0.05, roughness: 0.55 },
  stock: { metalness: 0.45, roughness: 0.35 },
  bought: { metalness: 0.45, roughness: 0.35 },
}

/**
 * What every part model shares: it registers its node for MotionDriver, reports its rest box for
 * framing, and keeps its materials in step with its display mode and the section plane.
 */
export function usePartDisplay(spec: PartManifest, materials: readonly Material[], worldBox: Box3): {
  node: RefObject<Group | null>
  mode: PartMode
} {
  const viewer = useViewer()
  const node = useRef<Group>(null)
  const mode = useViewerState(s => partMode(s, spec))
  const clipActive = useViewerState(viewer.selectClipActive)

  useEffect(() => () => materials.forEach(m => m.dispose()), [materials])

  const { reportBox } = viewer.actions
  useLayoutEffect(() => {
    reportBox(spec.name, worldBox)
    return () => reportBox(spec.name, null)
  }, [spec.name, worldBox, reportBox])

  useLayoutEffect(() => {
    viewer.nodes.set(spec.name, node.current)
    return () => viewer.nodes.set(spec.name, null)
  }, [viewer.nodes, spec.name])

  const ghost = mode === 'ghost'
  // How far this part has left the camera in an illustrative shot; 0 for every other part.
  const gone = useRef(0)
  useLayoutEffect(() => {
    for (const m of materials) {
      m.clippingPlanes = clipActive ? [viewer.clipPlane] : []
      m.transparent = ghost || gone.current > 0
      m.opacity = (ghost ? GHOST_OPACITY : 1) * (1 - gone.current)
      m.depthWrite = !m.transparent
      m.needsUpdate = true
    }
  }, [materials, clipActive, ghost, viewer.clipPlane])

  useFrame(() => {
    const remove = viewer.store.getState().remove
    const next = remove && remove.parts.includes(spec.name) ? remove.amount : 0
    if (next === gone.current) return
    gone.current = next
    const transparent = ghost || next > 0
    for (const m of materials) {
      if (m.transparent !== transparent) {
        m.transparent = transparent
        m.depthWrite = !transparent
        m.needsUpdate = true
      }
      m.opacity = (ghost ? GHOST_OPACITY : 1) * (1 - next)
    }
  })

  return { node, mode }
}
