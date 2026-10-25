import { createContext, useContext } from 'react'
import { Box3, Plane } from 'three'
import { PartNodes } from '../scene/partNodes'
import {
  type Cycle, type Group, type KindFilter, type Manifest, type PartManifest, type PartView, type Section, type Vec3,
  type ViewName,
} from '../types'
import { CyclePlayer } from './cycle'
import { Motion } from './motion'
import { createStore, useSelector, type Store } from './store'

export interface ViewerState {
  parts: Readonly<Record<string, PartView>>
  groups: Readonly<Record<Group, PartView>>
  filter: KindFilter
  section: Section
  explode: number
  view: ViewName
  /** Increments to move the camera to `view` again even when it has not changed. */
  viewRequest: number
  /** Rest-pose world box of each loaded part. */
  boxes: Readonly<Record<string, Box3>>
  failed: ReadonlySet<string>
  /** Parts the `mechanism` view frames: those the focused cycle moves. */
  framed: readonly string[]
  /** The cycle shown in its cutaway, with the part views it changed, so turning it off restores them. */
  focus: { cycle: string; saved: Readonly<Record<string, PartView>> } | null
  /**
   * Parts leaving the camera in an illustrative shot (the presentation's body swap), how far they
   * slide at the end, and how far along they are. Not a mechanism: the CAD has no such motion.
   */
  remove: { parts: readonly string[]; slide: Vec3; amount: number } | null
}

/** What a part shows right now, after its own toggles, its group's toggles and the kind filter. */
export type PartMode = 'solid' | 'ghost' | 'hidden'

export function partMode(s: ViewerState, part: PartManifest): PartMode {
  const own = s.parts[part.name]
  const group = s.groups[part.group]
  if (!own.visible || !group.visible || (s.filter !== 'all' && s.filter !== part.kind)) return 'hidden'
  return own.ghost || group.ghost ? 'ghost' : 'solid'
}

export interface Viewer {
  manifest: Manifest
  /** Where the manifest was fetched from; part GLB paths resolve against it. */
  baseUrl: string
  store: Store<ViewerState>
  /** Mechanism values, outside React state because they change every frame. */
  motion: Motion
  /** One player per scripted cycle in the manifest, writing into `motion`. */
  cycles: readonly CyclePlayer[]
  nodes: PartNodes
  /** The one section plane every part clips against; the section controls move it in place. */
  clipPlane: Plane
  /** Union of all part boxes once every part has loaded or failed; null until then. */
  selectBounds: (s: ViewerState) => Box3 | null
  /** True when a section is on and its bounds are known. */
  selectClipActive: (s: ViewerState) => boolean
  actions: {
    setPartView: (name: string, patch: Partial<PartView>) => void
    setGroupView: (group: Group, patch: Partial<PartView>) => void
    setFilter: (filter: KindFilter) => void
    setSection: (section: Section) => void
    setExplode: (amount: number) => void
    setRemoveAmount: (amount: number) => void
    showView: (view: ViewName) => void
    reportBox: (name: string, box: Box3 | null) => void
    /** Marks a part that will not appear; whoever caught the failure has already logged it. */
    reportFailed: (name: string) => void
    /** Ghosts and hides the cycle's focus parts, or shows them again. */
    setFocus: (cycle: CyclePlayer, on: boolean) => void
  }
}

const SHOWN: PartView = { visible: true, ghost: false }

function boundsSelector(parts: readonly PartManifest[]): (s: ViewerState) => Box3 | null {
  let lastBoxes: ViewerState['boxes'] | null = null
  let lastFailed: ViewerState['failed'] | null = null
  let last: Box3 | null = null
  return s => {
    if (s.boxes === lastBoxes && s.failed === lastFailed) return last
    lastBoxes = s.boxes
    lastFailed = s.failed
    // A part that failed to load counts as settled, so the rest still frame and report.
    if (!parts.every(p => s.boxes[p.name] || s.failed.has(p.name))) return (last = null)
    const all = new Box3()
    for (const p of parts) if (s.boxes[p.name]) all.union(s.boxes[p.name])
    return (last = all)
  }
}

