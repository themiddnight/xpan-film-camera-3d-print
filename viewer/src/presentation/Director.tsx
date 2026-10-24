import { useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { KeyPlayer } from '../state/cycle'
import { useViewer, useViewerState, type Viewer } from '../state/viewer'
import type { CycleCounter } from '../types'
import type { Staging } from './story'

/** Autoplay waits for the camera to arrive, as ShotRig eases over this long. */
const SETTLE_MS = 800

export interface Motion {
  player: KeyPlayer
  counter: CycleCounter | null
}

/** One player per owner with motion, all writing into that viewer's mechanisms. */
export function motionsFor(viewer: Viewer, owners: readonly { id: string; motion?: Staging['motion'] }[]): Map<string, Motion> {
  const motions = new Map<string, Motion>()
  for (const { id, motion } of owners) {
    if (!motion) continue
    if ('cycle' in motion) {
      const cycle = viewer.manifest.cycles.find(k => k.id === motion.cycle)
      if (cycle) motions.set(id, { player: new KeyPlayer(cycle.keys, viewer.motion), counter: cycle.counter })
    } else {
      motions.set(id, { player: new KeyPlayer(motion.keys, viewer.motion), counter: null })
    }
  }
  return motions
}

/**
 * Runs inside a staged view, after the active staging is applied in the same commit. On a change of
 * `active` it stops every motion, so nothing an earlier owner started keeps writing over the new
 * pose; with `autoplay`, once the parts are in and the camera has arrived it plays the new owner's
 * motion once.
 */
export function Director({ motions, active, autoplay }: { motions: ReadonlyMap<string, Motion>; active: string; autoplay: boolean }) {
  const viewer = useViewer()
  const invalidate = useThree(s => s.invalidate)
  const ready = useViewerState(s => viewer.selectBounds(s) !== null)
  const player = motions.get(active)?.player ?? null

  useEffect(() => {
    for (const m of motions.values()) m.player.stop()
    if (!player) return
    return player.subscribe(invalidate)
  }, [motions, player, invalidate])

  useEffect(() => {
    if (!player || !ready || !autoplay) return
    const timer = setTimeout(() => player.run(), SETTLE_MS)
    return () => clearTimeout(timer)
  }, [player, ready, autoplay])

  useFrame((_, seconds) => {
    if (!player) return
    player.tick(seconds)
    if (player.getStatus().running) invalidate()
  })
  return null
}
