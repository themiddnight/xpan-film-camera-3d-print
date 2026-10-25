import { useEffect, useState, type ReactNode, type RefObject } from 'react'
import { useThree } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, View } from '@react-three/drei'
import { PartsScene } from '../scene/PartsScene'
import { useSelector } from '../state/store'
import { useViewerState, ViewerContext, type Viewer } from '../state/viewer'
import { PHONE, useMedia } from './media'
import { Pins } from './Pins'
import { ShotRig } from './ShotRig'
import { applyStaging, SHOT_FOV_DEG } from './staging'
import { StudioLights } from './StudioLights'
import { Turntable } from './Turntable'
import type { Staging } from './story'

const still = () => 0

/** Frames the shot at the viewer's explode, which changes as the page scrolls; only this re-renders. */
function LiveShotRig({ shot, track, focus }: {
  shot: Staging['shot']
  track: RefObject<HTMLElement | null>
  focus?: RefObject<HTMLElement | null>
}) {
  const explode = useViewerState(s => s.explode)
  return <ShotRig shot={shot} explode={explode} follow track={track} focus={focus} />
}

/** Whether the element is anywhere in the viewport, so a view far off the page keeps no labels. */
function useOnScreen(ref: RefObject<HTMLElement | null>): boolean {
  const [on, setOn] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(([entry]) => setOn(entry.isIntersecting))
    observer.observe(el)
    return () => observer.disconnect()
  }, [ref])
  return on
}

function StagingSync({ viewer, staging }: { viewer: Viewer; staging: Staging }) {
  const invalidate = useThree(s => s.invalidate)
  useEffect(() => {
    applyStaging(viewer, staging)
    invalidate()
  }, [viewer, staging, invalidate])
  return null
}

/**
 * One staged picture of the camera, drawn into the shared canvas over the rect of `track`. Render it
 * inside `StageCanvas`. `track` must be a positioned element, since pin labels are placed inside it.
 * Each view needs its own viewer, so its mechanisms move independently of every other view.
 * `focus`, an element inside `track`, is where the shot is framed; the picture still fills `track`.
 * `turn` returns the turntable angle in radians, read every frame. Children render on the turntable with
 * the parts, so overlays in camera coordinates turn with them, with the viewer in context.
 */
export function StagedView({ track, focus, viewer, staging, interactive, turn = still, spin = 0, frameExplode, children }: {
  track: RefObject<HTMLElement | null>
  focus?: RefObject<HTMLElement | null>
  viewer: Viewer
  staging: Staging
  interactive: boolean
  turn?: () => number
  /** Radians a second the parts keep turning, for a chapter that should not sit still. */
  spin?: number
  /**
   * The explode the camera is framed at: a fixed amount, or `live` to follow the viewer's own, which
   * the scroll drives, so the camera pulls back as the parts separate.
   */
  frameExplode?: number | 'live'
  children?: ReactNode
}) {
  const compact = useMedia(PHONE)
  // Until every part has loaded or failed there is no shot, and the default camera would show a
  // close-up of whichever part arrived first.
  const framed = useSelector(viewer.store, s => viewer.selectBounds(s) !== null)
  // Labels mount in a layer over the page, so a view that has scrolled away must not keep any.
  const onScreen = useOnScreen(track)
  return (
    <View track={track as RefObject<HTMLElement>} visible={framed}>
      <ViewerContext.Provider value={viewer}>
        <PerspectiveCamera makeDefault fov={SHOT_FOV_DEG} near={1} far={5000} up={[0, 0, 1]} />
        <StudioLights />
        {/* Before the children, so its reset to rest runs ahead of their effects that pose the parts. */}
        <StagingSync viewer={viewer} staging={staging} />
        <Turntable angle={turn} spin={spin}>
          <PartsScene />
          <Pins viewer={viewer} ids={framed && onScreen ? staging.pins ?? [] : []} compact={compact} track={track} />
          {children}
        </Turntable>
        {interactive && <OrbitControls makeDefault enableZoom={false} enablePan={false} />}
        {frameExplode === 'live'
          ? <LiveShotRig shot={staging.shot} track={track} focus={focus} />
          : <ShotRig shot={staging.shot} explode={frameExplode} track={track} focus={focus} />}
      </ViewerContext.Provider>
    </View>
  )
}
