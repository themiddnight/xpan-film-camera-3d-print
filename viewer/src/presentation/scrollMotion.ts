import { chapterRange } from './useChapterScroll'

/** Share of a chapter's track at each end that holds the first or last pose, so a motion settles before the card leaves. */
const HOLD = 0.08
const MAX_STEP_SECONDS = 0.1
/** Input that means the visitor took the scroll back from a playing chapter. */
const TAKEOVER_EVENTS = ['wheel', 'touchstart', 'keydown', 'pointerdown'] as const

const clamp01 = (x: number) => Math.min(1, Math.max(0, x))

/** Seconds into a motion for scroll progress through its chapter. */
export function motionTime(progress: number, duration: number): number {
  return duration * clamp01((progress - HOLD) / (1 - 2 * HOLD))
}

/** Scroll progress through a chapter that shows the motion `time` seconds in. */
export function motionProgress(time: number, duration: number): number {
  return HOLD + clamp01(time / duration) * (1 - 2 * HOLD)
}

/** What the playback bar drives: play, pause, replay and seek. */
export interface Transport {
  subscribe: (listener: () => void) => () => void
  isPlaying: () => boolean
  play: () => void
  pause: () => void
  replay: () => void
  seek: (time: number) => void
}

/**
 * Plays a chapter's motion by scrolling the page through its track, so the picture, the scroll
 * position and the film strip always agree. Any scroll input from the visitor pauses it.
 */
export class ScrollTransport implements Transport {
  private playing = false
  private time = 0
  private last = 0
  private frame = 0
  private readonly listeners = new Set<() => void>()

  constructor(private readonly id: string, private readonly duration: number) {}

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => { this.listeners.delete(listener) }
  }

  isPlaying = (): boolean => this.playing

  play = (): void => {
    if (this.playing) return
    const range = chapterRange(this.id)
    if (!range) return
    this.time = motionTime((window.scrollY - range.top) / range.length, this.duration)
    if (this.time >= this.duration) this.time = 0
    this.scrollTo(this.time)
    this.last = performance.now()
    for (const type of TAKEOVER_EVENTS) window.addEventListener(type, this.takeover, { capture: true, passive: true })
    this.setPlaying(true)
    this.frame = requestAnimationFrame(this.step)
  }

  pause = (): void => {
    if (!this.playing) return
    cancelAnimationFrame(this.frame)
    for (const type of TAKEOVER_EVENTS) window.removeEventListener(type, this.takeover, { capture: true })
    this.setPlaying(false)
  }

  replay = (): void => {
    this.pause()
    this.scrollTo(0)
    this.play()
  }

  seek = (time: number): void => {
    this.pause()
    this.scrollTo(time)
  }

  private step = (now: number): void => {
    this.time = Math.min(this.duration, this.time + Math.min(MAX_STEP_SECONDS, (now - this.last) / 1000))
    this.last = now
    this.scrollTo(this.time)
    if (this.time >= this.duration) this.pause()
    else this.frame = requestAnimationFrame(this.step)
  }

  private takeover = (e: Event): void => {
    // The bar's own buttons and slider stay in charge.
    if (e.target instanceof Element && e.target.closest('.playback')) return
    this.pause()
  }

  private scrollTo(time: number): void {
    const range = chapterRange(this.id)
    if (range) window.scrollTo({ top: range.top + range.length * motionProgress(time, this.duration), behavior: 'instant' })
  }

  private setPlaying(playing: boolean): void {
    this.playing = playing
    this.listeners.forEach(l => l())
  }
}
