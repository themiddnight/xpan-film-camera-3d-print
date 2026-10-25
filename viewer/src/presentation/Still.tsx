import { useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { KeyPlayer } from '../state/cycle'
import { MANIFEST_URL } from '../manifest'
import { createViewer, useViewer, useViewerState } from '../state/viewer'
import type { Manifest } from '../types'
import { motionsFor } from './Director'
import { FormatOverlay } from './FormatOverlay'
import { StageCanvas } from './StageCanvas'
import { ScrollRemove } from './ScrollRemove'
import { ChapterScroll } from './useChapterScroll'
import { StagedView } from './StagedView'
import type { Chapter } from './story'

declare global {
  interface Window {
    /** Set by `?still=<chapter>` once the parts are in and the frame has been drawn. */
    stillReady?: boolean
  }
}

/** Frames drawn after the last change: drei draws a view one frame after it learns the view is on screen. */
const SETTLE_FRAMES = 4

/** A still has no scroll; the removal it stages is fixed. */
const EMPTY_SCROLL = new ChapterScroll('')

/** Plays the chapter's motion to its end, then flags the page once the picture has settled. */
function Finish({ player }: { player: KeyPlayer | null }) {
  const viewer = useViewer()
  const ready = useViewerState(s => viewer.selectBounds(s) !== null)
  const invalidate = useThree(s => s.invalidate)
  const finished = useRef(false)
  const frames = useRef(0)

  useEffect(() => {
    if (!ready || finished.current) return
    finished.current = true
    player?.seek(player.duration)
    invalidate()
  }, [ready, player, invalidate])

  useFrame(() => {
    if (!finished.current) return
    frames.current += 1
    if (frames.current < SETTLE_FRAMES) invalidate()
    else window.stillReady = true
  })
  return null
}

/** Mounted with the parts: its `Html` labels made React log an unmount error when mounted earlier in still mode. */
function OverlayWhenLoaded() {
  const viewer = useViewer()
  const ready = useViewerState(s => viewer.selectBounds(s) !== null)
  return ready ? <FormatOverlay /> : null
}

/** One chapter's staging at the end of its motion on the whole page, with no text or controls, for the stills. */
export function Still({ manifest, chapter }: { manifest: Manifest; chapter: Chapter }) {
  // A still shows the chapter at the end of its scroll, so a scroll-driven explode is at full.
  const staging: Chapter = chapter.scene?.explodeByScroll
    ? { ...chapter, scene: { ...chapter.scene, explode: 1, explodeByScroll: false } }
    : chapter
  const viewer = useMemo(() => createViewer(manifest, MANIFEST_URL), [manifest])
  const player = useMemo(() => motionsFor(viewer, [chapter]).get(chapter.id)?.player ?? null, [viewer, chapter])
  const stage = useRef<HTMLDivElement>(null)
  return (
    <>
      <StageCanvas>
        <StagedView track={stage} viewer={viewer} staging={staging} interactive={false}>
          <Finish player={player} />
          {chapter.scene?.remove && <ScrollRemove scroll={EMPTY_SCROLL} active={chapter.id} staging={staging} fixed={1} />}
          {chapter.id === 'format' && <OverlayWhenLoaded />}
        </StagedView>
      </StageCanvas>
      <div className="paper" aria-hidden="true" />
      <div ref={stage} className="still-stage" />
    </>
  )
}
