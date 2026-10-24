import type { Cycle, CycleKey } from '../types'
import type { Motion } from './motion'

/** Rest between looped cycles, so each lock reads before the next press. */
const LOOP_PAUSE_SECONDS = 1.2
const MAX_FRAME_SECONDS = 0.1

export interface CycleStatus {
  running: boolean
  looping: boolean
  phase: string
  /** Completed cycles since the page opened. */
  done: number
}

/** Eases each segment in and out, so parts start and stop gently instead of at constant speed. */
function smooth(x: number): number {
  return x * x * (3 - 2 * x)
}

function segment(keys: readonly CycleKey[], t: number): { from: CycleKey; to: CycleKey; f: number } {
  let i = 0
  while (i < keys.length - 2 && t >= keys[i + 1].t) i++
  const from = keys[i]
  const to = keys[i + 1]
  return { from, to, f: smooth(Math.min(1, Math.max(0, (t - from.t) / (to.t - from.t)))) }
}

/**
 * Plays scripted keys by writing mechanism values. A cyclic mechanism (the frame advance) is written
 * as the value it had when the run started plus the key's value, so every run continues from the
 * last instead of running back.
 */
export class KeyPlayer {
  readonly keys: readonly CycleKey[]
  private readonly motion: Motion
  private elapsed = 0
  private pause = 0
  private base: Map<string, number> | null = null
  private status: CycleStatus
  private readonly listeners = new Set<() => void>()

  constructor(keys: readonly CycleKey[], motion: Motion) {
    this.keys = keys
    this.motion = motion
    this.status = { running: false, looping: false, phase: keys[0].phase, done: 0 }
  }

  get duration(): number {
    return this.keys[this.keys.length - 1].t
  }

  /** Seconds into the current run. */
  get time(): number {
    return this.elapsed
  }

  getStatus = (): CycleStatus => this.status

  /** How far a mechanism has moved in this run: 1 after a whole frame advance. 0 before any run. */
  progress(id: string): number {
    return this.base ? this.motion.get(id) - (this.base.get(id) ?? 0) : 0
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => { this.listeners.delete(listener) }
  }

  /** Starts one run from the beginning unless one is already running. */
  run(): void {
    if (this.status.running) return
    this.elapsed = 0
    this.pause = 0
    this.takeBase()
    this.update({ running: true })
  }

  /** Runs again from the beginning, whatever it was doing. */
  restart(): void {
    this.update({ running: false })
    this.run()
  }

  /** Continues a paused run from where it stopped; starts over when it had finished. */
  resume(): void {
    if (this.status.running) return
    if (!this.base || this.elapsed >= this.duration) return this.run()
    this.update({ running: true })
  }

  pauseRun(): void {
    if (this.status.running) this.update({ running: false })
  }

  /** Shows the moment `t` seconds in and holds there. */
  seek(t: number): void {
    if (!this.base) this.takeBase()
    this.elapsed = Math.min(this.duration, Math.max(0, t))
    this.apply(this.elapsed)
    if (this.status.running) this.update({ running: false })
  }

  /** Stops without writing any value, so whoever stops it decides the pose. */
  stop(): void {
    this.elapsed = 0
    this.base = null
    this.update({ running: false, looping: false, phase: this.keys[0].phase })
  }

  setLooping(looping: boolean): void {
    this.update({ looping })
    if (looping) this.run()
  }

  tick(seconds: number): void {
    const dt = Math.min(seconds, MAX_FRAME_SECONDS)
    if (!this.status.running) {
      if (!this.status.looping) return
      this.pause += dt
      if (this.pause >= LOOP_PAUSE_SECONDS) this.run()
      return
    }
    this.elapsed = Math.min(this.duration, this.elapsed + dt)
    this.apply(this.elapsed)
    if (this.elapsed >= this.duration) {
      const last = this.keys[this.keys.length - 1]
      this.update({ running: false, done: this.status.done + 1, phase: last.phase })
    }
  }

  private takeBase(): void {
    this.base = new Map()
    for (const id of this.mechanismIds()) {
      // A frame advance starts from the last whole frame, so a run after manual slider moves stays aligned.
      this.base.set(id, this.motion.isCyclic(id) ? Math.floor(this.motion.get(id) + 1e-9) : 0)
    }
  }

  private apply(t: number): void {
    const { from, to, f } = segment(this.keys, t)
    for (const id of this.mechanismIds()) {
      const a = from.values[id] ?? 0
      const b = to.values[id] ?? 0
      this.motion.set(id, (this.base?.get(id) ?? 0) + a + (b - a) * f)
    }
    if (from.phase !== this.status.phase) this.update({ phase: from.phase })
  }

  private mechanismIds(): Set<string> {
    const ids = new Set<string>()
    for (const k of this.keys) for (const id of Object.keys(k.values)) ids.add(id)
    return ids
  }

  private update(patch: Partial<CycleStatus>): void {
    this.status = { ...this.status, ...patch }
    this.listeners.forEach(l => l())
  }
}

/** A manifest cycle with its player. */
export class CyclePlayer extends KeyPlayer {
  readonly cycle: Cycle

  constructor(cycle: Cycle, motion: Motion) {
    super(cycle.keys, motion)
    this.cycle = cycle
  }
}
