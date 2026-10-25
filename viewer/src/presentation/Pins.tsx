import { Fragment, useState, type RefObject } from 'react'
import { createPortal } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { Vector3, type Camera, type Object3D } from 'three'
import { partMode, type Viewer, useViewerState } from '../state/viewer'
import { useLabelPortal } from './StageCanvas'

/**
 * A brass dot with its label beside it. On a phone the dot alone shows, and tapping it opens the label.
 * Styles live in presentation.css.
 */
function Pin({ id, label, compact, side }: { id: string; label: string; compact: boolean; side: 'left' | 'right' }) {
  const [open, setOpen] = useState(false)
  if (!compact) {
    return (
      <div className="pin" data-pin={id} data-side={side} role="img" aria-label={label}>
        <span className="pin-dot" />
        <span className="pin-label">{label}</span>
      </div>
    )
  }
  return (
    <div className="pin" data-pin={id} data-side={side}>
      <button type="button" className="pin-dot pin-tap" aria-label={label} aria-expanded={open} onClick={() => setOpen(!open)} />
      {open && <span className="pin-label" aria-hidden="true">{label}</span>}
    </div>
  )
}

/**
 * Where a label goes in the page: the view projects into its own box, so the box's place on the page
 * is added to reach the label layer over the whole page.
 */
function placeInViewport(track?: RefObject<HTMLElement | null>) {
  const project = new Vector3()
  return (el: Object3D, camera: Camera, size: { width: number; height: number }): [number, number] => {
    el.getWorldPosition(project).project(camera)
    const box = track?.current?.getBoundingClientRect()
    return [
      (project.x * 0.5 + 0.5) * size.width + (box?.left ?? 0),
      (-project.y * 0.5 + 0.5) * size.height + (box?.top ?? 0),
    ]
  }
}

/**
 * Labels on feature points. Each pin hangs under its part's node, at the feature's rest-pose point,
 * so it rides with every mechanism and explode transform. A pin whose part failed to load or is
 * hidden is not drawn. `compact` shows the dot alone, with the label as its accessible name, and a
 * tap opens the label. Labels alternate right and left in the order `ids` names them, so a chapter
 * can keep two close pins from covering each other by listing them one after the other.
 */
export function Pins({ viewer, ids, compact, track }: {
  viewer: Viewer
  ids: readonly string[]
  compact: boolean
  /** The element the view draws into, whose origin the labels are placed from. */
  track?: RefObject<HTMLElement | null>
}) {
  const { manifest, nodes } = viewer
  const portal = useLabelPortal()
  const features = manifest.features.filter(f => ids.includes(f.id))
  // A part's box is reported when its node mounts, so a box means the node is there to hang the pin on.
  const drawn = useViewerState(s => features
    .filter(f => {
      const spec = manifest.parts.find(p => p.name === f.part)
      return s.boxes[f.part] && spec && partMode(s, spec) !== 'hidden'
    })
    .map(f => f.id)
    .join(' '))
  return (
    <>
      {features.map(f => {
        const node = nodes.get(f.part)
        if (!node || !drawn.split(' ').includes(f.id)) return null
        return <Fragment key={f.id}>{createPortal(
          <Html
            position={[...f.point]} zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}
            portal={portal as RefObject<HTMLElement> | undefined}
            calculatePosition={placeInViewport(track)}
          >
            <Pin id={f.id} label={f.label} compact={compact} side={ids.indexOf(f.id) % 2 ? 'left' : 'right'} />
          </Html>,
          node,
        )}</Fragment>
      })}
    </>
  )
}
