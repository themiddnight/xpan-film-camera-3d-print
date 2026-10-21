import { useViewer, useViewerState } from '../state/viewer'
import type { ViewName } from '../types'
import { MechanismPanel } from './MechanismPanel'
import { PartsPanel } from './PartsPanel'
import { SectionPanel } from './SectionPanel'

const SLIDER_STEPS = 100
const VIEWS: ViewName[] = ['iso', 'front', 'rear', 'top']
const VIEW_LABELS: Record<ViewName, string> = { iso: 'Iso', front: 'Front', rear: 'Rear', top: 'Top' }

function ViewPanel() {
  const { showView } = useViewer().actions
  return (
    <section>
      <h2>View</h2>
      <div className="btns">
        {VIEWS.map(v => <button key={v} onClick={() => showView(v)}>{VIEW_LABELS[v]}</button>)}
      </div>
    </section>
  )
}

function ExplodePanel() {
  const { setExplode } = useViewer().actions
  const explode = useViewerState(s => s.explode)
  return (
    <section>
      <h2>Exploded view</h2>
      <input
        type="range" min={0} max={SLIDER_STEPS} aria-label="Explode"
        value={Math.round(explode * SLIDER_STEPS)}
        onChange={e => setExplode(Number(e.target.value) / SLIDER_STEPS)}
      />
      <div className="sub">Groups separate along Y, parts spread from their group.</div>
    </section>
  )
}

/** Controls above the parts list, so a long list never pushes them off screen. */
export function Sidebar() {
  return (
    <aside>
      <div>
        <h1>X-Pan pinhole camera</h1>
        <div className="sub">65 x 24mm on 135 film. Built from cad/ with build123d.</div>
      </div>
      <ViewPanel />
      <MechanismPanel />
      <ExplodePanel />
      <SectionPanel />
      <PartsPanel />
    </aside>
  )
}
