import { useEffect, useMemo } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Matrix4, Vector3 } from 'three'
import { useViewer, useViewerState, type ViewerState } from '../state/viewer'
import { writeSectionPlane } from './frames'
import { explodeOffset, explodeVectors } from './explode'

interface Applied {
  revision: number
  explode: number
  remove: number
  nodes: number
  boxes: ViewerState['boxes'] | null
  vectors: Map<string, Vector3>
}

/**
 * The one place part transforms are written. Each frame it advances playing mechanisms, and when a
 * mechanism value, the explode amount, a part box or the set of nodes changed, it recomputes every
 * part's matrix: explode offset after the part's drives. Idle frames do no work.
 *
 * Under `frameloop="demand"` it also asks for the frames motion needs: one when a cycle starts, a
 * mechanism starts playing or the viewer state changes, and the next one while anything still moves.
 */
export function MotionDriver() {
  const viewer = useViewer()
  const invalidate = useThree(s => s.invalidate)
  useEffect(() => {
    const unsubscribe = [
      viewer.store.subscribe(invalidate),
      viewer.motion.subscribePlaying(invalidate),
      ...viewer.cycles.map(c => c.subscribe(invalidate)),
    ]
    invalidate()
    return () => unsubscribe.forEach(u => u())
  }, [viewer, invalidate])
  const scratch = useMemo(() => ({ matrix: new Matrix4(), offset: new Vector3(), leaving: new Vector3() }), [])
  const applied = useMemo((): Applied => ({ revision: -1, explode: -1, remove: -1, nodes: -1, boxes: null, vectors: new Map() }), [])

  useFrame((_, seconds) => {
    const { motion, nodes, store, manifest, cycles } = viewer
    for (const cycle of cycles) cycle.tick(seconds)
    motion.tick(seconds)
    const moving = cycles.some(c => c.getStatus().running || c.getStatus().looping) ||
      motion.mechanisms.some(m => motion.isPlaying(m.id))
    if (moving) invalidate()
    const { explode, boxes, remove } = store.getState()
    const removeAmount = remove?.amount ?? 0
    if (
      applied.revision === motion.revision && applied.explode === explode && applied.remove === removeAmount &&
      applied.nodes === nodes.version && applied.boxes === boxes
    ) return

    if (applied.boxes !== boxes) applied.vectors = explodeVectors(manifest.parts, boxes)
    applied.revision = motion.revision
    applied.explode = explode
    applied.remove = removeAmount
    applied.nodes = nodes.version
    applied.boxes = boxes

    for (const part of manifest.parts) {
      const node = nodes.get(part.name)
      if (!node) continue
      motion.partMatrix(scratch.matrix, part.name)
      explodeOffset(scratch.offset, applied.vectors.get(part.name), explode)
      if (remove && removeAmount > 0 && remove.parts.includes(part.name)) {
        scratch.offset.addScaledVector(scratch.leaving.set(...remove.slide), removeAmount)
      }
      // A translation applied after the drives only adds to the matrix's translation column.
      const e = scratch.matrix.elements
      scratch.matrix.setPosition(e[12] + scratch.offset.x, e[13] + scratch.offset.y, e[14] + scratch.offset.z)
      scratch.matrix.decompose(node.position, node.quaternion, node.scale)
    }
  })

  return null
}

/** Keeps the shared clip plane at the section position as the slider or the bounds change. */
export function ClipSync() {
  const viewer = useViewer()
  const section = useViewerState(s => s.section)
  const bounds = useViewerState(viewer.selectBounds)
  useEffect(() => {
    if (bounds) writeSectionPlane(viewer.clipPlane, section, bounds)
  }, [viewer.clipPlane, section, bounds])
  return null
}
