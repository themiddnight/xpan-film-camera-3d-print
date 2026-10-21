import { Suspense, useCallback, useEffect, useMemo, useState, type MutableRefObject } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Box3, Vector3 } from 'three'
import type { Manifest, PartView, Section, ViewName } from '../types'
import { CameraRig } from './CameraRig'
import { PartModel } from './PartModel'
import { sectionPlane } from './frames'
import { ErrorBoundary } from '../ErrorBoundary'

const SPIN_RAD_PER_S = Math.PI / 2

interface Props {
  manifest: Manifest
  baseUrl: string
  views: Record<string, PartView>
  section: Section
  explode: number
  spinning: boolean
  spinAngle: MutableRefObject<number>
  view: ViewName
  viewRequest: number
  onBounds: (bounds: Box3) => void
  onPartError: (name: string, error: Error) => void
  failed: ReadonlySet<string>
}

function SpinDriver({ spinning, spinAngle }: { spinning: boolean; spinAngle: MutableRefObject<number> }) {
  useFrame((_, dt) => {
    if (spinning) spinAngle.current += dt * SPIN_RAD_PER_S
  })
  return null
}

export function Viewport(props: Props) {
  const { manifest, baseUrl, views, section, explode, spinning, spinAngle, view, viewRequest, onBounds, onPartError, failed } = props
  const [boxes, setBoxes] = useState<Record<string, Box3>>({})

  const reportBounds = useCallback((name: string, box: Box3 | null) => {
    setBoxes(prev => {
      if (box === null) {
        if (!(name in prev)) return prev
        const { [name]: _removed, ...rest } = prev
        return rest
      }
      return prev[name]?.equals(box) ? prev : { ...prev, [name]: box }
    })
  }, [])

  // A part that failed to load counts as settled, so the rest still frame and report.
  const loadedAll = manifest.parts.every(p => boxes[p.name] || failed.has(p.name))
  const bounds = useMemo(() => {
    const all = new Box3()
    for (const p of manifest.parts) if (boxes[p.name]) all.union(boxes[p.name])
    return all
  }, [boxes, manifest.parts])

  useEffect(() => {
    if (loadedAll) onBounds(bounds)
  }, [loadedAll, bounds, onBounds])

  const centre = useMemo(() => bounds.getCenter(new Vector3()), [bounds])
  const clip = useMemo(() => sectionPlane(section, bounds), [section, bounds])

  return (
    <Canvas
      camera={{ fov: 35, near: 1, far: 5000, up: [0, 0, 1], position: [-150, 200, 150] }}
      gl={{ localClippingEnabled: true, preserveDrawingBuffer: true }}
      flat
    >
      {/* No scene background: the transparent canvas shows the .viewport CSS colour, which follows the theme. */}
      <hemisphereLight args={[0xffffff, 0x8a8a80, 1.6]} />
      <directionalLight position={[-120, 200, 260]} intensity={1.8} />
      <gridHelper args={[400, 40]} rotation={[Math.PI / 2, 0, 0]} material-transparent material-opacity={0.25} />
      {manifest.parts.map(spec => (
        <ErrorBoundary key={spec.name} fallback={null} onError={e => onPartError(spec.name, e)}>
          <Suspense fallback={null}>
            <PartModel
              spec={spec}
              url={new URL(spec.glb, baseUrl).href}
              unitScale={manifest.glb_unit_scale}
              view={views[spec.name]}
              clip={clip}
              explode={explode}
              sceneCentre={centre}
              spinAngle={spinAngle}
              onBounds={reportBounds}
            />
          </Suspense>
        </ErrorBoundary>
      ))}
      <SpinDriver spinning={spinning} spinAngle={spinAngle} />
      <OrbitControls makeDefault enableDamping />
      <CameraRig view={view} request={viewRequest} bounds={bounds} />
    </Canvas>
  )
}
