import { useEffect, useState } from 'react'

/** The chapter blocks carry `data-chapter="<id>"`. */
export const CHAPTER_ATTRIBUTE = 'data-chapter'

/**
 * The chapter whose block crosses the vertical middle of the screen. The observer's root is shrunk to
 * a line across that middle, so at most one block intersects it at a time; between blocks the last
 * one stays active.
 */
export function useActiveChapter(ids: readonly string[]): string {
  const [active, setActive] = useState(ids[0])
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          const id = entry.target.getAttribute(CHAPTER_ATTRIBUTE)
          if (entry.isIntersecting && id) setActive(id)
        }
      },
      { rootMargin: '-50% 0px -50% 0px', threshold: 0 },
    )
    for (const id of ids) {
      const block = document.querySelector(`[${CHAPTER_ATTRIBUTE}="${id}"]`)
      if (block) observer.observe(block)
    }
    return () => observer.disconnect()
  }, [ids])
  return active
}
