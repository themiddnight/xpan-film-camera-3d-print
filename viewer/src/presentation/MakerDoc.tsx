import { useEffect, useRef } from 'react'
import { marked } from 'marked'
import { ErrorBoundary } from '../ErrorBoundary'
import type { Manifest, SpecSection } from '../types'
import { BomTable } from './BomTable'
import { DOCS } from './content'
import { DRAWINGS, type Drawing } from './figures'
import type { FigureEntry } from './FigureViews'
import { splitDoc, type Block } from './maker'
import { PlaybackBar, playerTransport } from './PlaybackBar'
import { fillCopy } from './spec'
import { SpecTable } from './SpecTable'

function FigureBox({ entry }: { entry: FigureEntry }) {
  const { figure, motion } = entry
  return (
    <figure className="figure" data-figure={figure.id}>
      <div ref={entry.box} className="figure-box" role="img" aria-label={figure.caption} />
      {motion && (
        <PlaybackBar
          player={motion.player} transport={playerTransport(motion.player)} counter={motion.counter}
          label={`${figure.id} motion`} hint="Press play to watch it move"
        />
      )}
      <figcaption>{figure.caption}</figcaption>
    </figure>
  )
}

/**
 * A page of the anatomy figure in a frame that grows to the page's own height, so it never scrolls
 * inside itself. The page is this repository's own file, served from the same origin.
 */
function DrawingFrame({ drawing }: { drawing: Drawing }) {
  const frame = useRef<HTMLIFrameElement>(null)
  const observer = useRef<ResizeObserver | null>(null)
  useEffect(() => () => observer.current?.disconnect(), [])
  const fit = () => {
    const el = frame.current
    const doc = el?.contentDocument
    if (!el || !doc) return
    // A page's scroll height never falls below its frame's height, so measure it in a frame of height 0.
    const measure = () => {
      el.style.height = '0px'
      el.style.height = `${doc.documentElement.scrollHeight}px`
    }
    measure()
    observer.current?.disconnect()
    observer.current = new ResizeObserver(measure)
    observer.current.observe(doc.body)
  }
  return (
    <figure className="figure" data-drawing={drawing.id}>
      <iframe ref={frame} className="drawing" src={drawing.src} title={drawing.title} loading="lazy" onLoad={fit} />
      <figcaption>{drawing.caption}</figcaption>
    </figure>
  )
}

function BlockView({ block, manifest, entries, webgl }: { block: Block; manifest: Manifest; entries: readonly FigureEntry[]; webgl: boolean }) {
  switch (block.kind) {
    case 'markdown': return <div className="prose" dangerouslySetInnerHTML={{ __html: marked.parse(fillCopy(manifest, block.text), { async: false }) }} />
    case 'figure': {
      const entry = entries.find(e => e.figure.id === block.id)
      return entry && webgl ? <FigureBox entry={entry} /> : null
    }
    case 'drawing': {
      const drawing = DRAWINGS.find(d => d.id === block.id)
      return drawing ? <DrawingFrame drawing={drawing} /> : null
    }
    case 'spec': return <SpecTable manifest={manifest} section={block.section as SpecSection} />
    case 'bom': return (
      <ErrorBoundary fallback={<p role="alert">The bill of materials could not be read from docs/bom.md.</p>} onError={e => console.error(e)}>
        <BomTable />
      </ErrorBoundary>
    )
    case 'unknown': return null
  }
}

/**
 * The maker half: documents in page order on a white drawing sheet, with the 3D figures' boxes where
 * the markdown places them. The canvas sits above the sheet and draws each figure into its box.
 * Without WebGL the boxes are left out and the text reads on its own.
 */
export function MakerDoc({ manifest, entries, webgl }: { manifest: Manifest; entries: readonly FigureEntry[]; webgl: boolean }) {
  return (
    <div className="sheet" id="maker">
      {DOCS.map(doc => {
        const { title, blocks } = splitDoc(doc.markdown)
        return (
          <section key={doc.id} className={`maker maker-${doc.id}`} aria-labelledby={`maker-${doc.id}`}>
            {title && <h2 id={`maker-${doc.id}`}>{title}</h2>}
            <div className="maker-body">
              {blocks.map((block, i) => <BlockView key={i} block={block} manifest={manifest} entries={entries} webgl={webgl} />)}
            </div>
          </section>
        )
      })}
      {import.meta.env.DEV && (
        <section className="maker maker-workshop" aria-labelledby="maker-workshop">
          <h2 id="maker-workshop">Workshop</h2>
          <div className="maker-body">
            <p className="prose"><a href="workshop.html">Open the workshop viewer</a>, the full review tool with every part, section and mechanism. It is not part of the public site.</p>
          </div>
        </section>
      )}
    </div>
  )
}