/** Every part a cycle moves, through the mechanisms its keys set. */
function cycleParts(manifest: Manifest, cycle: Cycle): string[] {
  const moving = new Set(cycle.keys.flatMap(k => Object.keys(k.values)))
  return manifest.mechanisms.filter(m => moving.has(m.id)).flatMap(m => m.drives.map(d => d.part))
}

export function createViewer(manifest: Manifest, baseUrl: string): Viewer {
  const store = createStore<ViewerState>({
    parts: Object.fromEntries(manifest.parts.map(p => [p.name, SHOWN])),
    groups: { 'film-back': SHOWN, body: SHOWN, pinhole: SHOWN },
    filter: 'all',
    section: { axis: 'off', t: 0.5, flip: false },
    explode: 0,
    view: 'iso',
    viewRequest: 0,
    boxes: {},
    failed: new Set(),
    framed: manifest.cycles.length > 0 ? cycleParts(manifest, manifest.cycles[0]) : [],
    focus: null,
    remove: null,
  })
  const selectBounds = boundsSelector(manifest.parts)
  const motion = new Motion(manifest.mechanisms)

  return {
    manifest,
    baseUrl,
    store,
    motion,
    cycles: manifest.cycles.map(c => new CyclePlayer(c, motion)),
    nodes: new PartNodes(),
    clipPlane: new Plane(),
    selectBounds,
    selectClipActive: s => s.section.axis !== 'off' && selectBounds(s) !== null,
    actions: {
      setPartView: (name, patch) => store.update(s => ({ ...s, parts: { ...s.parts, [name]: { ...s.parts[name], ...patch } } })),
      setGroupView: (group, patch) => store.update(s => ({ ...s, groups: { ...s.groups, [group]: { ...s.groups[group], ...patch } } })),
      setFilter: filter => store.update(s => (s.filter === filter ? s : { ...s, filter })),
      setSection: section => store.update(s => ({ ...s, section })),
      setExplode: explode => store.update(s => (s.explode === explode ? s : { ...s, explode })),
      setRemoveAmount: amount => store.update(s => (s.remove && s.remove.amount !== amount
        ? { ...s, remove: { ...s.remove, amount } }
        : s)),
      showView: view => store.update(s => ({ ...s, view, viewRequest: s.viewRequest + 1 })),
      reportBox: (name, box) => store.update(s => {
        if (box === null) {
          if (!(name in s.boxes)) return s
          const { [name]: _removed, ...rest } = s.boxes
          return { ...s, boxes: rest }
        }
        return s.boxes[name]?.equals(box) ? s : { ...s, boxes: { ...s.boxes, [name]: box } }
      }),
      setFocus: (player, on) => store.update(s => {
        const { ghost, hide } = player.cycle.focus
        if (!on) {
          if (!s.focus) return s
          return { ...s, parts: { ...s.parts, ...s.focus.saved }, focus: null, view: 'iso', viewRequest: s.viewRequest + 1 }
        }
        const base = s.focus ? { ...s.parts, ...s.focus.saved } : s.parts
        const saved = Object.fromEntries([...ghost, ...hide].map(name => [name, base[name]]))
        const parts = { ...base }
        for (const name of ghost) parts[name] = { visible: true, ghost: true }
        for (const name of hide) parts[name] = { visible: false, ghost: false }
        return {
          ...s, parts, focus: { cycle: player.cycle.id, saved },
          framed: cycleParts(manifest, player.cycle), view: 'mechanism', viewRequest: s.viewRequest + 1,
        }
      }),
      reportFailed: name => store.update(s => (s.failed.has(name) ? s : { ...s, failed: new Set(s.failed).add(name) })),
    },
  }
}

export const ViewerContext = createContext<Viewer | null>(null)

export function useViewer(): Viewer {
  const viewer = useContext(ViewerContext)
  if (!viewer) throw new Error('useViewer needs a ViewerContext.Provider above it')
  return viewer
}

/** Subscribes to one slice of viewer state; the selector must return a stable value for a given state. */
export function useViewerState<T>(selector: (s: ViewerState) => T): T {
  return useSelector(useViewer().store, selector)
}
