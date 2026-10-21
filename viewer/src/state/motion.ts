import { Matrix4 } from 'three'
import { compileDrive, driveMatrix, type CompiledDrive } from '../scene/kinematics'
import type { Mechanism } from '../types'

/** Seconds for one sweep from 0 to 1; one sprocket turn took four seconds before mechanisms existed. */
const SWEEP_SECONDS = 4
/** A long frame (hidden tab) would skip a whole sweep, so time per frame is capped. */
const MAX_FRAME_SECONDS = 0.1

type Direction = 1 | -1

interface PartDrive {
  mechanism: string
  drive: CompiledDrive
}

/**
 * Mechanism values live here, not in React state, so a playing mechanism never re-renders a component.
 * The scene reads `revision` each frame to learn whether any value moved; the sidebar subscribes to one
 * mechanism's value and paints its own slider and readout.
 */
export class Motion {
  readonly mechanisms: readonly Mechanism[]
  /** Increments on every value change. */
  revision = 0
  private readonly values = new Map<string, number>()
  private readonly playing = new Map<string, Direction>()
  private readonly valueListeners = new Map<string, Set<(value: number) => void>>()
  private readonly playingListeners = new Set<() => void>()
  private readonly drivesByPart = new Map<string, PartDrive[]>()
  private readonly scratch = new Matrix4()
  private readonly cyclic = new Set<string>()

  constructor(mechanisms: readonly Mechanism[]) {
    this.mechanisms = mechanisms
    for (const m of mechanisms) {
      this.values.set(m.id, 0)
      this.valueListeners.set(m.id, new Set())
      if (m.cyclic) this.cyclic.add(m.id)
      for (const d of m.drives) {
        const list = this.drivesByPart.get(d.part) ?? []
        list.push({ mechanism: m.id, drive: compileDrive(d) })
        this.drivesByPart.set(d.part, list)
      }
    }
  }

  get(id: string): number {
    return this.values.get(id) ?? 0
  }

  set(id: string, value: number): void {
    const max = this.cyclic.has(id) ? Infinity : 1
    const clamped = Math.min(max, Math.max(0, value))
    if (clamped === this.get(id)) return
    this.values.set(id, clamped)
    this.revision++
    this.valueListeners.get(id)?.forEach(l => l(clamped))
  }

  isPlaying(id: string): boolean {
    return this.playing.has(id)
  }

  setPlaying(id: string, on: boolean): void {
    if (on === this.playing.has(id)) return
    if (on) this.playing.set(id, this.get(id) >= 1 ? -1 : 1)
    else this.playing.delete(id)
    this.playingListeners.forEach(l => l())
  }

  isCyclic(id: string): boolean {
    return this.cyclic.has(id)
  }

  /** Advances every playing mechanism: a cyclic one keeps turning, the others bounce between 0 and 1. */
  tick(seconds: number): void {
    const step = Math.min(seconds, MAX_FRAME_SECONDS) / SWEEP_SECONDS
    for (const [id, direction] of this.playing) {
      if (this.cyclic.has(id)) {
        this.set(id, this.get(id) + step)
        continue
      }
      let value = this.get(id) + direction * step
      let next = direction
      if (value > 1) { value = 2 - value; next = -1 }
      else if (value < 0) { value = -value; next = 1 }
      this.playing.set(id, next)
      this.set(id, value)
    }
  }

  subscribeValue(id: string, listener: (value: number) => void): () => void {
    const set = this.valueListeners.get(id)
    set?.add(listener)
    return () => { set?.delete(listener) }
  }

  subscribePlaying = (listener: () => void): (() => void) => {
    this.playingListeners.add(listener)
    return () => { this.playingListeners.delete(listener) }
  }

  /**
   * Writes the part's transform into `out`. Drives apply in manifest order, each about its own axis in
   * the at-rest pose, so the result is D_n ... D_2 D_1. A part with no drive gets the identity.
   */
  partMatrix(out: Matrix4, part: string): Matrix4 {
    out.identity()
    for (const { mechanism, drive } of this.drivesByPart.get(part) ?? []) {
      out.premultiply(driveMatrix(this.scratch, drive, this.get(mechanism)))
    }
    return out
  }
}
