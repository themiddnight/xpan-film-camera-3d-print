import { useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { KeyPlayer } from '../state/cycle'
import { useViewer, useViewerState, type Viewer } from '../state/viewer'
import type { CycleCounter } from '../types'
import { motionTime } from './scrollMotion'
import type { Staging } from './story'
import type { ChapterScroll } from './useChapterScroll'

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
 * pose. With `scroll`, the active owner's motion follows the scroll through its chapter once the
 * parts are in; without it, the motion moves only when its playback bar says so.
 */
export function Director({ motions, active, scroll }: { motions: ReadonlyMap<string, Motion>; active: string; scroll?: ChapterScroll }) {
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
    if (!player || !ready || !scroll) return
    const follow = () => {
      const at = scroll.get()
      if (at.id !== active) return
      player.seek(motionTime(at.value, player.duration))
      invalidate()
    }
    follow()
    return scroll.subscribe(follow)
  }, [player, ready, scroll, active, invalidate])

  useFrame((_, seconds) => {
    if (!player) return
    player.tick(seconds)
    if (player.getStatus().running) invalidate()
  })
  return null
}
