import { describe, expect, it } from 'vitest'
import { realManifest } from '../test/realManifest'
import { CHAPTERS } from './chapters'
import { DOCS } from './content'
import { DRAWINGS, FIGURES } from './figures'
import type { Chapter, Figure } from './story'
import { validateDocs, validateStory } from './validate'

const manifest = realManifest()
const part = manifest.parts[0].name
const mechanism = manifest.mechanisms[0].id
const cycle = manifest.cycles[0].id
const feature = manifest.features[0].id

const fixture: Chapter = {
  id: 'fixture',
  title: 'Fixture',
  text: 'A chapter that names one of each kind of reference.',
  shot: { direction: [1, -1, 1], frame: [part, 'film-back'] },
  scene: { hide: [part], ghost: [part] },
  pose: { [mechanism]: 1 },
  motion: { cycle },
  pins: [feature],
}

const errorsFor = (changes: Partial<Chapter>) => validateStory(manifest, [{ ...fixture, ...changes }], [])

describe('validateStory', () => {
  it('accepts a chapter whose references all exist in the real manifest', () => {
    expect(validateStory(manifest, [fixture], [])).toEqual([])
  })

  it('accepts the real chapters and figures against the real manifest', () => {
    expect(validateStory(manifest, CHAPTERS, FIGURES)).toEqual([])
  })

  it('names a figure that hides a part CAD no longer has', () => {
    const [first, ...rest] = FIGURES
    const stale = { ...first, scene: { ...first.scene, hide: [...(first.scene?.hide ?? []), 'no_such_part'] } }
    expect(validateStory(manifest, [], [stale, ...rest])).toEqual([`figure ${first.id}: unknown part "no_such_part"`])
  })

  it('names a spec value the copy asks for that the spec sheet lacks', () => {
    expect(errorsFor({ text: 'Frames of {{value:no_such_spec}}.' })).toEqual(['chapter fixture: unknown spec "no_such_spec"'])
  })

  it('names the chapter and the feature that no longer exists', () => {
    expect(errorsFor({ pins: [feature, 'no_such_feature'] })).toEqual(['chapter fixture: unknown feature "no_such_feature"'])
  })

  it('names an unknown part in the shot frame', () => {
    expect(errorsFor({ shot: { direction: [1, 0, 0], frame: ['no_such_part'] } })).toEqual(['chapter fixture: unknown part "no_such_part"'])
  })

  it('names an unknown part to hide or ghost', () => {
    expect(errorsFor({ scene: { hide: ['gone_a'], ghost: ['gone_b'] } })).toEqual([
      'chapter fixture: unknown part "gone_a"',
      'chapter fixture: unknown part "gone_b"',
    ])
  })

  it('names an unknown mechanism in the pose', () => {
    expect(errorsFor({ pose: { no_such_mechanism: 1 } })).toEqual(['chapter fixture: unknown mechanism "no_such_mechanism"'])
  })

  it('names an unknown cycle in the motion', () => {
    expect(errorsFor({ motion: { cycle: 'no_such_cycle' } })).toEqual(['chapter fixture: unknown cycle "no_such_cycle"'])
  })

  it('names an unknown mechanism inside inline motion keys', () => {
    const keys = [
      { t: 0, values: { [mechanism]: 0 }, phase: 'rest' },
      { t: 1, values: { no_such_mechanism: 1 }, phase: 'move' },
    ]
    expect(errorsFor({ motion: { keys } })).toEqual(['chapter fixture: unknown mechanism "no_such_mechanism"'])
  })

  it('reports every problem, and a figure is named as a figure', () => {
    const figure: Figure = { id: 'fig', caption: 'A figure', shot: fixture.shot, pins: ['no_such_feature'] }
    const errors = validateStory(manifest, [{ ...fixture, pose: { no_such_mechanism: 1 } }], [figure])
    expect(errors).toEqual([
      'chapter fixture: unknown mechanism "no_such_mechanism"',
      'figure fig: unknown feature "no_such_feature"',
    ])
  })

  it('rejects two chapters with one id', () => {
    expect(validateStory(manifest, [fixture, fixture], [])).toEqual(['chapter fixture: duplicate id "fixture"'])
  })
})

describe('validateDocs', () => {
  const docs = (markdown: string) => [{ id: 'doc', markdown }]
  const check = (markdown: string) => validateDocs(manifest, docs(markdown), FIGURES, DRAWINGS)

  it('accepts the real documents against the real manifest, figures and drawings', () => {
    expect(validateDocs(manifest, DOCS, FIGURES, DRAWINGS)).toEqual([])
  })

  it('accepts every kind of placeholder when it names something real', () => {
    const figure = FIGURES[0].id
    const value = manifest.spec_sheet[0].id
    expect(check(`## Doc\n\n{{figure:${figure}}}\n\n{{drawing:${DRAWINGS[0].id}}}\n\n{{spec:specs}}\n\n{{spec:interface}}\n\n{{bom}}\n\nA {{value:${value}}} and {{number:${value}}}.`)).toEqual([])
  })

  it('names an unknown figure', () => {
    expect(check('{{figure:no_such_figure}}')).toEqual(['document doc: unknown figure "no_such_figure"'])
  })

  it('names an unknown drawing', () => {
    expect(check('{{drawing:no_such_drawing}}')).toEqual(['document doc: unknown drawing "no_such_drawing"'])
  })

  it('names an unknown spec table', () => {
    expect(check('{{spec:no_such_section}}')).toEqual(['document doc: unknown spec table "no_such_section"'])
  })

  it('names an unknown spec value in prose', () => {
    expect(check('Frames of {{value:no_such_spec}} and {{number:no_such_number}}.')).toEqual([
      'document doc: unknown spec "no_such_spec"',
      'document doc: unknown spec "no_such_number"',
    ])
  })

  it('names a placeholder nothing handles, in prose or on its own line', () => {
    expect(check('A {{figure:inline}} in a sentence.\n\n{{table:specs}}\n\n{{figure}}')).toEqual([
      'document doc: unknown placeholder "{{figure:inline}}"',
      'document doc: unknown placeholder "{{table:specs}}"',
      'document doc: unknown placeholder "{{figure}}"',
    ])
  })
})
