import { memo, use, useEffect, useMemo } from 'react'
import {
  BackSide, Box3, Color, EdgesGeometry, FrontSide, LineBasicMaterial, LineSegments, Mesh, MeshBasicMaterial,
  MeshStandardMaterial, type Object3D,
} from 'three'
import { useViewer } from '../state/viewer'
import type { PartManifest } from '../types'
import { gltfToWorld } from './frames'
import { loadPart } from './partLoader'
import { INSIDE_SHADE, OUTLINE_ANGLE_DEG, OUTLINE_COLOR, SURFACE, SURFACE_LIFT, usePartDisplay } from './partDisplay'

const WHITE = new Color('#FFFFFF')

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
  const loaded = use(loadPart(spec.name, url))
  return loaded instanceof Error ? <FailedPart name={spec.name} /> : <LoadedPart spec={spec} scene={loaded} />
})

function FailedPart({ name }: { name: string }) {
  const { reportFailed } = useViewer().actions
  useEffect(() => reportFailed(name), [name, reportFailed])
  return null
}

function LoadedPart({ spec, scene }: { spec: PartManifest; scene: Object3D }) {
  const viewer = useViewer()

  const { model, materials, edges } = useMemo(() => {
    const model = scene.clone(true)
    const surface = new Color(spec.color).lerp(WHITE, SURFACE_LIFT)
    const front = new MeshStandardMaterial({ color: surface, ...SURFACE[spec.kind], side: FrontSide })
    // Inside faces in a dark tone, so a section reads as a cut rather than a hollow shell.
    const inside = new MeshBasicMaterial({ color: new Color(spec.color).multiplyScalar(INSIDE_SHADE), side: BackSide })
    const outline = new LineBasicMaterial({ color: OUTLINE_COLOR })
    const meshes: Mesh[] = []
    const edges: EdgesGeometry[] = []
    model.traverse(o => { if ((o as Mesh).isMesh) meshes.push(o as Mesh) })
    for (const m of meshes) {
      m.material = front
      m.add(new Mesh(m.geometry, inside))
      const geometry = new EdgesGeometry(m.geometry, OUTLINE_ANGLE_DEG)
      edges.push(geometry)
      m.add(new LineSegments(geometry, outline))
    }
    return { model, materials: [front, inside, outline], edges }
  }, [scene, spec.color, spec.kind])
  useEffect(() => () => edges.forEach(g => g.dispose()), [edges])

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
}
