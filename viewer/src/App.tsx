import { useEffect, useMemo, useState } from 'react'
import { fetchManifest, MANIFEST_URL } from './manifest'
import type { Manifest } from './types'
import { ErrorBoundary } from './ErrorBoundary'
import { Viewport } from './scene/Viewport'
import { createViewer, ViewerContext, useViewer, useViewerState } from './state/viewer'
import { Sidebar } from './ui/Sidebar'

declare global {
  interface Window {
    /** Read by verification scripts: loaded part names, mechanism ids, world bounds in mm, and part transforms. */
    viewerState?: {
      parts: string[]
      mechanisms: string[]
      min: number[]
      max: number[]
      /** Column-major 4x4 transform of a part from its exported pose (mechanisms and explode applied). */
      partTransform: (name: string) => number[] | null
    }
  }
}

type Load =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; manifest: Manifest }

function Hud() {
  const viewer = useViewer()
  const failed = useViewerState(s => s.failed)
  const bounds = useViewerState(viewer.selectBounds)
  const total = viewer.manifest.parts.length
  const text = failed.size > 0
    ? `${total - failed.size} of ${total} parts loaded. Failed: ${[...failed].join(', ')}`
    : bounds ? `${total} part${total === 1 ? '' : 's'} loaded` : 'Loading parts...'
  return <div className={failed.size > 0 ? 'hud err' : 'hud'}>{text}</div>
}

function Loaded({ manifest }: { manifest: Manifest }) {
  const viewer = useMemo(() => createViewer(manifest, MANIFEST_URL), [manifest])
  return (
    <ViewerContext.Provider value={viewer}>
      <Layout />
    </ViewerContext.Provider>
  )
}

function Layout() {
  const viewer = useViewer()
  const bounds = useViewerState(viewer.selectBounds)

  useEffect(() => {
    if (!bounds) return
    window.viewerState = {
      parts: viewer.manifest.parts.map(p => p.name),
      mechanisms: viewer.manifest.mechanisms.map(m => m.id),
      min: bounds.min.toArray(),
      max: bounds.max.toArray(),
      partTransform: name => viewer.nodes.get(name)?.matrix.toArray() ?? null,
    }
  }, [viewer, bounds])

  return (
    <div className="app">
      <Sidebar />
      <div className="viewport">
        <ErrorBoundary fallback={<div className="message err">The 3D view failed to start. See the browser console.</div>}>
          <Viewport />
        </ErrorBoundary>
        <Hud />
        <div className="axes">X travel · Y front · Z up · grid 10mm</div>
      </div>
    </div>
  )
}

export function App() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })

  useEffect(() => {
    let current = true
    fetchManifest().then(
      manifest => { if (current) setLoad({ status: 'ready', manifest }) },
      (e: unknown) => { if (current) setLoad({ status: 'error', message: e instanceof Error ? e.message : String(e) }) },
    )
    return () => { current = false }
  }, [])

  switch (load.status) {
    case 'loading': return <div className="message">Loading...</div>
    case 'error': return <div className="message err">{load.message}</div>
    case 'ready': return <Loaded manifest={load.manifest} />
  }
}
