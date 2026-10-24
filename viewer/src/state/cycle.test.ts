import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { KeyPlayer } from './cycle'
import { Motion } from './motion'

const manifest = realManifest()
const cyclic = manifest.mechanisms.find(m => m.cyclic)!.id
const plain = manifest.mechanisms.find(m => !m.cyclic && !m.internal)!.id

function player() {
  const motion = new Motion(manifest.mechanisms)
  const keys = [
    { t: 0, values: { [cyclic]: 0, [plain]: 0 }, phase: 'start' },
    { t: 1, values: { [cyclic]: 1, [plain]: 1 }, phase: 'end' },
  ]
  return { motion, keys: new KeyPlayer(keys, motion) }
}

describe('KeyPlayer', () => {
  it('holds a paused run and continues it from the same moment', () => {
    const { motion, keys } = player()
    keys.run()
    keys.tick(0.05)
    keys.pauseRun()
    const held = motion.get(plain)
    keys.tick(0.05)
    expect(motion.get(plain)).toBe(held)
    keys.resume()
    keys.tick(0.05)
    expect(keys.time).toBeCloseTo(0.1)
  })

  it('shows the seeked moment and stops playing', () => {
    const { motion, keys } = player()
    keys.run()
    keys.seek(0.5)
    expect(motion.get(plain)).toBeCloseTo(0.5)
    expect(keys.getStatus().running).toBe(false)
  })

  it('stops without writing, and a restart continues a cyclic mechanism from its last whole turn', () => {
    const { motion, keys } = player()
    keys.run()
    for (let i = 0; i < 20; i++) keys.tick(0.1)
    expect(motion.get(cyclic)).toBeCloseTo(1)
    keys.restart()
    keys.tick(0.05)
    keys.stop()
    const left = motion.get(cyclic)
    keys.tick(0.1)
    expect(motion.get(cyclic)).toBe(left)
    expect(left).toBeGreaterThan(1)
    expect(keys.getStatus().running).toBe(false)
  })
})
