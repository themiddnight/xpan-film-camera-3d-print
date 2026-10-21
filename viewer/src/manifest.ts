import { GROUPS, KINDS, type Drive, type Manifest, type Mechanism, type PartManifest, type Readout, type Vec3 } from './types'

export const MANIFEST_URL = new URL('manifest.json', document.baseURI).href

const EXPORT_HINT = 'Run: uv run python cad/export.py'

/** The manifest is unreadable or does not match the shape the viewer expects. */
export class ManifestError extends Error {}

function describe(x: unknown): string {
  if (x === undefined) return 'nothing'
  return JSON.stringify(x)?.slice(0, 60) ?? String(x)
}

function fail(path: string, expected: string, got: unknown): never {
  throw new ManifestError(`${path}: expected ${expected}, got ${describe(got)}`)
}

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null && !Array.isArray(x)
}

function record(x: unknown, path: string): Record<string, unknown> {
  return isRecord(x) ? x : fail(path, 'an object', x)
}

function array(x: unknown, path: string): readonly unknown[] {
  return Array.isArray(x) ? x : fail(path, 'an array', x)
}

function string(x: unknown, path: string): string {
  return typeof x === 'string' && x !== '' ? x : fail(path, 'a non-empty string', x)
}

function number(x: unknown, path: string): number {
  return typeof x === 'number' && Number.isFinite(x) ? x : fail(path, 'a finite number', x)
}

function oneOf<T extends string>(x: unknown, allowed: readonly T[], path: string): T {
  return allowed.find(a => a === x) ?? fail(path, `one of ${allowed.join(', ')}`, x)
}

function vec3(x: unknown, path: string): Vec3 {
  const items = array(x, path)
  if (items.length !== 3) fail(path, 'three numbers', x)
  return [number(items[0], `${path}[0]`), number(items[1], `${path}[1]`), number(items[2], `${path}[2]`)]
}

function part(x: unknown, path: string): PartManifest {
  const o = record(x, path)
  return {
    name: string(o.name, `${path}.name`),
    glb: string(o.glb, `${path}.glb`),
    group: oneOf(o.group, GROUPS, `${path}.group`),
    kind: oneOf(o.kind, KINDS, `${path}.kind`),
    color: string(o.color, `${path}.color`),
    volume_mm3: number(o.volume_mm3, `${path}.volume_mm3`),
    size_mm: vec3(o.size_mm, `${path}.size_mm`),
  }
}

function drive(x: unknown, path: string): Drive {
  const o = record(x, path)
  const axis = vec3(o.axis, `${path}.axis`)
  if (axis.every(c => c === 0)) fail(`${path}.axis`, 'a non-zero vector', axis)
  const base = { part: string(o.part, `${path}.part`), axis, amount: number(o.amount, `${path}.amount`) }
  const kind = oneOf(o.kind, ['rotate', 'slide'], `${path}.kind`)
  switch (kind) {
    case 'rotate':
      return { ...base, kind, origin: o.origin === undefined ? [0, 0, 0] : vec3(o.origin, `${path}.origin`) }
    case 'slide':
      return { ...base, kind }
    default: {
      const _exhaustive: never = kind
      return _exhaustive
    }
  }
}

function readout(x: unknown, path: string): Readout | null {
  if (x === undefined || x === null) return null
  const o = record(x, path)
  return { per_unit: number(o.per_unit, `${path}.per_unit`), unit: string(o.unit, `${path}.unit`) }
}

function mechanism(x: unknown, path: string): Mechanism {
  const o = record(x, path)
  return {
    id: string(o.id, `${path}.id`),
    label: string(o.label, `${path}.label`),
    readout: readout(o.readout, `${path}.readout`),
    drives: array(o.drives, `${path}.drives`).map((d, i) => drive(d, `${path}.drives[${i}]`)),
  }
}

/** Validates parsed JSON once and returns the domain type; everything downstream trusts it. */
export function parseManifest(json: unknown): Manifest {
  const o = record(json, 'manifest')
  const parts = array(o.parts, 'manifest.parts').map((p, i) => part(p, `manifest.parts[${i}]`))
  const mechanisms = array(o.mechanisms, 'manifest.mechanisms').map((m, i) => mechanism(m, `manifest.mechanisms[${i}]`))
  if (parts.length === 0) throw new ManifestError('manifest.parts: the list is empty')

  const names = new Set<string>()
  for (const p of parts) {
    if (names.has(p.name)) throw new ManifestError(`manifest.parts: duplicate part name ${JSON.stringify(p.name)}`)
    names.add(p.name)
  }
  const ids = new Set<string>()
  mechanisms.forEach((m, i) => {
    if (ids.has(m.id)) throw new ManifestError(`manifest.mechanisms[${i}].id: duplicate id ${JSON.stringify(m.id)}`)
    ids.add(m.id)
    m.drives.forEach((d, j) => {
      if (!names.has(d.part)) {
        throw new ManifestError(`manifest.mechanisms[${i}].drives[${j}].part: no part named ${JSON.stringify(d.part)}`)
      }
    })
  })

  return {
    glb_unit_scale: number(o.glb_unit_scale, 'manifest.glb_unit_scale'),
    film_advance_mm: number(o.film_advance_mm, 'manifest.film_advance_mm'),
    parts,
    mechanisms,
  }
}

/** Fetches and parses the manifest; every failure comes back as an Error with a readable message. */
export async function fetchManifest(url: string = MANIFEST_URL): Promise<Manifest> {
  const response = await fetch(url, { cache: 'no-store' })
  if (!response.ok) throw new ManifestError(`Cannot read ${url} (${response.status}). ${EXPORT_HINT}`)
  const json: unknown = await response.json().catch(() => {
    throw new ManifestError(`${url} is not valid JSON. ${EXPORT_HINT}`)
  })
  try {
    return parseManifest(json)
  } catch (e) {
    if (e instanceof ManifestError) throw new ManifestError(`The manifest at ${url} is not usable.\n${e.message}\n${EXPORT_HINT}`)
    throw e
  }
}
