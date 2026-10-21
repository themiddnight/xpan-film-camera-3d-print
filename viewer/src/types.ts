/** Shape of out/manifest.json, written by cad/export.py and parsed in manifest.ts. */

/** Rear to front along the camera's Y axis; the order also sets the exploded-view layers. */
export const GROUPS = ['film-back', 'body', 'pinhole'] as const
export type Group = (typeof GROUPS)[number]

export const GROUP_LABELS: Record<Group, string> = {
  'film-back': 'Film back',
  body: 'Body',
  pinhole: 'Pinhole module',
}

export const KINDS = ['printed', 'bought'] as const
export type Kind = (typeof KINDS)[number]

export type Vec3 = readonly [number, number, number]

export interface PartManifest {
  name: string
  glb: string
  group: Group
  kind: Kind
  color: string
  volume_mm3: number
  size_mm: Vec3
}

interface DriveBase {
  /** Name of the part this drive moves. */
  part: string
  /** Direction of the rotation axis or slide, in camera mm coordinates. Never zero-length. */
  axis: Vec3
}

/** Turns `amount` degrees about `axis` through `origin` at mechanism value 1. */
export interface RotateDrive extends DriveBase {
  kind: 'rotate'
  origin: Vec3
  amount: number
}

/** Moves `amount` mm along `axis` at mechanism value 1. */
export interface SlideDrive extends DriveBase {
  kind: 'slide'
  amount: number
}

export type Drive = RotateDrive | SlideDrive

export interface Readout {
  per_unit: number
  unit: string
}

export interface Mechanism {
  id: string
  label: string
  readout: Readout | null
  /**
   * The value keeps counting past 1 (a frame advance turns the knob on, it never runs back), and the
   * slider shows the part within the current turn. Otherwise the value stays in 0 to 1.
   */
  cyclic: boolean
  /** Driven only by cycles (e.g. the pawl riding the cam); no slider, since it only makes sense in sequence. */
  internal: boolean
  /** Applied to each part in this order. */
  drives: readonly Drive[]
}

/** Mechanism values at one moment of a cycle. A cyclic mechanism's value counts from the cycle's start. */
export interface CycleKey {
  /** Seconds from the start of the cycle. */
  t: number
  values: Readonly<Record<string, number>>
  /** What the mechanism is doing from this key to the next, for the readout. */
  phase: string
}

/** Counts something from a cyclic mechanism's value, e.g. perforations and mm of film per frame. */
export interface CycleCounter {
  mechanism: string
  /** Counted items per unit of the mechanism value, e.g. 14 perforations per frame. */
  count_per_unit: number
  count_label: string
  per_unit: number
  unit: string
}

/** A scripted run of several mechanisms together, e.g. one full frame advance. */
export interface Cycle {
  id: string
  label: string
  /** Ascending by t; the first is at 0, the last ends the cycle. */
  keys: readonly CycleKey[]
  counter: CycleCounter
  /** Parts to ghost or hide while showing the cycle, so the moving parts are in view. */
  focus: { ghost: readonly string[]; hide: readonly string[] }
}

/**
 * The film strip as a path, so the viewer can draw it moving: the perforations travel along the
 * centre line as the advance mechanism turns. It replaces the static GLB of `part`.
 */
export interface FilmStrip {
  part: string
  mechanism: string
  /** Film travel in mm per unit of the mechanism value. */
  advance_per_unit: number
  /** Arc length of the first point; points are spaced `ds` apart along the centre line, in XY. */
  s0: number
  ds: number
  points: readonly (readonly [number, number])[]
  width: number
  pitch: number
  perf_along: number
  perf_across: number
  /** Perforation rows sit at Z = +/- this. */
  perf_row_z: number
  /** Arc length of one perforation centre at rest. */
  first_perf_s: number
}

export interface Manifest {
  /** GLB files are in metres; multiply by this to get millimetres. */
  glb_unit_scale: number
  film_advance_mm: number
  parts: readonly PartManifest[]
  mechanisms: readonly Mechanism[]
  cycles: readonly Cycle[]
  film_strip: FilmStrip | null
}

/** World coordinates are camera-design coordinates in mm: X film travel, Y front, Z up. */
export type Axis = 'x' | 'y' | 'z'

export interface PartView {
  visible: boolean
  ghost: boolean
}

export interface Section {
  axis: Axis | 'off'
  /** Position across the scene bounds on that axis, 0 to 1. */
  t: number
  flip: boolean
}

/** `mechanism` frames only the parts a cycle moves, from the rear right, like the anatomy figure. */
export type ViewName = 'iso' | 'front' | 'rear' | 'top' | 'mechanism'

export type KindFilter = 'all' | Kind
