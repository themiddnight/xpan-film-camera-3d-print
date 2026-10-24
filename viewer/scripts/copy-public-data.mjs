// Copies the data the presentation loads from out/ into dist-public/. Only the manifest, the GLBs
// and the stills go; out/stl and out/step stay private.
import { cpSync, existsSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const viewerRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const outDir = join(viewerRoot, '..', 'out')
const target = join(viewerRoot, 'dist-public')

const PUBLIC_ENTRIES = [
  { path: 'manifest.json', required: true },
  { path: 'glb', required: true },
  { path: 'stills', required: false },
]

mkdirSync(target, { recursive: true })
for (const { path, required } of PUBLIC_ENTRIES) {
  const from = join(outDir, path)
  if (!existsSync(from)) {
    if (required) {
      console.error(`${from} is missing. Run: uv run python cad/export.py`)
      process.exit(1)
    }
    continue
  }
  cpSync(from, join(target, path), { recursive: true })
}
