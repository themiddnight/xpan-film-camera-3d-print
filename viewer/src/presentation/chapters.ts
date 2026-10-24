import type { CycleKey } from '../types'
import type { Chapter } from './story'

type Step = readonly [t: number, phase: string, values: Readonly<Record<string, number>>]

/**
 * Cycle keys from steps that name only what changes. The player writes every mechanism a cycle
 * touches at every key, so each key carries the earlier values forward.
 */
function steps(...list: readonly Step[]): CycleKey[] {
  let values: Record<string, number> = {}
  return list.map(([t, phase, change]) => {
    values = { ...values, ...change }
    return { t, phase, values }
  })
}

const FINDERS = ['viewfinder_rear_frame', 'viewfinder_front_frame']
const COVER = ['rear_cover', 'pressure_pad', 'slide_holder']

/**
 * The showcase, in page order. Copy uses `{{value:<spec id>}}` for a number with its unit and
 * `{{number:<spec id>}}` for the number alone, so every figure on the page comes from the CAD
 * spec sheet. Shots are directions from the framed parts toward the camera, in camera axes:
 * X along the film travel, Y toward the front, Z up.
 */
export const CHAPTERS: readonly Chapter[] = [
  {
    id: 'hero',
    title: 'X-Pan pinhole camera',
    text: 'A panoramic film camera you print yourself. It sees through a brass pinhole and takes the film sold in any camera shop.',
    shot: { direction: [-0.62, 0.72, 0.36], frame: ['film-back', 'body', 'pinhole'] },
  },
  {
    id: 'format',
    title: 'The format',
    text: 'Panoramic frames on ordinary 135 film. Each frame is {{value:frame_width}} by {{value:frame_height}}, {{number:aspect_ratio}} times as wide as it is tall. The thin outline is a standard frame on the same film.',
    shot: { direction: [0.08, -1, 0.12], frame: ['shell'] },
    scene: { hide: [...COVER, 'dark_slide'] },
    pins: [],
  },
  {
    id: 'modules',
    title: 'Three modules',
    text: 'The film back holds and moves the film. The body sets the distance to it, and the pinhole module screws onto the body’s lens mount. Pick a module to see it on its own.',
    shot: { direction: [1, 0.42, 0.34], frame: ['film-back', 'body', 'pinhole'] },
    scene: { explode: 0.4 },
    pins: ['advance_knob', 'm42_mount', 'shutter_lock'],
  },
  {
    id: 'advance',
    title: 'One turn, one frame',
    text: 'Press the release button and turn the advance knob. The {{number:sprocket_teeth}}-tooth sprocket rides the perforations and locks after one full turn, exactly {{value:advance_per_frame}} of film.',
    shot: { direction: [0.3, -0.75, 0.85], frame: ['sprocket', 'pawl', 'release_button', 'advance_knob', 'takeup_spool', 'cassette'] },
    scene: {
      ghost: ['shell', 'rear_cover', 'pressure_pad', 'dark_slide', 'slide_holder', 'turn_button_left', 'turn_button_right'],
      hide: FINDERS,
    },
    motion: { cycle: 'frame' },
    pins: ['sprocket', 'release_button', 'pawl', 'cam_notch'],
  },
  {
    id: 'loading',
    title: 'Loading film',
    text: 'Turn both cover latches and swing the rear cover open. Drop the cassette in on the left, lead the film across the gate to the take-up spool, then close the cover and turn the latches back.',
    shot: { direction: [0.95, -0.85, 0.75], frame: ['film-back'] },
    motion: {
      keys: steps(
        [0, 'turn the cover latches', { turn_buttons: 0, cover: 0 }],
        [1, 'swing the cover open', { turn_buttons: 1 }],
        [2.6, 'drop the cassette in and lead the film to the spool', { cover: 1 }],
        [4.8, 'close the cover', {}],
        [6.2, 'turn the latches back', { cover: 0 }],
        [7.2, 'loaded', { turn_buttons: 0 }],
        [7.8, 'loaded', {}],
      ),
    },
    pins: ['rear_cover_latch'],
  },
  {
    id: 'dark-slide',
    title: 'Dark slide',
    text: 'The dark slide keeps light off the film whenever the body is off. Pull it out before you shoot and park it on the back of the cover. A velvet light trap seals the slot it runs through.',
    shot: { direction: [0.55, -0.75, 0.75], frame: ['film-back'] },
    motion: {
      keys: steps(
        [0, 'pull the dark slide', { dark_slide: 0, slide_carry: 0, slide_stow: 0 }],
        [2, 'carry it over the cover', { dark_slide: 1 }],
        [3.2, 'slide it into the holder', { slide_carry: 1 }],
        [4.8, 'parked: ready to shoot', { slide_stow: 1 }],
        [5.4, 'parked: ready to shoot', {}],
      ),
    },
    pins: ['dark_slide', 'slot_velvet'],
  },
  {
    id: 'shutter',
    title: 'Pinhole and shutter',
    text: 'Light comes in through a {{value:pinhole_diameter}} hole, {{value:pinhole_distance}} from the film, which works out to f/{{number:f_number}}. Unlock the shutter and slide it open to start the exposure, then slide it shut to end it.',
    shot: { direction: [0.35, 1, 0.3], frame: ['pinhole', 'pinhole_body'] },
    motion: {
      keys: steps(
        [0, 'unlock the shutter', { shutter_lock: 0, shutter: 0 }],
        [0.9, 'slide it open', { shutter_lock: 1 }],
        [2, 'open: the exposure runs', { shutter: 1 }],
        [3, 'open: the exposure runs', {}],
      ),
    },
    pins: ['pinhole', 'shutter_lock', 'shutter_tabs'],
  },
  {
    id: 'viewfinder',
    title: 'Viewfinder',
    text: 'Unfold the front frame, then the rear sight. Put your eye to the sight: what fits inside the front frame is what lands on the film.',
    shot: { direction: [0.55, 1, 0.5], frame: ['viewfinder_front_frame', 'viewfinder_rear_frame', 'm42_rear_cap_ring'] },
    pose: { finder_rear: 1, finder_front: 1 },
    motion: {
      keys: steps(
        [0, 'unfold the front frame', { finder_rear: 1, finder_front: 1 }],
        [1.6, 'unfold the rear sight', { finder_front: 0 }],
        [2.8, 'ready to frame', { finder_rear: 0 }],
        [3.4, 'ready to frame', {}],
      ),
    },
    pins: ['viewfinder_front', 'viewfinder_rear'],
  },
  {
    id: 'swap-body',
    title: 'Swap the body',
    text: 'The body hangs on a hook rail at the top of the film back and clicks onto a latch pin at the bottom. Swing it off and fit another, deeper or with a real lens. The rest of this page shows how to design one.',
    shot: { direction: [-0.85, 0.5, 0.3], frame: ['pinhole_body', 'latch_pin', 'm42_body_cap'] },
    // Cut through the middle and seen from the cut side, the hook rail and the latch pin show in profile.
    scene: { section: { axis: 'x', t: 0.5, flip: true } },
    motion: {
      keys: steps(
        [0, 'swing the body off the latch', { body_detach: 0 }],
        [1.6, 'lift it off the hook rail', { body_detach: 1 }],
        [2.2, 'lift it off the hook rail', {}],
      ),
    },
    pins: ['body_hook_rail', 'body_latch_pin'],
  },
]
