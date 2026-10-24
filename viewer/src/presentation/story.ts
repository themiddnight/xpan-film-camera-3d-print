import type { CycleKey, Group, Section } from '../types'

/** Camera direction from the framed centre toward the camera, in camera mm axes. */
export type ShotDirection = readonly [number, number, number]

/** What a chapter or a figure shows: where the camera looks, what is drawn, how mechanisms sit and move. */
export interface Staging {
  shot: {
    direction: ShotDirection
    /** Part names or groups the shot frames. */
    frame: readonly (string | Group)[]
    /** Overrides the distance fitted from the framed bounds. */
    distance?: number
  }
  scene?: { hide?: readonly string[]; ghost?: readonly string[]; explode?: number; section?: Section }
  /** Mechanism values on entry, by mechanism id. */
  pose?: Readonly<Record<string, number>>
  /** A manifest cycle by id, or inline keys played by the cycle player. */
  motion?: { cycle: string } | { keys: readonly CycleKey[] }
  /** Feature ids to pin. */
  pins?: readonly string[]
}

export interface Chapter extends Staging {
  id: string
  title: string
  text: string
}

export interface Figure extends Staging {
  id: string
  caption: string
}
