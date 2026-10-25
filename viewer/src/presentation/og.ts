import '@fontsource-variable/archivo/wdth.css'
import { fetchManifest } from '../manifest'
import { spec } from './spec'

declare global {
  interface Window {
    /** Set once the card holds its numbers, so scripts/stills.mjs can capture it. */
    ogCardReady?: boolean
  }
}

/** The two numbers on the card, both from the CAD spec sheet so the card cannot drift from the model. */
function fill(manifest: Awaited<ReturnType<typeof fetchManifest>>) {
  const value = (name: string, text: string) => {
    const node = document.querySelector<HTMLElement>(`[data-spec="${name}"]`)
    if (!node) throw new Error(`the card has no [data-spec="${name}"]`)
    node.textContent = text
  }
  value('frame', `${spec(manifest, 'frame_width', false)} × ${spec(manifest, 'frame_height')}`)
  value('aperture', `f/${spec(manifest, 'f_number', false)}`)
  value('roll', `${spec(manifest, 'frames_per_roll', false)} frames`)
}

fetchManifest().then(
  manifest => {
    fill(manifest)
    document.fonts.ready.then(() => { window.ogCardReady = true })
  },
  (e: unknown) => { console.error(e) },
)
