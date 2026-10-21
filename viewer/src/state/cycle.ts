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
 * Plays a scripted cycle by writing mechanism values. A cyclic mechanism (the frame advance) is written
 * as the value it had when the cycle started plus the key's value, so every cycle continues from the
 * last instead of running back.
 */
export class CyclePlayer {
  readonly cycle: Cycle
  private readonly motion: Motion
  private time = 0
  private pause = 0
  private base = new Map<string, number>()
  private status: CycleStatus
  private readonly listeners = new Set<() => void>()

  constructor(cycle: Cycle, motion: Motion) {
    this.cycle = cycle
    this.motion = motion
    this.status = { running: false, looping: false, phase: cycle.keys[0].phase, done: 0 }
  }

  get duration(): number {
    return this.cycle.keys[this.cycle.keys.length - 1].t
  }

  getStatus = (): CycleStatus => this.status

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => { this.listeners.delete(listener) }
  }

  /** Starts one cycle unless one is already running. */
  run(): void {
    if (this.status.running) return
    this.time = 0
    this.pause = 0
    this.base = new Map()
    for (const id of this.mechanismIds()) {
      // A frame advance starts from the last whole frame, so a cycle after manual slider moves stays aligned.
      this.base.set(id, this.motion.isCyclic(id) ? Math.floor(this.motion.get(id) + 1e-9) : 0)
    }
    this.update({ running: true })
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
    this.time = Math.min(this.duration, this.time + dt)
    this.apply(this.time)
    if (this.time >= this.duration) {
      const last = this.cycle.keys[this.cycle.keys.length - 1]
      this.update({ running: false, done: this.status.done + 1, phase: last.phase })
    }
  }

  private apply(t: number): void {
    const { from, to, f } = segment(this.cycle.keys, t)
    for (const id of this.mechanismIds()) {
      const a = from.values[id] ?? 0
      const b = to.values[id] ?? 0
      this.motion.set(id, (this.base.get(id) ?? 0) + a + (b - a) * f)
    }
    if (from.phase !== this.status.phase) this.update({ phase: from.phase })
  }

  private mechanismIds(): Set<string> {
    const ids = new Set<string>()
    for (const k of this.cycle.keys) for (const id of Object.keys(k.values)) ids.add(id)
    return ids
  }

  private update(patch: Partial<CycleStatus>): void {
    this.status = { ...this.status, ...patch }
    this.listeners.forEach(l => l())
  }
}
