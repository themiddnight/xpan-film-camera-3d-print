import { Fragment } from 'react'
import { createPortal } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { partMode, type Viewer, useViewerState } from '../state/viewer'

const BRASS = '#A4823F'
const DOT_PX = 10

/**
 * Labels on feature points. Each pin hangs under its part's node, at the feature's rest-pose point,
 * so it rides with every mechanism and explode transform. A pin whose part failed to load or is
 * hidden is not drawn. `compact` shows the dot alone, with the label as its accessible name.
 */
export function Pins({ viewer, ids, compact }: { viewer: Viewer; ids: readonly string[]; compact: boolean }) {
  const { manifest, nodes } = viewer
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
          <Html position={[...f.point]} zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}>
            <div data-pin={f.id} role="img" aria-label={f.label} style={{ position: 'relative', whiteSpace: 'nowrap' }}>
              <span style={{
                position: 'absolute', left: -DOT_PX / 2, top: -DOT_PX / 2, width: DOT_PX, height: DOT_PX,
                borderRadius: '50%', background: BRASS, boxShadow: '0 0 0 2px #FFFFFF',
              }} />
              {!compact && (
                <span style={{
                  position: 'absolute', left: DOT_PX, top: -11, padding: '2px 6px', borderRadius: 3,
                  background: '#FFFFFF', color: '#000000', font: '500 13px/18px system-ui, sans-serif',
                }}>{f.label}</span>
              )}
            </div>
          </Html>,
          node,
        )}</Fragment>
      })}
    </>
  )
}
