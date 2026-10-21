import { memo, useMemo } from 'react'
import { useGLTF } from '@react-three/drei'
import { BackSide, Box3, Color, FrontSide, Mesh, MeshBasicMaterial, MeshStandardMaterial } from 'three'
import { useViewer } from '../state/viewer'
import type { PartManifest } from '../types'
import { gltfToWorld } from './frames'
import { INSIDE_SHADE, SURFACE, usePartDisplay } from './partDisplay'

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

  const { model, materials } = useMemo(() => {
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
    return { model, materials: [front, inside] }
  }, [scene, spec.color, spec.kind])

  const toWorld = useMemo(() => gltfToWorld(viewer.manifest.glb_unit_scale), [viewer.manifest.glb_unit_scale])

  const worldBox = useMemo(() => {
    model.updateMatrixWorld(true)
    return new Box3().setFromObject(model).applyMatrix4(toWorld)
  }, [model, toWorld])

  const { node, mode } = usePartDisplay(spec, materials, worldBox)

  return (
    <group ref={node} visible={mode !== 'hidden'}>
      <group matrixAutoUpdate={false} matrix={toWorld}>
        <primitive object={model} />
      </group>
    </group>
  )
})
