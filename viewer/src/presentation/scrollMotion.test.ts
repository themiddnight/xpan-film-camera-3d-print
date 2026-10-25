import { describe, expect, it } from 'vitest'
import { motionProgress, motionTime } from './scrollMotion'

describe('scroll to motion time', () => {
  it('holds the first and last pose at the ends of the track', () => {
    expect(motionTime(0, 6)).toBe(0)
    expect(motionTime(0.05, 6)).toBe(0)
    expect(motionTime(0.95, 6)).toBe(6)
    expect(motionTime(1, 6)).toBe(6)
  })

  it('maps time back to the progress that shows it', () => {
    for (const t of [0, 1.3, 3, 6]) expect(motionTime(motionProgress(t, 6), 6)).toBeCloseTo(t, 9)
  })
})
