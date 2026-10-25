import { useEffect, useMemo, useRef, useState, useSyncExternalStore, type ReactNode } from 'react'
import { KeyPlayer } from '../state/cycle'
import { useSelector } from '../state/store'
import { createViewer, type Viewer } from '../state/viewer'
import { MANIFEST_URL } from '../manifest'
import { GROUP_LABELS, GROUPS, type Group, type Manifest } from '../types'
import { Director, motionsFor } from './Director'
import { FilmStripNav, stripVars } from './FilmStripNav'
import { Loading, useLoadingDone } from './Loading'
import { FormatOverlay } from './FormatOverlay'
import { matches, PHONE, REDUCED_MOTION, useMedia } from './media'
import { PlaybackBar } from './PlaybackBar'
import { ScrollExplode } from './ScrollExplode'
import { ScrollRemove } from './ScrollRemove'
import { ScrollTransport } from './scrollMotion'
import { fillCopy } from './spec'
import { StageCanvas } from './StageCanvas'
import { StagedView } from './StagedView'
import type { Chapter, Staging } from './story'
import { chapterRange, useChapterScroll, type ChapterScroll } from './useChapterScroll'

/** Screen heights of scroll per second of motion. */
const SCREENS_PER_SECOND = 0.4
/** Screen heights of scroll through a chapter without motion. */
const STILL_SCREENS = 1
/** The whole turn, in radians, the camera swings through as a chapter without motion scrolls by. */
const ORBIT_RAD = 0.4

declare global {
  interface Window {
    /** Read by browser checks: the stage's viewer, the active chapter and the scroll through it. */
    presentation?: { viewer: Viewer; chapter: string; players: ReadonlyMap<string, KeyPlayer>; scroll: ChapterScroll }
  }
}

