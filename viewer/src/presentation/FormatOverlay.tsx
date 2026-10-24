import { useMemo } from 'react'
import { Html, Line } from '@react-three/drei'
import { DoubleSide } from 'three'
import { useViewer } from '../state/viewer'
import { spec } from './spec'

/**
 * The standard 135 frame is 36 mm wide. It is a film standard this camera does not use, so CAD does
 * not publish it; move it to the spec sheet if CAD ever does.
 */
const STANDARD_FRAME_WIDTH_MM = 36
/** Sits this far behind the film as the rear shot sees it, so the film never hides the frame. */
const FILM_CLEARANCE_MM = 0.6
/** Rings of fading light around the frame read as a glow without a post-processing pass. */
const HALO = [{ grow: 1.6, opacity: 0.22 }, { grow: 3.4, opacity: 0.1 }]

/**
 * A lit frame where the exposure lands on the film, sized from the spec sheet and centred on the gate
 * (camera X and Z are zero at the gate centre), with the standard frame outlined inside it.
 */
export function FormatOverlay() {
  const { manifest } = useViewer()
  const gate = manifest.features.find(f => f.id === 'film_gate')
  const size = useMemo(() => {
    const value = (id: string) => manifest.spec_sheet.find(s => s.id === id)?.value ?? 0
    return { w: value('frame_width'), h: value('frame_height') }
  }, [manifest])
  if (!gate || size.w === 0 || size.h === 0) return null
  const [x, gateY] = gate.point
  const y = gateY - FILM_CLEARANCE_MM
  const { w, h } = size
  const sw = STANDARD_FRAME_WIDTH_MM
  const outline: [number, number, number][] = [
    [x - sw / 2, y - 0.01, -h / 2], [x + sw / 2, y - 0.01, -h / 2], [x + sw / 2, y - 0.01, h / 2],
    [x - sw / 2, y - 0.01, h / 2], [x - sw / 2, y - 0.01, -h / 2],
  ]
  return (
    <group>
      {HALO.map(({ grow, opacity }) => (
        <mesh key={grow} position={[x, y + 0.01, 0]} rotation={[Math.PI / 2, 0, 0]} renderOrder={1}>
          <planeGeometry args={[w + grow * 2, h + grow * 2]} />
          <meshBasicMaterial color="#F6E7C1" transparent opacity={opacity} side={DoubleSide} depthWrite={false} toneMapped={false} />
        </mesh>
      ))}
      <mesh position={[x, y, 0]} rotation={[Math.PI / 2, 0, 0]} renderOrder={2}>
        <planeGeometry args={[w, h]} />
        <meshBasicMaterial color="#FBF3DE" side={DoubleSide} toneMapped={false} />
      </mesh>
      <Line points={outline} color="#000000" lineWidth={1.5} renderOrder={3} />
      <Html position={[x - w / 2, y, h / 2]} zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}>
        <span className="overlay-label overlay-label-above">
          This camera, {spec(manifest, 'frame_width', false)} × {spec(manifest, 'frame_height')}
        </span>
      </Html>
      <Html position={[x - sw / 2, y, -h / 2]} zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}>
        <span className="overlay-label overlay-label-below">Standard frame</span>
      </Html>
    </group>
  )
}
