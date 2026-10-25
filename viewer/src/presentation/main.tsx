import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/archivo/wdth.css'
import './presentation.css'
import { fetchManifest } from '../manifest'
import type { Manifest } from '../types'
import { CHAPTERS } from './chapters'
import { Showcase } from './Showcase'
import { DOCS } from './content'
import { DRAWINGS, FIGURES } from './figures'
import { FigureViews, useFigureEntries } from './FigureViews'
import { MakerDoc } from './MakerDoc'
import { hasWebGL, NoWebGL } from './NoWebGL'
import { Still } from './Still'
import { validateDocs, validateStory } from './validate'

type Load =
  | { status: 'loading' }
  | { status: 'error'; messages: readonly string[] }
  | { status: 'ready'; manifest: Manifest }

/** The showcase over the maker half, with every figure drawn into the showcase's one canvas. */
function Page({ manifest }: { manifest: Manifest }) {
  const entries = useFigureEntries(manifest, FIGURES)
  const still = new URLSearchParams(location.search).get('still')
  const chapter = CHAPTERS.find(c => c.id === still)
  if (chapter) return <Still manifest={manifest} chapter={chapter} />
  if (!hasWebGL()) {
    return (
      <>
        <NoWebGL manifest={manifest} chapters={CHAPTERS} />
        <MakerDoc manifest={manifest} entries={entries} webgl={false} />
      </>
    )
  }
  return (
    <>
      <Showcase manifest={manifest} chapters={CHAPTERS} figureViews={<FigureViews entries={entries} />} />
      <MakerDoc manifest={manifest} entries={entries} webgl />
    </>
  )
}

function Presentation() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })

  useEffect(() => {
    let current = true
    fetchManifest().then(
      manifest => {
        const errors = [...validateStory(manifest, CHAPTERS, FIGURES), ...validateDocs(manifest, DOCS, FIGURES, DRAWINGS)]
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
    case 'ready': return <Page manifest={load.manifest} />
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Presentation />
  </StrictMode>,
)
