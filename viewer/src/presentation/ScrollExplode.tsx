import { useEffect } from 'react'
import { useViewer } from '../state/viewer'
import type { Staging } from './story'
import type { ChapterScroll } from './useChapterScroll'

/** Takes the stage apart from none to full as the page scrolls through the chapter, and back at its start. */
export function ScrollExplode({ scroll, active, staging }: {
  scroll: ChapterScroll
  active: string
  /** Re-read on every re-staging, since that puts the explode back to its start. */
  staging: Staging
}) {
  const { actions } = useViewer()
  useEffect(() => {
    const follow = () => {
      const at = scroll.get()
      if (at.id === active) actions.setExplode(at.value)
    }
    follow()
    const unsubscribe = scroll.subscribe(follow)
    return () => {
      unsubscribe()
      actions.setExplode(0)
    }
  }, [scroll, active, staging, actions])
  return null
}
