import { memo, useMemo, useState } from 'react'
import { useViewer, useViewerState } from '../../state/viewer'
import {
  GROUPS, GROUP_LABELS, KINDS, type Group, type Kind, type KindFilter, type PartManifest,
} from '../../types'

const FILTERS: readonly KindFilter[] = ['all', ...KINDS]
const FILTER_LABELS: Record<KindFilter, string> = { all: 'All', printed: 'Printed', bought: 'Bought' }

const PartRow = memo(function PartRow({ part }: { part: PartManifest }) {
  const { setPartView } = useViewer().actions
  const view = useViewerState(s => s.parts[part.name])
  const [x, y, z] = part.size_mm
  return (
    <div className="part">
      <span className={`swatch ${part.kind}`} style={{ background: part.color }} title={part.kind} />
      <label className="pname">
        <input type="checkbox" checked={view.visible} onChange={e => setPartView(part.name, { visible: e.target.checked })} />
        <span>
          {part.name}
          <small>{x} x {y} x {z}mm · {(part.volume_mm3 / 1000).toFixed(1)} cm³ · {part.kind}</small>
        </span>
      </label>
      <button
        className={view.ghost ? 'on' : ''}
        aria-pressed={view.ghost}
        title="See through"
        onClick={() => setPartView(part.name, { ghost: !view.ghost })}
      >
        Ghost
      </button>
    </div>
  )
})

function GroupSection({ group, parts }: { group: Group; parts: readonly PartManifest[] }) {
  const { setGroupView } = useViewer().actions
  const view = useViewerState(s => s.groups[group])
  const [open, setOpen] = useState(true)
  const listId = `parts-${group}`
  return (
    <div className="group" data-hidden={!view.visible}>
      <div className="ghead">
        <button className="twirl" aria-expanded={open} aria-controls={listId} onClick={() => setOpen(o => !o)}>
          <span aria-hidden="true">{open ? '▾' : '▸'}</span> {GROUP_LABELS[group]} <span className="count">{parts.length}</span>
        </button>
        <label>
          <input
            type="checkbox" aria-label={`Show ${GROUP_LABELS[group]}`} checked={view.visible}
            onChange={e => setGroupView(group, { visible: e.target.checked })}
          />
        </label>
        <button
          className={view.ghost ? 'on' : ''}
          aria-pressed={view.ghost}
          aria-label={`Ghost ${GROUP_LABELS[group]}`}
          title="See through the whole group"
          onClick={() => setGroupView(group, { ghost: !view.ghost })}
        >
          Ghost
        </button>
      </div>
      <div id={listId} hidden={!open}>
        {parts.map(p => <PartRow key={p.name} part={p} />)}
      </div>
    </div>
  )
}

function matches(filter: KindFilter, kind: Kind): boolean {
  return filter === 'all' || filter === kind
}

export function PartsPanel() {
  const viewer = useViewer()
  const filter = useViewerState(s => s.filter)
  const byGroup = useMemo(
    () => GROUPS.map(group => ({ group, parts: viewer.manifest.parts.filter(p => p.group === group) })),
    [viewer.manifest],
  )
  return (
    <section>
      <h2>Parts</h2>
      <div className="btns seg" role="group" aria-label="Show parts of kind">
        {FILTERS.map(f => (
          <button key={f} className={f === filter ? 'on' : ''} aria-pressed={f === filter} onClick={() => viewer.actions.setFilter(f)}>
            {FILTER_LABELS[f]}
          </button>
        ))}
      </div>
      {byGroup.map(({ group, parts }) => {
        const shown = parts.filter(p => matches(filter, p.kind))
        return shown.length > 0 ? <GroupSection key={group} group={group} parts={shown} /> : null
      })}
    </section>
  )
}
