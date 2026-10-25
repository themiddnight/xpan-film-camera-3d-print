import { useEffect, useRef, type CSSProperties } from 'react'
import type { FilmStrip, Manifest } from '../types'
import type { Chapter } from './story'
import type { ChapterScroll } from './useChapterScroll'

interface FrameGeometry {
  /** Film advance per frame, frame width and height, in mm. */
  pitch: number
  width: number
  height: number
  film: FilmStrip | null
}

/**
 * The navigator's proportions as CSS custom properties, each a multiple of the frame height: film
 * advance per frame, film width and frame width. The showcase sets them so its layout can leave room
 * for the strip.
 */
export function stripVars(manifest: Manifest): CSSProperties {
  const g = geometry(manifest)
  return {
    '--strip-pitch': g.pitch / g.height,
    '--strip-film': (g.film?.width ?? g.height) / g.height,
    '--strip-frame-w': g.width / g.height,
  } as CSSProperties
}

function geometry(manifest: Manifest): FrameGeometry {
  const value = (id: string) => {
    const entry = manifest.spec_sheet.find(s => s.id === id)
    if (!entry) throw new Error(`the navigator needs spec "${id}"`)
    return entry.value
  }
  return { pitch: value('advance_per_frame'), width: value('frame_width'), height: value('frame_height'), film: manifest.film_strip }
}

/**
 * One frame's length of film, drawn in mm: the perforations of the real strip, both rows, every
 * pitch, and the frame between them. The holes show the seamless behind the navigator.
 */
function FilmTile({ g, exposed = true }: { g: FrameGeometry; exposed?: boolean }) {
  const film = g.film
  const filmWidth = film?.width ?? g.height
  const mid = filmWidth / 2
  const perfs: { x: number; y: number }[] = []
  if (film) {
    const count = Math.round(g.pitch / film.pitch)
    for (let i = 0; i < count; i++) {
      for (const row of [-film.perf_row_z, film.perf_row_z]) perfs.push({ x: (i + 0.5) * film.pitch, y: mid + row })
    }
  }
  return (
    <svg className="strip-film" viewBox={`0 0 ${g.pitch} ${filmWidth}`} preserveAspectRatio="none" aria-hidden="true">
      {film && perfs.map(p => (
        <rect
          key={`${p.x} ${p.y}`} className="strip-perf"
          x={p.x - film.perf_along / 2} y={p.y - film.perf_across / 2}
          width={film.perf_along} height={film.perf_across} rx={film.perf_along / 4}
        />
      ))}
      {exposed && <rect className="strip-frame" x={(g.pitch - g.width) / 2} y={mid - g.height / 2} width={g.width} height={g.height} />}
    </svg>
  )
}

/** Unexposed film either side of the chapters, so the strip runs past both screen edges. */
const LEADER_TILES = 10

function leader(g: FrameGeometry, end: 'head' | 'tail') {
  return Array.from({ length: LEADER_TILES }, (_, i) => (
    <li key={`${end}${i}`} className="strip-leader" aria-hidden="true">
      <span className="strip-edge" />
      <FilmTile g={g} exposed={false} />
    </li>
  ))
}

/**
 * The film-strip navigator: a black-and-white negative with one frame per chapter and frame numbers
 * printed along its edge. The current chapter's frame advances into the gate at the centre of the
 * screen, with a bar under the gate for how far through the chapter the page has scrolled; choosing a
 * frame scrolls to the start of its chapter.
 */
export function FilmStripNav({ manifest, chapters, active, scroll, onSelect }: {
  manifest: Manifest
  chapters: readonly Chapter[]
  active: string
  scroll: ChapterScroll
  onSelect: (id: string) => void
}) {
  const nav = useRef<HTMLElement>(null)
  useEffect(() => {
    const show = () => nav.current?.style.setProperty('--chapter-progress', String(scroll.get().value))
    show()
    return scroll.subscribe(show)
  }, [scroll])
  const g = geometry(manifest)
  const index = Math.max(0, chapters.findIndex(c => c.id === active))
  const style = { '--strip-i': index, '--strip-leader': LEADER_TILES } as CSSProperties
  return (
    <nav ref={nav} className="strip" aria-label="Chapters" style={style}>
      <ol className="strip-run">
        {leader(g, 'head')}
        {chapters.map((c, i) => (
          <li key={c.id}>
            <button
              type="button" className="strip-tile" aria-current={c.id === active ? 'step' : undefined}
              onClick={() => onSelect(c.id)}
            >
              <span className="strip-edge" aria-hidden="true">
                <span>{i + 1}</span>
                <span>▸{i + 1}A</span>
              </span>
              <FilmTile g={g} />
              <span className="strip-title">{c.title}</span>
            </button>
          </li>
        ))}
        {leader(g, 'tail')}
      </ol>
      <span className="strip-gate" aria-hidden="true" />
      <span className="strip-progress" aria-hidden="true"><span className="strip-progress-bar" /></span>
    </nav>
  )
}
