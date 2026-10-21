/** Shape of out/manifest.json, written by cad/export.py. */
export interface PartManifest {
  name: string
  glb: string
  color: string
  volume_mm3: number
  size_mm: [number, number, number]
  /** Camera-plan (x, y) of the vertical axis the part turns about, or null if it does not turn. */
  spin_axis_xy: [number, number] | null
}

export interface Manifest {
  /** GLB files are in metres; multiply by this to get millimetres. */
  glb_unit_scale: number
  film_advance_mm: number
  parts: PartManifest[]
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

export type ViewName = 'iso' | 'front' | 'rear' | 'top'
