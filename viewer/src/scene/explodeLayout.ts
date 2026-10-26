import type { Group } from '../types'

export type Vec3 = readonly [number, number, number]

/**
 * Where each part sits at full explode, in camera mm (X along the film, Y toward the front, Z up).
 * Modules and the lens mount stack along the optical axis, Y, so they stay coaxial; parts that come
 * off the top or bottom move along Z only. A part not named here moves with its group.
 */
export const GROUP_OFFSET: Record<Group, Vec3> = {
  'film-back': [0, 0, 0],
  body: [0, 70, 0],
  pinhole: [0, 170, 0],
}

const REAR_COVER: Vec3 = [0, -50, 0]
const TOP_CONTROLS: Vec3 = [0, 0, 25]
const FINDER: Vec3 = [0, GROUP_OFFSET.body[1], 25]

export const PART_OFFSET: Readonly<Record<string, Vec3>> = {
  rear_cover: REAR_COVER,
  pressure_pad: REAR_COVER,
  slide_holder: REAR_COVER,
  hinge_pin: REAR_COVER,

  advance_knob: TOP_CONTROLS,
  rewind_knob: TOP_CONTROLS,
  release_button: TOP_CONTROLS,
  turn_button_left: TOP_CONTROLS,
  turn_button_right: TOP_CONTROLS,
  m3_screw_left: TOP_CONTROLS,
  m3_screw_right: TOP_CONTROLS,

  viewfinder_rear_frame: FINDER,
  viewfinder_rear_hinge: FINDER,
  viewfinder_rear_pin_left: FINDER,
  viewfinder_rear_pin_right: FINDER,
  viewfinder_front_frame: FINDER,
  viewfinder_front_hinge: FINDER,
  viewfinder_front_pin_left: FINDER,
  viewfinder_front_pin_right: FINDER,
  tripod_nut: [0, GROUP_OFFSET.body[1], -20],

  m42_shim_ring: [0, 100, 0],
  m42_rear_cap_ring: [0, 125, 0],
  m42_body_cap: [0, 150, 0],
}

/** Parts lifted straight up until they clear the top of `above`, plus this much air. */
export const LIFT_CLEAR: Readonly<Record<string, { above: string; air: number }>> = {
  dark_slide: { above: 'shell', air: 12 },
}
