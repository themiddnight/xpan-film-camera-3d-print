import bomMarkdown from '../../../docs/bom.md?raw'
import { parseBom } from './bom'

/** The bill of materials from docs/bom.md: what to buy, how many, which spec and what it is for. */
export function BomTable() {
  const rows = parseBom(bomMarkdown)
  return (
    <div className="table-scroll">
      <table className="bom-table">
        <thead>
          <tr><th scope="col">Part</th><th scope="col">Qty</th><th scope="col">Spec</th><th scope="col">Used for</th></tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} id={`bom-${r.id}`}>
              <th scope="row">{r.part}</th>
              <td>{r.qty}</td>
              <td>{r.spec}</td>
              <td>{r.usedFor}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
