import type { Manifest } from '../types'
import { fillCopy } from './spec'
import type { Chapter } from './story'

/** Whether this browser can create a WebGL context at all. */
export function hasWebGL(): boolean {
  const canvas = document.createElement('canvas')
  return Boolean(canvas.getContext('webgl2') ?? canvas.getContext('webgl'))
}

/**
 * The showcase for a browser without WebGL: each chapter's text beside the still that
 * `pnpm stills` made of it.
 */
export function NoWebGL({ manifest, chapters }: { manifest: Manifest; chapters: readonly Chapter[] }) {
  return (
    <section className="still-fallback" aria-label="The camera">
      <p className="still-note" role="status">
        This browser cannot draw the 3D model, so each chapter shows a picture of it.
      </p>
      {chapters.map(c => (
        <article key={c.id} className={`fallback-chapter chapter-${c.id}`} data-chapter={c.id}>
          {c.id === 'hero' ? <h1>{c.title}</h1> : <h2>{c.title}</h2>}
          <p>{fillCopy(manifest, c.text)}</p>
          <img src={`stills/${c.id}.png`} alt={`${c.title}, shown on the camera`} width={1600} height={900} loading="lazy" />
        </article>
      ))}
    </section>
  )
}
