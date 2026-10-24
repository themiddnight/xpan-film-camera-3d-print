import { useSyncExternalStore } from 'react'

export const REDUCED_MOTION = '(prefers-reduced-motion: reduce)'
export const PHONE = '(max-width: 640px), (pointer: coarse)'

export function matches(query: string): boolean {
  return window.matchMedia(query).matches
}

/** Follows a media query, so a resize or a system setting change re-renders the caller. */
export function useMedia(query: string): boolean {
  return useSyncExternalStore(
    listener => {
      const list = window.matchMedia(query)
      list.addEventListener('change', listener)
      return () => list.removeEventListener('change', listener)
    },
    () => matches(query),
  )
}
