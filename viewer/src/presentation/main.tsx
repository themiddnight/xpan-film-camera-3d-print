import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { fetchManifest } from '../manifest'
import type { Chapter, Figure } from './story'
import { validateStory } from './validate'

// Real chapters and figures arrive with the showcase and the maker half.
const CHAPTERS: readonly Chapter[] = []
const FIGURES: readonly Figure[] = []

type Load =
  | { status: 'loading' }
  | { status: 'error'; messages: readonly string[] }
  | { status: 'ready' }

function Placeholder() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })

  useEffect(() => {
    let current = true
    fetchManifest().then(
      manifest => {
        const errors = validateStory(manifest, CHAPTERS, FIGURES)
        if (current) setLoad(errors.length > 0 ? { status: 'error', messages: errors } : { status: 'ready' })
      },
      (e: unknown) => { if (current) setLoad({ status: 'error', messages: [e instanceof Error ? e.message : String(e)] }) },
    )
    return () => { current = false }
  }, [])

  switch (load.status) {
    case 'loading': return <p>Loading...</p>
    case 'error': return <ul role="alert">{load.messages.map(m => <li key={m}>{m}</li>)}</ul>
    case 'ready': return <p>Presentation coming.</p>
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Placeholder />
  </StrictMode>,
)
