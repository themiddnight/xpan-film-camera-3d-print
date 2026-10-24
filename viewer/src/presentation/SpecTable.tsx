import type { Manifest, SpecSection } from '../types'
import { formatSpec, formatNumber } from './spec'

/** Interface entries that belong to the lens joint. Every other interface entry is a body-to-film-back value. */
const LENS_JOINT = /^(m42_|image_circle$)/

const JOINTS = [
  { title: 'Film back to body', test: (id: string) => !LENS_JOINT.test(id) },
  { title: 'Body to lens', test: (id: string) => LENS_JOINT.test(id) },
] as const

function Row({ label, value, unit, draft }: { label: string; value: string; unit: string; draft: boolean }) {
  return (
    <tr>
      <th scope="row">{label}{draft && <span className="spec-draft">Draft</span>}</th>
      <td className="spec-value">{value}</td>
      <td className="spec-unit">{unit}</td>
    </tr>
  )
}

/**
 * One section of the spec sheet as a table, every value read from the manifest. The interface section
 * splits into its two joints. A draft tag shows only where it tells rows apart, so a table that is
 * draft throughout carries no tags (the section says so once).
 */
export function SpecTable({ manifest, section }: { manifest: Manifest; section: SpecSection }) {
  const entries = manifest.spec_sheet.filter(s => s.section === section)
  const mixed = entries.some(e => e.status === 'locked') && entries.some(e => e.status === 'draft')
  const groups = section === 'interface'
    ? JOINTS.map(j => ({ title: j.title, rows: entries.filter(e => j.test(e.id)) }))
    : [{ title: null, rows: entries }]
  return (
    <div className="table-scroll">
      <table className="spec-table">
        {groups.map(({ title, rows }) => (
          <tbody key={title ?? section}>
            {title && <tr><th colSpan={3} scope="colgroup" className="spec-group">{title}</th></tr>}
            {rows.map(e => (
              <Row key={e.id} label={e.label} value={e.unit ? formatNumber(e.value) : formatSpec(e, false)} unit={e.unit} draft={mixed && e.status === 'draft'} />
            ))}
          </tbody>
        ))}
      </table>
    </div>
  )
}
