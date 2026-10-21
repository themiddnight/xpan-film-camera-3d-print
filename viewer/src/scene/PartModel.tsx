import { useEffect, useLayoutEffect, useMemo, useRef, type MutableRefObject } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import {
  BackSide, Box3, Color, FrontSide, Group, Mesh, MeshBasicMaterial, MeshStandardMaterial, Plane, Vector3,
} from 'three'
import type { PartManifest, PartView } from '../types'
import { gltfToWorld } from './frames'

const GHOST_OPACITY = 0.25
const INSIDE_SHADE = 0.35
const EXPLODE_DISTANCE_MM = 60

interface Props {
  spec: PartManifest
  url: string
  unitScale: number
  view: PartView
  clip: Plane | null
  explode: number
  sceneCentre: Vector3
  spinAngle: MutableRefObject<number>
  onBounds: (name: string, box: Box3 | null) => void
}

/**
 * One exported part in world (camera-design mm) coordinates.
 * Nesting: explode offset > spin about the part's own vertical axis > glTF-to-world transform.
 */
export function PartModel({ spec, url, unitScale, view, clip, explode, sceneCentre, spinAngle, onBounds }: Props) {
  const { scene } = useGLTF(url)
  const spinner = useRef<Group>(null)

  const { model, front, inside } = useMemo(() => {
    const model = scene.clone(true)
    const front = new MeshStandardMaterial({ color: spec.color, metalness: 0.05, roughness: 0.55, side: FrontSide })
    // Inside faces in a dark tone, so a section reads as a cut rather than a hollow shell.
    const inside = new MeshBasicMaterial({ color: new Color(spec.color).multiplyScalar(INSIDE_SHADE), side: BackSide })
    const meshes: Mesh[] = []
    model.traverse(o => { if ((o as Mesh).isMesh) meshes.push(o as Mesh) })
    for (const m of meshes) {
      m.material = front
      m.add(new Mesh(m.geometry, inside))
    }
    return { model, front, inside }
  }, [scene, spec.color])

  const toWorld = useMemo(() => gltfToWorld(unitScale), [unitScale])

  const worldBox = useMemo(() => {
    model.updateMatrixWorld(true)
    return new Box3().setFromObject(model).applyMatrix4(toWorld)
  }, [model, toWorld])

  useEffect(() => () => { front.dispose(); inside.dispose() }, [front, inside])

  useLayoutEffect(() => {
    onBounds(spec.name, worldBox)
    return () => onBounds(spec.name, null)
  }, [spec.name, worldBox, onBounds])

  useLayoutEffect(() => {
    for (const m of [front, inside]) {
      m.clippingPlanes = clip ? [clip] : []
      m.transparent = view.ghost
      m.opacity = view.ghost ? GHOST_OPACITY : 1
      m.depthWrite = !view.ghost
      m.needsUpdate = true
    }
  }, [front, inside, clip, view.ghost])

  const offset = useMemo(() => {
    const dir = worldBox.getCenter(new Vector3()).sub(sceneCentre)
    if (dir.lengthSq() < 1e-6) dir.set(0, 0, 1)
    return dir.normalize().multiplyScalar(explode * EXPLODE_DISTANCE_MM)
  }, [worldBox, sceneCentre, explode])

  const axis = spec.spin_axis_xy
  useFrame(() => {
    if (spinner.current && axis) spinner.current.rotation.z = spinAngle.current
  })

  return (
    <group position={offset} visible={view.visible}>
      <group ref={spinner} position={axis ? [axis[0], axis[1], 0] : [0, 0, 0]}>
        <group position={axis ? [-axis[0], -axis[1], 0] : [0, 0, 0]}>
          <group matrixAutoUpdate={false} matrix={toWorld}>
            <primitive object={model} />
          </group>
        </group>
      </group>
    </group>
  )
}
