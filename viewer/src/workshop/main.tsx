import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'
import './index.css'

/** scripts/check-public.mjs searches the public build for this string, so workshop code there fails the build. */
export const WORKSHOP_MARKER = 'xpan-workshop-entry'

// The bundler drops an unused export, so the marker is also written where it cannot be dropped.
document.documentElement.dataset.entry = WORKSHOP_MARKER

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
