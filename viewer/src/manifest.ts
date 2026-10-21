import {
  GROUPS, KINDS, type Cycle, type CycleKey, type Drive, type FilmStrip, type Manifest, type Mechanism, type PartManifest, type Readout,
  type Vec3,
} from './types'

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

function boolean(x: unknown, path: string): boolean {
  return typeof x === 'boolean' ? x : fail(path, 'true or false', x)
}

function strings(x: unknown, path: string): readonly string[] {
  return array(x, path).map((s, i) => string(s, `${path}[${i}]`))
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
  const kind = oneOf(o.kind, ['rotate', 'slide', 'stretch'], `${path}.kind`)
  switch (kind) {
    case 'rotate':
    case 'stretch':
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
    cyclic: o.cyclic === undefined ? false : boolean(o.cyclic, `${path}.cyclic`),
    internal: o.internal === undefined ? false : boolean(o.internal, `${path}.internal`),
    drives: array(o.drives, `${path}.drives`).map((d, i) => drive(d, `${path}.drives[${i}]`)),
  }
}

function cycleKey(x: unknown, path: string): CycleKey {
  const o = record(x, path)
  const values = record(o.values, `${path}.values`)
  return {
    t: number(o.t, `${path}.t`),
    values: Object.fromEntries(Object.entries(values).map(([k, v]) => [k, number(v, `${path}.values.${k}`)])),
    phase: string(o.phase, `${path}.phase`),
  }
}

function cycle(x: unknown, path: string): Cycle {
  const o = record(x, path)
  const keys = array(o.keys, `${path}.keys`).map((k, i) => cycleKey(k, `${path}.keys[${i}]`))
  if (keys.length < 2 || keys[0].t !== 0) fail(`${path}.keys`, 'two or more keys starting at t = 0', o.keys)
  keys.forEach((k, i) => { if (i > 0 && k.t <= keys[i - 1].t) fail(`${path}.keys[${i}].t`, 'a time after the previous key', k.t) })
  const counter = record(o.counter, `${path}.counter`)
  const focus = record(o.focus, `${path}.focus`)
  return {
    id: string(o.id, `${path}.id`),
    label: string(o.label, `${path}.label`),
    keys,
    counter: {
      mechanism: string(counter.mechanism, `${path}.counter.mechanism`),
      count_per_unit: number(counter.count_per_unit, `${path}.counter.count_per_unit`),
      count_label: string(counter.count_label, `${path}.counter.count_label`),
      per_unit: number(counter.per_unit, `${path}.counter.per_unit`),
      unit: string(counter.unit, `${path}.counter.unit`),
    },
    focus: { ghost: strings(focus.ghost, `${path}.focus.ghost`), hide: strings(focus.hide, `${path}.focus.hide`) },
  }
}

function filmStrip(x: unknown, path: string): FilmStrip | null {
  if (x === undefined || x === null) return null
  const o = record(x, path)
  const points = array(o.points, `${path}.points`).map((p, i): readonly [number, number] => {
    const xy = array(p, `${path}.points[${i}]`)
    if (xy.length !== 2) fail(`${path}.points[${i}]`, 'two numbers', p)
    return [number(xy[0], `${path}.points[${i}][0]`), number(xy[1], `${path}.points[${i}][1]`)]
  })
  if (points.length < 2) fail(`${path}.points`, 'two or more points', o.points)
  const positive = (key: string) => {
    const v = number(o[key], `${path}.${key}`)
    return v > 0 ? v : fail(`${path}.${key}`, 'a positive number', v)
  }
  return {
    part: string(o.part, `${path}.part`),
    mechanism: string(o.mechanism, `${path}.mechanism`),
    advance_per_unit: number(o.advance_per_unit, `${path}.advance_per_unit`),
    s0: number(o.s0, `${path}.s0`),
    ds: positive('ds'),
    points,
    width: positive('width'),
    pitch: positive('pitch'),
    perf_along: positive('perf_along'),
    perf_across: positive('perf_across'),
    perf_row_z: positive('perf_row_z'),
    first_perf_s: number(o.first_perf_s, `${path}.first_perf_s`),
  }
}

/** Validates parsed JSON once and returns the domain type; everything downstream trusts it. */
export function parseManifest(json: unknown): Manifest {
  const o = record(json, 'manifest')
  const parts = array(o.parts, 'manifest.parts').map((p, i) => part(p, `manifest.parts[${i}]`))
  const mechanisms = array(o.mechanisms, 'manifest.mechanisms').map((m, i) => mechanism(m, `manifest.mechanisms[${i}]`))
  const strip = filmStrip(o.film_strip, 'manifest.film_strip')
  const cycles = o.cycles === undefined ? [] : array(o.cycles, 'manifest.cycles').map((c, i) => cycle(c, `manifest.cycles[${i}]`))
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

  cycles.forEach((c, i) => {
    const known = (id: string) => ids.has(id)
    c.keys.forEach((k, j) => Object.keys(k.values).forEach(id => {
      if (!known(id)) throw new ManifestError(`manifest.cycles[${i}].keys[${j}].values: no mechanism ${JSON.stringify(id)}`)
    }))
    if (!known(c.counter.mechanism)) throw new ManifestError(`manifest.cycles[${i}].counter.mechanism: no mechanism ${JSON.stringify(c.counter.mechanism)}`)
    for (const name of [...c.focus.ghost, ...c.focus.hide]) {
      if (!names.has(name)) throw new ManifestError(`manifest.cycles[${i}].focus: no part named ${JSON.stringify(name)}`)
    }
  })

  if (strip && !names.has(strip.part)) throw new ManifestError(`manifest.film_strip.part: no part named ${JSON.stringify(strip.part)}`)
  if (strip && !ids.has(strip.mechanism)) throw new ManifestError(`manifest.film_strip.mechanism: no mechanism ${JSON.stringify(strip.mechanism)}`)

  return {
    glb_unit_scale: number(o.glb_unit_scale, 'manifest.glb_unit_scale'),
    film_advance_mm: number(o.film_advance_mm, 'manifest.film_advance_mm'),
    parts,
    mechanisms,
    cycles,
    film_strip: strip,
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
