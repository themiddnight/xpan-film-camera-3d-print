import { useEffect, type ReactNode } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { NeutralToneMapping } from 'three'
import { PHONE, useMedia } from './media'

/**
 * Views follow their track elements, which move on scroll without any canvas resize. Two frames: drei
 * learns that a view has come on screen during a frame and draws it only in the next one, so a view
 * scrolled in by the last scroll event would stay blank after one.
 */
function RedrawOnScroll() {
  const invalidate = useThree(s => s.invalidate)
  useEffect(() => {
    const redraw = () => invalidate(2)
    window.addEventListener('scroll', redraw, { passive: true })
    return () => window.removeEventListener('scroll', redraw)
  }, [invalidate])
  return null
}

/**
 * The one WebGL canvas of the presentation, fixed behind the page. It draws only when asked:
 * a view's motion, a camera tween, orbiting, a resize or a scroll requests the next frame. The canvas
 * is transparent outside its views, so the page background shows through; it sits above the maker sheet so
 * figures draw onto it. Pass `StagedView`s as children.
 */
export function StageCanvas({ children }: { children: ReactNode }) {
  const phone = useMedia(PHONE)
  return (
    <Canvas
      frameloop="demand"
      dpr={phone ? [1, 1.5] : [1, 2]}
      gl={{ localClippingEnabled: true, toneMapping: NeutralToneMapping }}
      style={{ position: 'fixed', inset: 0, zIndex: 2, pointerEvents: 'none' }}
    >
      <RedrawOnScroll />
      {children}
    </Canvas>
  )
}
