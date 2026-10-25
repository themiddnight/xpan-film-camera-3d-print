import { useEffect, useState } from 'react'
import { matches, REDUCED_MOTION } from './media'

/** How long the last frame of the bar stays before the screen lifts, ms. */
const HOLD_MS = 450

/**
 * The page has nothing to show until the manifest and then every part is in, so this covers it with
 * the title and a bar. `progress` is null while the manifest itself is still being fetched.
 */
export function Loading({ progress }: { progress: number | null }) {
  const percent = progress === null ? null : Math.round(progress * 100)
  return (
    <div className="loading" role="status" aria-live="polite">
      <div className="loading-body">
        <p className="loading-title">X-Pan pinhole camera</p>
        <div
          className="loading-track" data-sweep={percent === null}
          role="progressbar" aria-label="Loading the camera" aria-valuemin={0} aria-valuemax={100}
          aria-valuenow={percent ?? undefined}
        >
          <span className="loading-bar" style={percent === null ? undefined : { transform: `scaleX(${progress})` }} />
        </div>
        <p className="loading-text">
          {percent === null ? 'Reading the camera' : `Loading the camera, ${percent}%`}
        </p>
      </div>
    </div>
  )
}

/** Keeps the screen mounted while it fades out, then takes it away. */
export function useLoadingDone(done: boolean): { visible: boolean; leaving: boolean } {
  const [state, setState] = useState({ visible: !done, leaving: false })
  useEffect(() => {
    if (!done || !state.visible) return
    setState({ visible: true, leaving: true })
    const timer = setTimeout(() => setState({ visible: false, leaving: false }), matches(REDUCED_MOTION) ? 0 : HOLD_MS)
    return () => clearTimeout(timer)
  }, [done, state.visible])
  return state
}
