import { parseManifest } from '../manifest'
import type { Manifest } from '../types'

const files = import.meta.glob('../../../out/manifest.json', { query: '?raw', import: 'default', eager: true })

/** The manifest the CAD export wrote to out/, parsed as the app parses it. For tests only. */
export function realManifest(): Manifest {
  const raw = Object.values(files)[0]
  if (typeof raw !== 'string') throw new Error('out/manifest.json is missing. Run: uv run python cad/export.py')
  return parseManifest(JSON.parse(raw))
}
