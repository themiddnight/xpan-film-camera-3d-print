import { sectionPosition } from '../../scene/frames'
import { useViewer, useViewerState } from '../../state/viewer'
import type { Section } from '../../types'

const SLIDER_STEPS = 1000
const AXES: readonly Section['axis'][] = ['off', 'x', 'y', 'z']
const AXIS_LABELS: Record<Section['axis'], string> = {
  off: 'Off', x: 'X (film travel)', y: 'Y (front / back)', z: 'Z (height)',
}

export function SectionPanel() {
  const viewer = useViewer()
  const { setSection } = viewer.actions
  const section = useViewerState(s => s.section)
  const bounds = useViewerState(viewer.selectBounds)
  const pos = bounds ? sectionPosition(section, bounds) : null
  const label = pos === null ? 'No section' : `${section.axis.toUpperCase()} = ${pos.toFixed(2)}mm`
  return (
    <section>
      <h2>Section</h2>
      <div className="row">
        <select
          aria-label="Section axis"
          value={section.axis}
          onChange={e => setSection({ ...section, axis: AXES.find(a => a === e.target.value) ?? 'off' })}
        >
          {AXES.map(a => <option key={a} value={a}>{AXIS_LABELS[a]}</option>)}
        </select>
        <button
          className={section.flip ? 'on' : ''}
          aria-pressed={section.flip}
          title="Show the other side"
          onClick={() => setSection({ ...section, flip: !section.flip })}
        >
          Flip
        </button>
      </div>
      <input
        type="range" min={0} max={SLIDER_STEPS} aria-label="Section position"
        value={Math.round(section.t * SLIDER_STEPS)}
        onChange={e => setSection({ ...section, t: Number(e.target.value) / SLIDER_STEPS })}
      />
      <div className="sub">{label}</div>
    </section>
  )
}
