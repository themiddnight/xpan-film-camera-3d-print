import { Suspense } from 'react'
import { useViewer } from '../state/viewer'
import { ErrorBoundary } from '../ErrorBoundary'
import { ClipSync, MotionDriver } from './MotionDriver'
import { FilmStripModel } from './FilmStripModel'
import { PartModel } from './PartModel'

/**
 * Every part of the viewer in the context, with the driver that moves them and the section plane sync.
 * Lights, camera and controls belong to the caller: the workshop and the presentation light the parts
 * for different backgrounds. A part that fails to load or to render is marked failed and left out; the
 * rest still render. React logs a render error; partLoader logs a load failure once per page.
 */
export function PartsScene() {
  const { manifest, baseUrl, actions } = useViewer()
  return (
    <>
      {manifest.parts.map(spec => (
        <ErrorBoundary key={spec.name} fallback={null} onError={() => actions.reportFailed(spec.name)}>
          <Suspense fallback={null}>
            {manifest.film_strip?.part === spec.name
              ? <FilmStripModel spec={spec} strip={manifest.film_strip} />
              : <PartModel spec={spec} url={new URL(spec.glb, baseUrl).href} />}
          </Suspense>
        </ErrorBoundary>
      ))}
      <MotionDriver />
      <ClipSync />
    </>
  )
}
