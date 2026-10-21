import { memo, useEffect, useLayoutEffect, useMemo, useRef } from 'react'
import { useGLTF } from '@react-three/drei'
import {
  BackSide, Box3, Color, FrontSide, Group, Mesh, MeshBasicMaterial, MeshStandardMaterial,
} from 'three'
import { partMode, useViewer, useViewerState } from '../state/viewer'
import type { Kind, PartManifest } from '../types'
import { gltfToWorld } from './frames'

const GHOST_OPACITY = 0.25
const INSIDE_SHADE = 0.35
/** Bought parts read as metal; the colour still comes from the manifest. */
const SURFACE: Record<Kind, { metalness: number; roughness: number }> = {
  printed: { metalness: 0.05, roughness: 0.55 },
  bought: { metalness: 0.45, roughness: 0.35 },
}

interface Props {
  spec: PartManifest
  url: string
}

/**
 * One exported part in world (camera-design mm) coordinates. The outer node carries the mechanism
 * and explode transform, which MotionDriver writes each frame; the GLB hangs under the glTF-to-world map.
 * Memoised, and it subscribes only to its own display mode, so a slider drag renders no part.
 */
export const PartModel = memo(function PartModel({ spec, url }: Props) {
  const viewer = useViewer()
  const { scene } = useGLTF(url)
  const node = useRef<Group>(null)
  const mode = useViewerState(s => partMode(s, spec))
  const clipActive = useViewerState(viewer.selectClipActive)

  const { model, front, inside } = useMemo(() => {
    const model = scene.clone(true)
    const front = new MeshStandardMaterial({ color: spec.color, ...SURFACE[spec.kind], side: FrontSide })
    // Inside faces in a dark tone, so a section reads as a cut rather than a hollow shell.
    const inside = new MeshBasicMaterial({ color: new Color(spec.color).multiplyScalar(INSIDE_SHADE), side: BackSide })
    const meshes: Mesh[] = []
    model.traverse(o => { if ((o as Mesh).isMesh) meshes.push(o as Mesh) })
    for (const m of meshes) {
      m.material = front
      m.add(new Mesh(m.geometry, inside))
    }
    return { model, front, inside }
  }, [scene, spec.color, spec.kind])

  const toWorld = useMemo(() => gltfToWorld(viewer.manifest.glb_unit_scale), [viewer.manifest.glb_unit_scale])

  const worldBox = useMemo(() => {
    model.updateMatrixWorld(true)
    return new Box3().setFromObject(model).applyMatrix4(toWorld)
  }, [model, toWorld])

  useEffect(() => () => { front.dispose(); inside.dispose() }, [front, inside])

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
    for (const m of [front, inside]) {
      m.clippingPlanes = clipActive ? [viewer.clipPlane] : []
      m.transparent = ghost
      m.opacity = ghost ? GHOST_OPACITY : 1
      m.depthWrite = !ghost
      m.needsUpdate = true
    }
  }, [front, inside, clipActive, ghost, viewer.clipPlane])

  return (
    <group ref={node} visible={mode !== 'hidden'}>
      <group matrixAutoUpdate={false} matrix={toWorld}>
        <primitive object={model} />
      </group>
    </group>
  )
})
