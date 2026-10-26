import type { Kind, Manifest } from '../types'
import { inventory, type InventoryItem, type KindList } from './parts'

const KIND_HEADINGS: Record<Kind, string> = { printed: 'Print', stock: 'Make from stock', bought: 'Buy' }
const KIND_TALLY: Record<Kind, string> = { printed: 'print', stock: 'make', bought: 'buy' }

/** "30 pieces · 13 print · 10 make · 7 buy": the module's total, then each kind that has pieces. */
export function tally(lists: readonly KindList[]): string {
  const total = lists.reduce((n, l) => n + l.pieces, 0)
  return [`${total} ${total === 1 ? 'piece' : 'pieces'}`, ...lists.filter(l => l.pieces > 0).map(l => `${l.pieces} ${KIND_TALLY[l.kind]}`)].join(' · ')
}

/** Whole numbers without a trailing ".0": a 3mm rod reads "3 mm", not "3.0 mm". */
function mm(value: number): string {
  return `${Number(value.toFixed(1))} mm`
}

function Card({ item }: { item: InventoryItem }) {
  return (
    <li className="part-card">
      <img src={`stills/parts/${item.part}.png`} alt="" width={320} height={320} loading="lazy" decoding="async" />
      <p className="part-name">
        {item.label}
        {item.count > 1 && <span className="part-count"> ×{item.count}</span>}
      </p>
      <p className="part-meta">
        <span>{mm(item.largestMm)}</span>
        {item.bom !== null && <a href={`#bom-${item.bom}`}>BOM #{item.bom}</a>}
      </p>
    </li>
  )
}

/**
 * Every piece of the camera, by module and then by how a builder gets it. A flat inventory built
 * from the manifest; the thumbnails are the stills `pnpm stills` writes.
 */
export function PartsInventory({ manifest }: { manifest: Manifest }) {
  return (
    <div className="parts">
      {inventory(manifest).map(module => (
        <section key={module.group} className="parts-module" aria-labelledby={`parts-${module.group}`}>
          <h3 id={`parts-${module.group}`}>{module.label}</h3>
          <p className="parts-tally">{tally(module.lists)}</p>
          {module.lists.filter(l => l.items.length > 0).map(list => (
            <div key={list.kind} className={`parts-kind parts-${list.kind}`}>
              <h4>{KIND_HEADINGS[list.kind]}</h4>
              <ul className="parts-grid">
                {list.items.map(item => <Card key={item.part} item={item} />)}
              </ul>
            </div>
          ))}
        </section>
      ))}
    </div>
  )
}
