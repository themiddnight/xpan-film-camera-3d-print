// Fails when the public build holds anything private: the workshop page or its code, or the
// STL and STEP files. Usage: node scripts/check-public.mjs [dir]   (default: dist-public)
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const viewerRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const dir = process.argv[2] ?? join(viewerRoot, 'dist-public')

const workshopEntry = readFileSync(join(viewerRoot, 'src/workshop/main.tsx'), 'utf8')
const marker = /export const WORKSHOP_MARKER = '([^']+)'/.exec(workshopEntry)?.[1]
if (!marker) {
  console.error('src/workshop/main.tsx no longer exports WORKSHOP_MARKER as a string literal.')
  process.exit(1)
}
if (!existsSync(dir)) {
  console.error(`${dir} does not exist. Run the public build first.`)
  process.exit(1)
}

function* walk(folder) {
  for (const entry of readdirSync(folder, { withFileTypes: true })) {
    const path = join(folder, entry.name)
    if (entry.isDirectory()) yield* walk(path)
    else yield path
  }
}

const problems = []
if (!existsSync(join(dir, 'index.html'))) problems.push('index.html is missing')
for (const file of walk(dir)) {
  const name = relative(dir, file)
  if (/(^|\/)workshop\.html$/.test(name)) problems.push(`${name}: the workshop page is in the public build`)
  if (/\.(stl|step|stp)$/i.test(name)) problems.push(`${name}: a CAD source file is in the public build`)
  if (/\.(js|mjs|html|css)$/.test(name)) {
    const text = readFileSync(file, 'utf8')
    if (text.includes(marker)) problems.push(`${name}: contains the workshop marker ${marker}`)
    if (text.includes('workshop.html')) problems.push(`${name}: links to workshop.html`)
  }
}

if (problems.length > 0) {
  console.error(`Public build check failed in ${dir}:\n${problems.map(p => `  ${p}`).join('\n')}`)
  process.exit(1)
}
console.log(`Public build check passed: ${dir} has no workshop page, workshop code or CAD source files.`)
