import { useMemo, type RefObject } from 'react'
import { createViewer, type Viewer } from '../state/viewer'
import { MANIFEST_URL } from '../manifest'
import type { Manifest } from '../types'
import { Director, motionsFor, type Motion } from './Director'
import { PHONE, useMedia } from './media'
import { StagedView } from './StagedView'
import type { Figure } from './story'

/** One figure with its own viewer, so its mechanisms move apart from every other view. */
export interface FigureEntry {
  figure: Figure
  viewer: Viewer
  motion: Motion | null
  /** The document box the view draws into; it keeps a fixed aspect ratio so drei never needs a resize. */
  box: RefObject<HTMLDivElement | null>
}

export function useFigureEntries(manifest: Manifest, figures: readonly Figure[]): FigureEntry[] {
  return useMemo(() => figures.map(figure => {
    const viewer = createViewer(manifest, MANIFEST_URL)
    return { figure, viewer, motion: motionsFor(viewer, [figure]).get(figure.id) ?? null, box: { current: null } }
  }), [manifest, figures])
}

function FigureView({ entry }: { entry: FigureEntry }) {
  const phone = useMedia(PHONE)
  const motions = useMemo(() => new Map(entry.motion ? [[entry.figure.id, entry.motion]] : []), [entry])
  return (
    <StagedView track={entry.box} viewer={entry.viewer} staging={entry.figure} interactive={!phone}>
      <Director motions={motions} active={entry.figure.id} />
    </StagedView>
  )
}

/** Draws every figure into the page's canvas. Render it inside `StageCanvas`. */
export function FigureViews({ entries }: { entries: readonly FigureEntry[] }) {
  return <>{entries.map(entry => <FigureView key={entry.figure.id} entry={entry} />)}</>
}
