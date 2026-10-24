import type { Manifest, SpecEntry } from '../types'

/** `{{value:<id>}}` is a spec number with its unit, `{{number:<id>}}` the number alone. */
const REF = /\{\{(value|number):([^}]+)\}\}/g

/**
 * Rounds to what a reader needs: whole numbers from 100 up (f/167), one decimal from 10 (66.5 mm),
 * two below (0.3 mm, 2.71). Trailing zeros are dropped.
 */
export function formatNumber(value: number): string {
  const decimals = Math.abs(value) >= 100 ? 0 : Math.abs(value) >= 10 ? 1 : 2
  return String(Number(value.toFixed(decimals)))
}

export function formatSpec(entry: SpecEntry, withUnit: boolean): string {
  const number = formatNumber(entry.value)
  return withUnit && entry.unit ? `${number} ${entry.unit}` : number
}

/** Spec ids a piece of copy names. */
export function specRefs(text: string): string[] {
  return [...text.matchAll(REF)].map(m => m[2])
}

/** Copy with every spec reference replaced by its value. An unknown id stays visible as its reference. */
export function fillCopy(manifest: Manifest, text: string): string {
  return text.replace(REF, (ref, form: string, id: string) => {
    const entry = manifest.spec_sheet.find(s => s.id === id)
    return entry ? formatSpec(entry, form === 'value') : ref
  })
}

/** One spec entry's value, formatted. Throws on an id the validator would have reported. */
export function spec(manifest: Manifest, id: string, withUnit = true): string {
  const entry = manifest.spec_sheet.find(s => s.id === id)
  if (!entry) throw new Error(`unknown spec "${id}"`)
  return formatSpec(entry, withUnit)
}
