import { StrictMode, useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { fetchManifest, MANIFEST_URL } from '../manifest'
import { createViewer, type Viewer } from '../state/viewer'
import type { Manifest } from '../types'
import { StageCanvas } from './StageCanvas'
import { StagedView } from './StagedView'
import type { Chapter, Figure } from './story'
import { validateStory } from './validate'

// Real chapters and figures arrive with the showcase and the maker half. Until then two test views
// prove the shared canvas: the whole camera, and the advance mechanism cut away with its pins.
const CHAPTERS: readonly Chapter[] = []
const FIGURES: readonly Figure[] = [
  { id: 'test-whole', caption: 'Whole camera', shot: { direction: [-0.55, 0.75, 0.45], frame: ['film-back', 'body', 'pinhole'] } },
  {
    id: 'test-advance',
    caption: 'Frame advance',
    shot: { direction: [0.5, -0.7, 0.62], frame: ['sprocket', 'pawl', 'release_button', 'advance_knob', 'takeup_spool'] },
    scene: {
      ghost: ['shell', 'rear_cover', 'pressure_pad', 'dark_slide', 'slide_holder', 'turn_button_left', 'turn_button_right'],
      hide: ['viewfinder_rear_frame', 'viewfinder_front_frame'],
    },
    pins: ['sprocket', 'cam_notch', 'pawl', 'release_button'],
  },
  {
    id: 'test-advance-top',
    caption: 'Frame advance from above',
    shot: { direction: [0.2, -0.3, 1], frame: ['sprocket', 'pawl', 'release_button'] },
    scene: { hide: ['shell', 'rear_cover', 'viewfinder_rear_frame', 'viewfinder_front_frame'] },
    pins: ['sprocket', 'cam_notch', 'pawl', 'release_button'],
  },
]

declare global {
  interface Window {
    /** Read by browser checks while the test views are mounted. */
    presentationTest?: { viewers: readonly Viewer[] }
  }
}

type Load =
  | { status: 'loading' }
  | { status: 'error'; messages: readonly string[] }
  | { status: 'ready'; manifest: Manifest }

const track = { position: 'absolute', top: 0, height: '100vh', width: '50vw' } as const

function TestViews({ manifest }: { manifest: Manifest }) {
  const viewers = useMemo(() => [createViewer(manifest, MANIFEST_URL), createViewer(manifest, MANIFEST_URL)], [manifest])
  const [above, setAbove] = useState(false)
  const left = useRef<HTMLDivElement>(null)
  const right = useRef<HTMLDivElement>(null)
  useEffect(() => { window.presentationTest = { viewers } }, [viewers])
  const frame = viewers[1].cycles.find(c => c.cycle.id === 'frame')
  return (
    <>
      <StageCanvas>
        <StagedView track={left} viewer={viewers[0]} staging={FIGURES[0]} interactive />
        <StagedView track={right} viewer={viewers[1]} staging={FIGURES[above ? 2 : 1]} interactive={false} />
      </StageCanvas>
      <div ref={left} style={{ ...track, left: 0 }} />
      <div ref={right} style={{ ...track, left: '50vw' }} />
      <div style={{ position: 'fixed', right: 16, bottom: 16, display: 'flex', gap: 8 }}>
        <button onClick={() => setAbove(!above)}>Change shot</button>
        <button onClick={() => frame?.run()}>Advance one frame</button>
      </div>
    </>
  )
}

function Presentation() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })

  useEffect(() => {
    let current = true
    fetchManifest().then(
      manifest => {
        const errors = validateStory(manifest, CHAPTERS, FIGURES)
        if (current) setLoad(errors.length > 0 ? { status: 'error', messages: errors } : { status: 'ready', manifest })
      },
      (e: unknown) => { if (current) setLoad({ status: 'error', messages: [e instanceof Error ? e.message : String(e)] }) },
    )
    return () => { current = false }
  }, [])

  switch (load.status) {
    case 'loading': return <p>Loading...</p>
    case 'error': return <ul role="alert">{load.messages.map(m => <li key={m}>{m}</li>)}</ul>
    case 'ready': return <TestViews manifest={load.manifest} />
  }
}

document.body.style.margin = '0'
document.body.style.background = '#D5D8D8'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Presentation />
  </StrictMode>,
)
