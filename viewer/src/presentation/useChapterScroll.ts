import { useEffect, useMemo, useState } from 'react'

/** The chapter tracks carry `data-chapter="<id>"`. */
export const CHAPTER_ATTRIBUTE = 'data-chapter'

export interface ChapterProgress {
  id: string
  /** 0 when the chapter's track reaches the top of the screen, 1 when its end does. */
  value: number
}

/** Scroll progress through the chapter under the middle of the screen, read without re-rendering. */
export class ChapterScroll {
  private at: ChapterProgress
  private readonly listeners = new Set<() => void>()

  constructor(id: string) {
    this.at = { id, value: 0 }
  }

  get = (): ChapterProgress => this.at

  set(at: ChapterProgress): void {
    if (at.id === this.at.id && at.value === this.at.value) return
    this.at = at
    this.listeners.forEach(l => l())
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => { this.listeners.delete(listener) }
  }
}

export function chapterElement(id: string): HTMLElement | null {
  return document.querySelector<HTMLElement>(`[${CHAPTER_ATTRIBUTE}="${id}"]`)
}

/** Where a chapter's track starts on the page and how far it scrolls. */
export function chapterRange(id: string): { top: number; length: number } | null {
  const el = chapterElement(id)
  if (!el) return null
  return { top: el.getBoundingClientRect().top + window.scrollY, length: Math.max(1, el.offsetHeight) }
}

/**
 * The chapter whose track is at the top of the screen, as React state, and the progress through it as
 * a `ChapterScroll`. Past the last track the last chapter stays active, at its end.
 */
export function useChapterScroll(ids: readonly string[]): { active: string; scroll: ChapterScroll } {
  const [active, setActive] = useState(ids[0])
  const scroll = useMemo(() => new ChapterScroll(ids[0]), [ids])
  useEffect(() => {
    const read = () => {
      for (const id of ids) {
        const rect = chapterElement(id)?.getBoundingClientRect()
        if (!rect || rect.top > 0 || rect.bottom <= 0) continue
        setActive(id)
        scroll.set({ id, value: rect.height > 0 ? Math.min(1, -rect.top / rect.height) : 0 })
        return
      }
      const last = ids[ids.length - 1]
      const rect = chapterElement(last)?.getBoundingClientRect()
      if (rect && rect.bottom <= 0) {
        setActive(last)
        scroll.set({ id: last, value: 1 })
      }
    }
    read()
    window.addEventListener('scroll', read, { passive: true })
    window.addEventListener('resize', read)
    return () => {
      window.removeEventListener('scroll', read)
      window.removeEventListener('resize', read)
    }
  }, [ids, scroll])
  return { active, scroll }
}
