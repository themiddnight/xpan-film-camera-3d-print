import { useEffect, type RefObject } from 'react'
import { useThree } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, View } from '@react-three/drei'
import { PartsScene } from '../scene/PartsScene'
import { ViewerContext, type Viewer } from '../state/viewer'
import { PHONE, useMedia } from './media'
import { Pins } from './Pins'
import { ShotRig } from './ShotRig'
import { applyStaging, SHOT_FOV_DEG } from './staging'
import { StudioLights } from './StudioLights'
import type { Staging } from './story'

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
 */
export function StagedView({ track, viewer, staging, interactive }: {
  track: RefObject<HTMLElement | null>
  viewer: Viewer
  staging: Staging
  interactive: boolean
}) {
  const compact = useMedia(PHONE)
  return (
    <View track={track as RefObject<HTMLElement>}>
      <ViewerContext.Provider value={viewer}>
        <PerspectiveCamera makeDefault fov={SHOT_FOV_DEG} near={1} far={5000} up={[0, 0, 1]} />
        <StudioLights />
        <PartsScene />
        <StagingSync viewer={viewer} staging={staging} />
        {interactive && <OrbitControls makeDefault enableZoom={false} enablePan={false} />}
        <ShotRig shot={staging.shot} />
        <Pins viewer={viewer} ids={staging.pins ?? []} compact={compact} />
      </ViewerContext.Provider>
    </View>
  )
}
