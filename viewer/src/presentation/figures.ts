import filmTransportUrl from '../../../docs/figures/film-transport/film-transport-light.html?url'
import type { Figure, Staging } from './story'

/**
 * Every part in the manifest. A figure shows only the parts it names and hides the rest, since each
 * visible part costs draw calls in every view. A part CAD adds is missing here and the test says so,
 * which forces a decision instead of letting it appear in every figure.
 */
export const PART_NAMES: readonly string[] = [
  'shell', 'rear_cover', 'turn_button_left', 'turn_button_right', 'slide_holder', 'dark_slide', 'slot_velvet',
  'pressure_pad', 'hinge_pin', 'latch_pin', 'm3_insert_left', 'm3_insert_right', 'm3_screw_left', 'm3_screw_right',
  'sprocket', 'pawl', 'release_button', 'takeup_spool', 'drive_collar', 'advance_knob', 'rewind_fork', 'rewind_knob',
  'sprocket_pin', 'takeup_shaft', 'rewind_shaft', 'pawl_pin', 'pawl_spring', 'clutch_spring', 'felt_washer',
  'rewind_o_ring', 'pinhole_body', 'm42_shim_ring', 'm42_rear_cap_ring', 'tripod_nut', 'viewfinder_rear_frame',
  'viewfinder_rear_hinge', 'viewfinder_rear_pins', 'viewfinder_front_frame', 'viewfinder_front_hinge',
  'viewfinder_front_pins', 'shutter_housing', 'shutter_open_tab', 'shutter_close_tab', 'shutter_lock',
  'shutter_lock_cap', 'm42_body_cap', 'pinhole_shim', 'shutter_blade', 'shutter_lock_pivot', 'cassette', 'film',
  'film_roll',
]

/**
 * A staging of the named parts alone, solid, plus any `ghost` parts as context. The shot frames the
 * solid ones. Every other part is hidden, so a rename in CAD reports the stale name.
 */
function only(solid: readonly string[], ghost: readonly string[] = []): Pick<Staging, 'scene'> & { frame: readonly string[] } {
  const shown = new Set([...solid, ...ghost])
  return { frame: solid, scene: { ghost, hide: PART_NAMES.filter(name => !shown.has(name)) } }
}

const TRANSPORT = only(
  ['sprocket', 'sprocket_pin', 'pawl', 'pawl_pin', 'pawl_spring', 'release_button', 'takeup_spool', 'takeup_shaft',
    'drive_collar', 'advance_knob', 'clutch_spring', 'felt_washer', 'film', 'film_roll', 'cassette'],
  ['shell'],
)
const RAIL = only(['pinhole_body', 'latch_pin'], ['shell'])
const MOUNT = only(
  ['m42_rear_cap_ring', 'm42_shim_ring', 'm42_body_cap', 'shutter_housing', 'shutter_blade', 'pinhole_shim', 'shutter_lock',
    'shutter_lock_cap', 'shutter_lock_pivot', 'shutter_open_tab', 'shutter_close_tab'],
  ['pinhole_body'],
)

/** The 3D figures of the maker half, by the id its markdown names in `{{figure:<id>}}`. */
export const FIGURES: readonly Figure[] = [
  {
    id: 'transport-cutaway',
    caption: 'The film transport with the back shell ghosted. Press play to turn the advance knob through one frame.',
    shot: { direction: [0.3, -0.75, 0.85], frame: TRANSPORT.frame },
    scene: TRANSPORT.scene,
    motion: { cycle: 'frame' },
    pins: ['sprocket', 'release_button', 'cam_notch', 'pawl'],
  },
  {
    id: 'interface-rail',
    caption: 'The body hung on the film back, cut through the middle. The hook rail holds the top and the latch pin the bottom.',
    shot: { direction: [-0.9, 0.4, 0.3], frame: RAIL.frame },
    scene: { ...RAIL.scene, section: { axis: 'x', t: 0.5, flip: true } },
    pins: ['body_hook_rail', 'body_latch_pin'],
  },
  {
    id: 'interface-m42',
    caption: 'The M42 mount on the front of the body, with the pinhole module drawn away from it.',
    shot: { direction: [0.95, 0.45, 0.28], frame: MOUNT.frame },
    scene: { ...MOUNT.scene, explode: 0.7 },
    pins: ['m42_mount'],
  },
]

/** A page of the existing anatomy figure, embedded as it is. */
export interface Drawing {
  id: string
  title: string
  src: string
  caption: string
}

export const DRAWINGS: readonly Drawing[] = [
  {
    id: 'film-transport',
    title: 'Film transport, isometric drawing',
    src: filmTransportUrl,
    caption: 'The same mechanism drawn in isometric. Click the drawing to advance it one frame.',
  },
]
