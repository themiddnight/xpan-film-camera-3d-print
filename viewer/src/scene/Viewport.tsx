import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { ViewerContext, useViewer } from '../state/viewer'
import { ErrorBoundary } from '../ErrorBoundary'
import { CameraRig } from './CameraRig'
import { ClipSync, MotionDriver } from './MotionDriver'
import { FilmStripModel } from './FilmStripModel'
import { PartModel } from './PartModel'

export function Viewport() {
  // The Canvas renders in its own React root, so the viewer is provided again inside it.
  const viewer = useViewer()
  const { manifest, baseUrl, actions } = viewer
  return (
    <Canvas
      camera={{ fov: 35, near: 1, far: 5000, up: [0, 0, 1], position: [-150, 200, 150] }}
      gl={{ localClippingEnabled: true, preserveDrawingBuffer: true }}
      flat
    >
      <ViewerContext.Provider value={viewer}>
        {/* No scene background: the transparent canvas shows the .viewport CSS colour, which follows the theme. */}
        <hemisphereLight args={[0xffffff, 0x8a8a80, 1.6]} />
        <directionalLight position={[-120, 200, 260]} intensity={1.8} />
        <gridHelper args={[400, 40]} rotation={[Math.PI / 2, 0, 0]} material-transparent material-opacity={0.25} />
        {manifest.parts.map(spec => (
          <ErrorBoundary key={spec.name} fallback={null} onError={e => actions.reportFailed(spec.name, e)}>
            <Suspense fallback={null}>
              {manifest.film_strip?.part === spec.name
                ? <FilmStripModel spec={spec} strip={manifest.film_strip} />
                : <PartModel spec={spec} url={new URL(spec.glb, baseUrl).href} />}
            </Suspense>
          </ErrorBoundary>
        ))}
        <MotionDriver />
        <ClipSync />
        <OrbitControls makeDefault enableDamping />
        <CameraRig />
      </ViewerContext.Provider>
    </Canvas>
  )
}
