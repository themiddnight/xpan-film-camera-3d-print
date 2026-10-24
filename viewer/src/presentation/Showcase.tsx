import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { KeyPlayer } from '../state/cycle'
import { useSelector } from '../state/store'
import { createViewer, type Viewer } from '../state/viewer'
import { MANIFEST_URL } from '../manifest'
import { GROUP_LABELS, GROUPS, type Group, type Manifest } from '../types'
import { Director, motionsFor } from './Director'
import { FilmStripNav, stripVars } from './FilmStripNav'
import { FormatOverlay } from './FormatOverlay'
import { matches, PHONE, REDUCED_MOTION, useMedia } from './media'
import { PlaybackBar } from './PlaybackBar'
import { fillCopy } from './spec'
import { StageCanvas } from './StageCanvas'
import { StagedView } from './StagedView'
import type { Chapter, Staging } from './story'
import { CHAPTER_ATTRIBUTE, useActiveChapter } from './useActiveChapter'

declare global {
  interface Window {
    /** Read by browser checks: the stage's viewer and the active chapter. */
    presentation?: { viewer: Viewer; chapter: string; players: ReadonlyMap<string, KeyPlayer> }
  }
}

function LoadProgress({ viewer }: { viewer: Viewer }) {
  const total = viewer.manifest.parts.length
  const settled = useSelector(viewer.store, s => viewer.manifest.parts.filter(p => s.boxes[p.name] || s.failed.has(p.name)).length)
  if (settled >= total) return null
  return (
    <div className="load" role="progressbar" aria-label="Loading the camera" aria-valuemin={0} aria-valuemax={total} aria-valuenow={settled}>
      <span className="load-track"><span className="load-bar" style={{ transform: `scaleX(${settled / total})` }} /></span>
      <span className="load-text">Loading the camera, {settled} of {total} parts</span>
    </div>
  )
}

function ModulePicker({ highlight, onPick }: { highlight: Group | null; onPick: (g: Group | null) => void }) {
  return (
    <div className="modules" role="group" aria-label="Show one module">
      {GROUPS.map(g => (
        <button key={g} type="button" className="module" aria-pressed={highlight === g} onClick={() => onPick(highlight === g ? null : g)}>
          {GROUP_LABELS[g]}
        </button>
      ))}
    </div>
  )
}

/** The chapter's staging, with every module but the highlighted one ghosted. The shot stays the same object, so the camera holds still. */
function highlighted(manifest: Manifest, chapter: Chapter, group: Group | null): Staging {
  if (!group) return chapter
  const others = manifest.parts.filter(p => p.group !== group).map(p => p.name)
  return { ...chapter, scene: { ...chapter.scene, ghost: [...(chapter.scene?.ghost ?? []), ...others] } }
}

/**
 * The showcase: one stage behind the page, restaged as each chapter's text crosses the middle of the
 * screen, with the film-strip navigator along the bottom. `figureViews`, the page's other staged
 * views, are drawn into the same canvas, since a page has only one.
 */
export function Showcase({ manifest, chapters, figureViews }: { manifest: Manifest; chapters: readonly Chapter[]; figureViews?: ReactNode }) {
  const viewer = useMemo(() => createViewer(manifest, MANIFEST_URL), [manifest])
  const motions = useMemo(() => motionsFor(viewer, chapters), [viewer, chapters])
  const ids = useMemo(() => chapters.map(c => c.id), [chapters])
  const active = useActiveChapter(ids)
  const phone = useMedia(PHONE)
  const reduced = useMedia(REDUCED_MOTION)
  const [explore, setExplore] = useState(false)
  const [highlight, setHighlight] = useState<Group | null>(null)
  const stage = useRef<HTMLDivElement>(null)
  const focus = useRef<HTMLDivElement>(null)

  const chapter = chapters.find(c => c.id === active) ?? chapters[0]
  const staging = useMemo(() => highlighted(manifest, chapter, chapter.id === 'modules' ? highlight : null), [manifest, chapter, highlight])
  useEffect(() => {
    window.presentation = { viewer, chapter: active, players: new Map([...motions].map(([id, m]) => [id, m.player])) }
  }, [viewer, motions, active])
  useEffect(() => { if (active !== 'modules') setHighlight(null) }, [active])

  const scrollTo = (id: string) => {
    document.querySelector(`[${CHAPTER_ATTRIBUTE}="${id}"]`)?.scrollIntoView({ behavior: matches(REDUCED_MOTION) ? 'auto' : 'smooth', block: 'center' })
  }

  const interactive = !phone || explore
  return (
    <section className="showcase" aria-label="The camera" style={stripVars(manifest)}>
      <StageCanvas>
        <StagedView track={stage} focus={focus} viewer={viewer} staging={staging} interactive={interactive} spin={active === 'hero' && !reduced}>
          <Director motions={motions} active={active} autoplay={!reduced} />
          {active === 'format' && <FormatOverlay />}
        </StagedView>
        {figureViews}
      </StageCanvas>
      <div ref={stage} className="stage" data-explore={interactive}>
        <div ref={focus} className="stage-focus" />
        {phone && (
          <button type="button" className="explore" aria-pressed={explore} onClick={() => setExplore(!explore)}>
            Explore
          </button>
        )}
      </div>
      <div className="chapters">
        {chapters.map(c => {
          const motion = motions.get(c.id)
          const isActive = c.id === active
          return (
            <article key={c.id} className={`chapter chapter-${c.id}`} data-chapter={c.id} aria-current={isActive ? 'step' : undefined}>
              <div className="card">
                {c.id === 'hero' ? <h1>{c.title}</h1> : <h2>{c.title}</h2>}
                <p>{fillCopy(manifest, c.text)}</p>
                {c.id === 'hero' && <LoadProgress viewer={viewer} />}
                {c.id === 'modules' && isActive && <ModulePicker highlight={highlight} onPick={setHighlight} />}
                {motion && isActive && <PlaybackBar player={motion.player} counter={motion.counter} label={`${c.title} motion`} />}
              </div>
            </article>
          )
        })}
      </div>
      <FilmStripNav manifest={manifest} chapters={chapters} active={active} onSelect={scrollTo} />
    </section>
  )
}
