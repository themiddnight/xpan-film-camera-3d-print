import { useEffect } from 'react'
import { useViewer } from '../state/viewer'
import type { Staging } from './story'
import type { ChapterScroll } from './useChapterScroll'

/** The scroll through a chapter where the unlock has finished and the body starts to leave. */
const LEAVES_FROM = 0.5

const clamp01 = (x: number) => Math.min(1, Math.max(0, x))

/**
 * Carries the staged parts out of the camera as the page scrolls through the second half of the
 * chapter, and puts them back at its start. Illustrative only: no CAD mechanism drives it.
 */
export function ScrollRemove({ scroll, active, staging, fixed }: {
  scroll: ChapterScroll
  active: string
  /** Re-read on every re-staging, since that puts the removal back to its start. */
  staging: Staging
  /** A still shows the chapter at the end of its scroll. */
  fixed?: number
}) {
  const { actions } = useViewer()
  useEffect(() => {
    const follow = () => {
      const at = scroll.get()
      if (at.id === active) actions.setRemoveAmount(fixed ?? clamp01((at.value - LEAVES_FROM) / (1 - LEAVES_FROM)))
    }
    follow()
    const unsubscribe = scroll.subscribe(follow)
    return () => {
      unsubscribe()
      actions.setRemoveAmount(0)
    }
  }, [scroll, active, staging, actions, fixed])
  return null
}
