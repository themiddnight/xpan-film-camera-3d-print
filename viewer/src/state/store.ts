import { useSyncExternalStore } from 'react'

/** A minimal external store: state is replaced, never mutated, so selectors can compare by identity. */
export interface Store<S> {
  getState: () => S
  update: (fn: (state: S) => S) => void
  subscribe: (listener: () => void) => () => void
}

export function createStore<S>(initial: S): Store<S> {
  let state = initial
  const listeners = new Set<() => void>()
  return {
    getState: () => state,
    update(fn) {
      const next = fn(state)
      if (next === state) return
      state = next
      listeners.forEach(l => l())
    },
    subscribe(listener) {
      listeners.add(listener)
      return () => { listeners.delete(listener) }
    },
  }
}

/** Re-renders only when the selected value changes. The selector must return a stable value for a given state. */
export function useSelector<S, T>(store: Store<S>, selector: (state: S) => T): T {
  return useSyncExternalStore(store.subscribe, () => selector(store.getState()))
}
