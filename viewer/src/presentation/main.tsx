import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/archivo/wdth.css'
import './presentation.css'
import { fetchManifest } from '../manifest'
import type { Manifest } from '../types'
import { CHAPTERS } from './chapters'
import { Showcase } from './Showcase'
import type { Figure } from './story'
import { validateStory } from './validate'

// Figures arrive with the maker half.
const FIGURES: readonly Figure[] = []

type Load =
  | { status: 'loading' }
  | { status: 'error'; messages: readonly string[] }
  | { status: 'ready'; manifest: Manifest }

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
    case 'loading': return <p className="page-status">Loading the camera</p>
    case 'error': return (
      <div className="page-status" role="alert">
        <p>The page could not be built from the CAD export:</p>
        <ul>{load.messages.map(m => <li key={m}>{m}</li>)}</ul>
      </div>
    )
    case 'ready': return <Showcase manifest={load.manifest} chapters={CHAPTERS} />
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Presentation />
  </StrictMode>,
)
