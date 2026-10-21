import type { MutableRefObject } from 'react'
import type { Axis, Manifest, PartView, Section, ViewName } from '../types'
import { SpinLabel } from './SpinLabel'

interface Props {
  manifest: Manifest
  views: Record<string, PartView>
  onPartView: (name: string, view: PartView) => void
  section: Section
  sectionLabel: string
  onSection: (section: Section) => void
  explode: number
  onExplode: (value: number) => void
  spinning: boolean
  onSpin: () => void
  spinAngle: MutableRefObject<number>
  onView: (view: ViewName) => void
}

const SLIDER_STEPS = 1000
const VIEWS: ViewName[] = ['iso', 'front', 'rear', 'top']
const VIEW_LABELS: Record<ViewName, string> = { iso: 'Iso', front: 'Front', rear: 'Rear', top: 'Top' }
const AXIS_LABELS: Record<Axis | 'off', string> = {
  off: 'Off', x: 'X (film travel)', y: 'Y (front / back)', z: 'Z (height)',
}

export function Sidebar(p: Props) {
  const hasSpinner = p.manifest.parts.some(part => part.spin_axis_xy)
  return (
    <aside>
      <div>
        <h1>X-Pan pinhole camera</h1>
        <div className="sub">65 x 24mm on 135 film. Built from cad/ with build123d.</div>
      </div>

      <section>
        <h2>Parts</h2>
        {p.manifest.parts.map(part => {
          const view = p.views[part.name]
          const [x, y, z] = part.size_mm
          return (
            <div className="part" key={part.name}>
              <span className="swatch" style={{ background: part.color }} />
              <label>
                <input
                  type="checkbox"
                  checked={view.visible}
                  onChange={e => p.onPartView(part.name, { ...view, visible: e.target.checked })}
                />{' '}
                {part.name}
                <small>{x} x {y} x {z}mm · {(part.volume_mm3 / 1000).toFixed(1)} cm³</small>
              </label>
              <button
                className={view.ghost ? 'on' : ''}
                title="See through"
                onClick={() => p.onPartView(part.name, { ...view, ghost: !view.ghost })}
              >
                Ghost
              </button>
            </div>
          )
        })}
      </section>

      <section>
        <h2>Section</h2>
        <div className="row">
          <select
            aria-label="Section axis"
            value={p.section.axis}
            onChange={e => p.onSection({ ...p.section, axis: e.target.value as Section['axis'] })}
          >
            {(Object.keys(AXIS_LABELS) as (Axis | 'off')[]).map(a => <option key={a} value={a}>{AXIS_LABELS[a]}</option>)}
          </select>
          <button
            className={p.section.flip ? 'on' : ''}
            title="Show the other side"
            onClick={() => p.onSection({ ...p.section, flip: !p.section.flip })}
          >
            Flip
          </button>
        </div>
        <input
          type="range" min={0} max={SLIDER_STEPS} aria-label="Section position"
          value={Math.round(p.section.t * SLIDER_STEPS)}
          onChange={e => p.onSection({ ...p.section, t: Number(e.target.value) / SLIDER_STEPS })}
        />
        <div className="sub">{p.sectionLabel}</div>
      </section>

      <section>
        <h2>Exploded view</h2>
        <input
          type="range" min={0} max={100} aria-label="Explode"
          value={Math.round(p.explode * 100)}
          onChange={e => p.onExplode(Number(e.target.value) / 100)}
        />
      </section>

      {hasSpinner && (
        <section>
          <h2>Mechanism</h2>
          <div className="btns">
            <button className={p.spinning ? 'on' : ''} onClick={p.onSpin}>Turn sprocket</button>
          </div>
          <SpinLabel spinning={p.spinning} spinAngle={p.spinAngle} filmAdvanceMm={p.manifest.film_advance_mm} />
        </section>
      )}

      <section>
        <h2>View</h2>
        <div className="btns">
          {VIEWS.map(v => <button key={v} onClick={() => p.onView(v)}>{VIEW_LABELS[v]}</button>)}
        </div>
      </section>
    </aside>
  )
}
