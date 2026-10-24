import { describe, expect, it } from 'vitest'
import { ManifestError, parseManifest } from './manifest'
import { realManifest } from './test/realManifest'

const raw = (): Record<string, unknown> => JSON.parse(JSON.stringify(realManifest()))

describe('parseManifest features and spec sheet', () => {
  it('reads both blocks from the real manifest', () => {
    const m = realManifest()
    expect(m.features.length).toBeGreaterThan(0)
    expect(m.spec_sheet.length).toBeGreaterThan(0)
    expect(m.spec_sheet.some(e => e.unit === '')).toBe(true)
  })

  it('rejects a manifest from before the blocks existed', () => {
    const { features: _features, ...old } = raw()
    expect(() => parseManifest(old)).toThrow(/manifest\.features: expected an array/)
    const { spec_sheet: _specSheet, ...older } = raw()
    expect(() => parseManifest(older)).toThrow(/manifest\.spec_sheet: expected an array/)
  })

  it('rejects a feature on a part that does not exist', () => {
    const m = raw()
    m.features = [{ id: 'x', label: 'X', part: 'no_such_part', point: [0, 0, 0] }]
    expect(() => parseManifest(m)).toThrow(ManifestError)
    expect(() => parseManifest(m)).toThrow(/manifest\.features\[0\]\.part: no part named "no_such_part"/)
  })

  it('rejects duplicate feature ids', () => {
    const m = raw()
    const first = (m.features as Record<string, unknown>[])[0]
    m.features = [first, first]
    expect(() => parseManifest(m)).toThrow(/manifest\.features\[1\]\.id: duplicate id/)
  })

  it('rejects a spec entry with an unknown status', () => {
    const m = raw()
    const first = (m.spec_sheet as Record<string, unknown>[])[0]
    m.spec_sheet = [{ ...first, status: 'final' }]
    expect(() => parseManifest(m)).toThrow(/manifest\.spec_sheet\[0\]\.status: expected one of locked, draft/)
  })

  it('rejects a spec entry whose value is not a number', () => {
    const m = raw()
    const first = (m.spec_sheet as Record<string, unknown>[])[0]
    m.spec_sheet = [{ ...first, value: '65' }]
    expect(() => parseManifest(m)).toThrow(/manifest\.spec_sheet\[0\]\.value: expected a finite number/)
  })
})
