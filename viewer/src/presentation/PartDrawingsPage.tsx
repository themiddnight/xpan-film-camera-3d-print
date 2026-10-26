import { useEffect } from 'react'
import type { Manifest } from '../types'

declare global {
  interface Window {
    /** Set by `?drawings`: each drawn part's PNG data URL by manifest name, once `partDrawingsReady` is true. Empty if drawing failed. */
    partDrawings?: Record<string, string>
    partDrawingsReady?: boolean
  }
}

let started = false

/**
 * The `?drawings` route `pnpm stills` loads once for every part drawing. The renderer is imported
 * here and nowhere else, so a visitor to the site never downloads it.
 */
export function PartDrawingsPage({ manifest }: { manifest: Manifest }) {
  useEffect(() => {
    // StrictMode runs this effect twice in the dev server; one render of every part is enough.
    if (started) return
    started = true
    import('./renderPartDrawings')
      .then(m => m.renderPartDrawings(manifest))
      .then(drawings => { window.partDrawings = drawings })
      .catch((e: unknown) => {
        console.error(e instanceof Error ? e.message : String(e))
        window.partDrawings = {}
      })
      .finally(() => { window.partDrawingsReady = true })
  }, [manifest])
  return <p className="page-status">Drawing the parts</p>
}
