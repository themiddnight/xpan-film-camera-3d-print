import { useEffect, type ReactNode } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { NeutralToneMapping } from 'three'
import { PHONE, useMedia } from './media'

/** Views follow their track elements, which move on scroll without any canvas resize. */
function RedrawOnScroll() {
  const invalidate = useThree(s => s.invalidate)
  useEffect(() => {
    const redraw = () => invalidate()
    window.addEventListener('scroll', redraw, { passive: true })
    return () => window.removeEventListener('scroll', redraw)
  }, [invalidate])
  return null
}

/**
 * The one WebGL canvas of the presentation, fixed behind the page. It draws only when asked:
 * a view's motion, a camera tween, orbiting, a resize or a scroll requests the next frame. The canvas
 * is transparent, so the page background is the studio seamless. Pass `StagedView`s as children.
 */
export function StageCanvas({ children }: { children: ReactNode }) {
  const phone = useMedia(PHONE)
  return (
    <Canvas
      frameloop="demand"
      dpr={phone ? [1, 1.5] : [1, 2]}
      gl={{ localClippingEnabled: true, toneMapping: NeutralToneMapping }}
      style={{ position: 'fixed', inset: 0, pointerEvents: 'none' }}
    >
      <RedrawOnScroll />
      {children}
    </Canvas>
  )
}