/** The loading screen over the page, down to the last part that has loaded or failed. */
function LoadScreen({ viewer }: { viewer: Viewer }) {
  const total = viewer.manifest.parts.length
  const settled = useSelector(viewer.store, s => viewer.manifest.parts.filter(p => s.boxes[p.name] || s.failed.has(p.name)).length)
  const { visible, leaving } = useLoadingDone(total > 0 && settled >= total)
  if (!visible) return null
  return (
    <div className="loading-layer" data-leaving={leaving}>
      <Loading progress={settled / Math.max(1, total)} />
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

/** How tall a chapter's scroll track is, in screen heights: longer motions get more room. */
function trackScreens(motion: KeyPlayer | undefined): number {
  return motion ? Math.max(STILL_SCREENS, motion.duration * SCREENS_PER_SECOND) : STILL_SCREENS
}

/** The page title, kept at the top once the hero has scrolled away, and a way past the showcase. */
function Masthead({ title, showTitle, onSkip }: { title: string; showTitle: boolean; onSkip: () => void }) {
  return (
    <div className="masthead">
      <div className="masthead-bar">
        <p className="masthead-title" data-shown={showTitle} aria-hidden={!showTitle}>{title}</p>
        <button type="button" className="masthead-skip" aria-label="Skip to the build notes" onClick={onSkip}>
          <span className="masthead-skip-long">Skip to the build notes</span>
          <span className="masthead-skip-short" aria-hidden="true">Build notes</span>
        </button>
      </div>
    </div>
  )
}

/**
 * The showcase: one stage behind the page, one pinned layer of chapter cards over it, and a scroll
 * track per chapter laid end to end, so the end of one chapter's scroll is the start of the next and
 * the cards swap in place. Scrolling through a chapter with motion plays its keyframes; through one
 * without, it swings the camera a little. The film-strip navigator runs along the bottom.
 * `figureViews`, the page's other staged views, are drawn into the same canvas, since a page has only one.
 */
export function Showcase({ manifest, chapters, figureViews }: { manifest: Manifest; chapters: readonly Chapter[]; figureViews?: ReactNode }) {
  const viewer = useMemo(() => createViewer(manifest, MANIFEST_URL), [manifest])
  const motions = useMemo(() => motionsFor(viewer, chapters), [viewer, chapters])
  const ids = useMemo(() => chapters.map(c => c.id), [chapters])
  const { active, scroll } = useChapterScroll(ids)
  const progress = useSyncExternalStore(scroll.subscribe, () => Math.round(scroll.get().value * 20) / 20)
  const phone = useMedia(PHONE)
  const reduced = useMedia(REDUCED_MOTION)
  const [explore, setExplore] = useState(false)
  const [highlight, setHighlight] = useState<Group | null>(null)
  const stage = useRef<HTMLDivElement>(null)
  const focus = useRef<HTMLDivElement>(null)
  const cards = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const show = () => cards.current?.style.setProperty('--chapter-progress', String(scroll.get().value))
    show()
    return scroll.subscribe(show)
  }, [scroll])
  // On a phone the card sits under the camera, so the shot is framed above the active card's top edge.
  useEffect(() => {
    const layer = cards.current
    const chapter = layer?.querySelector<HTMLElement>('.chapter[aria-current="step"]')
    if (!phone || !layer || !chapter || !stage.current) return
    // Layout offsets, not the bounding box, which would include the card's entry slide.
    let frame = 0
    const place = () => {
      cancelAnimationFrame(frame)
      // Next frame, so the framing area's own observer does not fire inside this one's loop.
      frame = requestAnimationFrame(() => stage.current?.style.setProperty('--card-reach', `${layer.clientHeight - chapter.offsetTop}px`))
    }
    const observer = new ResizeObserver(place)
    observer.observe(chapter)
    return () => {
      observer.disconnect()
      cancelAnimationFrame(frame)
    }
  }, [phone, active])

  const chapter = chapters.find(c => c.id === active) ?? chapters[0]
  const staging = useMemo(() => highlighted(manifest, chapter, chapter.id === 'modules' ? highlight : null), [manifest, chapter, highlight])
  const transports = useMemo(
    () => new Map([...motions].map(([id, m]) => [id, new ScrollTransport(id, m.player.duration)])),
    [motions],
  )
  useEffect(() => {
    window.presentation = { viewer, chapter: active, players: new Map([...motions].map(([id, m]) => [id, m.player])), scroll }
  }, [viewer, motions, active, scroll])
  useEffect(() => { if (active !== 'modules') setHighlight(null) }, [active])
  useEffect(() => () => transports.forEach(t => t.pause()), [transports, active])

  const turn = useMemo(() => () => {
    const at = scroll.get()
    return reduced || motions.has(at.id) ? 0 : ORBIT_RAD * (at.value - 0.5)
  }, [scroll, reduced, motions])

  const behavior = (): ScrollBehavior => (matches(REDUCED_MOTION) ? 'auto' : 'smooth')
  const scrollTo = (id: string) => {
    const range = chapterRange(id)
    if (range) window.scrollTo({ top: range.top, behavior: behavior() })
  }
  const skip = () => document.getElementById('maker')?.scrollIntoView({ behavior: behavior() })

  const interactive = !phone || explore
  return (
    <section className="showcase" aria-label="The camera" style={stripVars(manifest)}>
      <LoadScreen viewer={viewer} />
      <Masthead title={chapters[0].title} showTitle={active !== chapters[0].id} onSkip={skip} />
      <div className="paper" aria-hidden="true" />
      <StageCanvas>
        <StagedView
          track={stage} focus={focus} viewer={viewer} staging={staging} interactive={interactive} turn={turn}
          frameExplode={chapter.scene?.explodeByScroll ? 1 : undefined}
        >
          <Director motions={motions} active={active} scroll={scroll} />
          {chapter.scene?.explodeByScroll && <ScrollExplode scroll={scroll} active={active} staging={staging} />}
          {chapter.scene?.remove && <ScrollRemove scroll={scroll} active={active} staging={staging} />}
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
        <div ref={cards} className="chapter-cards">
          {chapters.map(c => {
            const motion = motions.get(c.id)
            const transport = transports.get(c.id)
            const isActive = c.id === active
            return (
              <article key={c.id} className={`chapter chapter-${c.id}`} aria-current={isActive ? 'step' : undefined} inert={!isActive}>
                <div className="card">
                  {c.id === 'hero' ? <h1>{c.title}</h1> : <h2>{c.title}</h2>}
                  <p>{fillCopy(manifest, c.text)}</p>
                  {c.id === 'modules' && isActive && <ModulePicker highlight={highlight} onPick={setHighlight} />}
                  {motion && transport && isActive && (
                    <PlaybackBar
                      player={motion.player} transport={transport} counter={motion.counter}
                      label={`${c.title} motion`} hint="Scroll to watch it move, or press play"
                    />
                  )}
                  {isActive && (
                    <div
                      className="card-progress" role="progressbar" aria-label={`Scroll through ${c.title}`}
                      aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress * 100)}
                    >
                      <span className="card-progress-bar" />
                    </div>
                  )}
                </div>
              </article>
            )
          })}
        </div>
        {chapters.map(c => (
          <div key={c.id} className="chapter-track" data-chapter={c.id} style={{ height: `${trackScreens(motions.get(c.id)?.player) * 100}svh` }} />
        ))}
        <div className="chapters-exit" />
      </div>
      <FilmStripNav manifest={manifest} chapters={chapters} active={active} scroll={scroll} onSelect={scrollTo} />
    </section>
  )
}
