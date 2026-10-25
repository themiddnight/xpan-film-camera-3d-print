import type { CycleKey, Group, Section, Vec3 } from '../types'

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
  scene?: {
    hide?: readonly string[]
    ghost?: readonly string[]
    explode?: number
    /** The explode follows the scroll through the chapter, from none to full. */
    explodeByScroll?: boolean
    /**
     * Parts that leave the camera as the chapter scrolls: their groups or names, and how far they
     * slide in camera mm at the end. They fade out on the way, since they pass behind the film back.
     */
    remove?: { parts: readonly (string | Group)[]; slide: Vec3 }
    section?: Section
  }
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
