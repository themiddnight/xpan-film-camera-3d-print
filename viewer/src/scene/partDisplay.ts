import { useEffect, useLayoutEffect, useRef, type RefObject } from 'react'
import type { Box3, Group, Material } from 'three'
import { partMode, useViewer, useViewerState, type PartMode } from '../state/viewer'
import type { Kind, PartManifest } from '../types'

const GHOST_OPACITY = 0.25
export const INSIDE_SHADE = 0.35
/** Bought parts read as metal; the colour still comes from the manifest. */
export const SURFACE: Record<Kind, { metalness: number; roughness: number }> = {
  printed: { metalness: 0.05, roughness: 0.55 },
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
  useLayoutEffect(() => {
    for (const m of materials) {
      m.clippingPlanes = clipActive ? [viewer.clipPlane] : []
      m.transparent = ghost
      m.opacity = ghost ? GHOST_OPACITY : 1
      m.depthWrite = !ghost
      m.needsUpdate = true
    }
  }, [materials, clipActive, ghost, viewer.clipPlane])

  return { node, mode }
}
