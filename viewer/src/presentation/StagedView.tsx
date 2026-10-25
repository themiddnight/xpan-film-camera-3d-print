import { useEffect, type ReactNode, type RefObject } from 'react'
import { useThree } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, View } from '@react-three/drei'
import { PartsScene } from '../scene/PartsScene'
import { useSelector } from '../state/store'
import { ViewerContext, type Viewer } from '../state/viewer'
import { PHONE, useMedia } from './media'
import { Pins } from './Pins'
import { ShotRig } from './ShotRig'
import { applyStaging, SHOT_FOV_DEG } from './staging'
import { StudioLights } from './StudioLights'
import { Turntable } from './Turntable'
import type { Staging } from './story'

const still = () => 0

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
export function StagedView({ track, focus, viewer, staging, interactive, turn = still, children }: {
  track: RefObject<HTMLElement | null>
  focus?: RefObject<HTMLElement | null>
  viewer: Viewer
  staging: Staging
  interactive: boolean
  turn?: () => number
  children?: ReactNode
}) {
  const compact = useMedia(PHONE)
  // Until every part has loaded or failed there is no shot, and the default camera would show a
  // close-up of whichever part arrived first.
  const framed = useSelector(viewer.store, s => viewer.selectBounds(s) !== null)
  return (
    <View track={track as RefObject<HTMLElement>} visible={framed}>
      <ViewerContext.Provider value={viewer}>
        <PerspectiveCamera makeDefault fov={SHOT_FOV_DEG} near={1} far={5000} up={[0, 0, 1]} />
        <StudioLights />
        <Turntable angle={turn}>
          <PartsScene />
          <Pins viewer={viewer} ids={framed ? staging.pins ?? [] : []} compact={compact} />
          {children}
        </Turntable>
        <StagingSync viewer={viewer} staging={staging} />
        {interactive && <OrbitControls makeDefault enableZoom={false} enablePan={false} />}
        <ShotRig shot={staging.shot} track={track} focus={focus} />
      </ViewerContext.Provider>
    </View>
  )
}
