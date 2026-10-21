import { useCallback, useEffect, useRef, useState } from 'react'
import type { Box3 } from 'three'
import type { Manifest, PartView, Section, ViewName } from './types'
import { Viewport } from './scene/Viewport'
import { Sidebar } from './ui/Sidebar'
import { sectionPosition } from './scene/frames'
import { ErrorBoundary } from './ErrorBoundary'

const MANIFEST_URL = new URL('manifest.json', document.baseURI).href

declare global {
  interface Window {
    /** Read by verification scripts: loaded part names and world bounds in mm. */
    viewerState?: { parts: string[]; min: number[]; max: number[] }
  }
}

export function App() {
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [views, setViews] = useState<Record<string, PartView>>({})
  const [section, setSection] = useState<Section>({ axis: 'off', t: 0.5, flip: false })
  const [explode, setExplode] = useState(0)
  const [spinning, setSpinning] = useState(false)
  const [failed, setFailed] = useState<ReadonlySet<string>>(new Set())
  const [view, setView] = useState<ViewName>('iso')
  const [viewRequest, setViewRequest] = useState(0)
  const [bounds, setBounds] = useState<Box3 | null>(null)
  const spinAngle = useRef(0)

  useEffect(() => {
    fetch(MANIFEST_URL, { cache: 'no-store' })
      .then(r => {
        if (!r.ok) throw new Error(`Cannot read ${MANIFEST_URL} (${r.status}). Run: uv run python cad/export.py`)
        return r.json() as Promise<Manifest>
      })
      .then(m => {
        setManifest(m)
        setViews(Object.fromEntries(m.parts.map(p => [p.name, { visible: true, ghost: false }])))
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  const onBounds = useCallback((b: Box3) => {
    setBounds(b)
    if (manifest) {
      window.viewerState = { parts: manifest.parts.map(p => p.name), min: b.min.toArray(), max: b.max.toArray() }
    }
  }, [manifest])

  const onPartError = useCallback((name: string, e: Error) => {
    console.error(`Part ${name} failed to load:`, e)
    setFailed(prev => new Set(prev).add(name))
  }, [])

  const showView = useCallback((v: ViewName) => {
    setView(v)
    setViewRequest(n => n + 1)
  }, [])

  if (error) return <div className="message err">{error}</div>
  if (!manifest) return <div className="message">Loading...</div>

  const pos = bounds ? sectionPosition(section, bounds) : null
  const sectionLabel = pos === null ? 'No section' : `${section.axis.toUpperCase()} = ${pos.toFixed(2)}mm`
  const total = manifest.parts.length
  const loaded = total - failed.size
  const hud = failed.size > 0
    ? `${loaded} of ${total} parts loaded. Failed: ${[...failed].join(', ')}`
    : bounds ? `${total} part${total === 1 ? '' : 's'} loaded` : 'Loading parts...'

  return (
    <div className="app">
      <Sidebar
        manifest={manifest}
        views={views}
        onPartView={(name, v) => setViews(prev => ({ ...prev, [name]: v }))}
        section={section}
        sectionLabel={sectionLabel}
        onSection={setSection}
        explode={explode}
        onExplode={setExplode}
        spinning={spinning}
        onSpin={() => setSpinning(s => !s)}
        spinAngle={spinAngle}
        onView={showView}
      />
      <div className="viewport">
        <ErrorBoundary fallback={<div className="message err">The 3D view failed to start. See the browser console.</div>}>
          <Viewport
            manifest={manifest}
            baseUrl={MANIFEST_URL}
            views={views}
            section={section}
            explode={explode}
            spinning={spinning}
            spinAngle={spinAngle}
            view={view}
            viewRequest={viewRequest}
            onBounds={onBounds}
            onPartError={onPartError}
            failed={failed}
          />
        </ErrorBoundary>
        <div className={failed.size > 0 ? 'hud err' : 'hud'}>{hud}</div>
        <div className="axes">X travel · Y front · Z up · grid 10mm</div>
      </div>
    </div>
  )
}
