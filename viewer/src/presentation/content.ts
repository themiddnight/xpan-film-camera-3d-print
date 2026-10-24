import specifications from './content/specifications.md?raw'
import filmTransport from './content/film-transport.md?raw'
import intro from './content/intro.md?raw'
import interfaceSpec from './content/interface.md?raw'
import designYourOwn from './content/design-your-own.md?raw'
import bom from './content/bom.md?raw'
import printing from './content/printing.md?raw'
import decisions from './content/decisions.md?raw'
import type { Doc } from './maker'

/** The maker half, in page order. */
export const DOCS: readonly Doc[] = [
  { id: 'intro', markdown: intro },
  { id: 'specifications', markdown: specifications },
  { id: 'film-transport', markdown: filmTransport },
  { id: 'interface', markdown: interfaceSpec },
  { id: 'design-your-own', markdown: designYourOwn },
  { id: 'bom', markdown: bom },
  { id: 'printing', markdown: printing },
  { id: 'decisions', markdown: decisions },
]
