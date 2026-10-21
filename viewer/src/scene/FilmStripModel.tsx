import { memo, useEffect, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import {
  BufferGeometry, CanvasTexture, DoubleSide, Float32BufferAttribute, MeshStandardMaterial, RepeatWrapping,
  SRGBColorSpace,
} from 'three'
import { useViewer } from '../state/viewer'
import type { FilmStrip, PartManifest } from '../types'
import { SURFACE, usePartDisplay } from './partDisplay'

/** Texture pixels per mm; enough for crisp perforation corners up close. */
const PX_PER_MM = 24
const PERF_CORNER_MM = 0.5

/**
 * One perforation pitch of film as a tile: the base colour with both perforation holes cut out
 * (transparent). It repeats along the strip, so scrolling its offset moves every perforation.
 */
function perforationTile(strip: FilmStrip, color: string): CanvasTexture {
  const w = Math.round(strip.pitch * PX_PER_MM)
  const h = Math.round(strip.width * PX_PER_MM)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('No 2D canvas for the film texture')
  ctx.fillStyle = color
  ctx.fillRect(0, 0, w, h)
  ctx.globalCompositeOperation = 'destination-out'
  const holeW = strip.perf_along * PX_PER_MM
  const holeH = strip.perf_across * PX_PER_MM
  for (const z of [-strip.perf_row_z, strip.perf_row_z]) {
    const cy = (z + strip.width / 2) * PX_PER_MM
    ctx.beginPath()
    ctx.roundRect(w / 2 - holeW / 2, cy - holeH / 2, holeW, holeH, PERF_CORNER_MM * PX_PER_MM)
    ctx.fill()
  }
  const texture = new CanvasTexture(canvas)
  texture.wrapS = RepeatWrapping
  texture.colorSpace = SRGBColorSpace
  texture.anisotropy = 8
  return texture
}

/**
 * A ribbon along the strip's centre line, Z across its width. Texture u counts perforation pitches
 * from a perforation centre, so u = 0.5 lands on one at rest.
 */
function ribbon(strip: FilmStrip): BufferGeometry {
  const positions: number[] = []
  const uvs: number[] = []
  const indices: number[] = []
  const half = strip.width / 2
  strip.points.forEach(([x, y], i) => {
    const s = strip.s0 + i * strip.ds
    const u = (s - strip.first_perf_s) / strip.pitch + 0.5
    positions.push(x, y, -half, x, y, half)
    uvs.push(u, 0, u, 1)
    if (i > 0) {
      const a = 2 * (i - 1)
      indices.push(a, a + 2, a + 1, a + 1, a + 2, a + 3)
    }
  })
  const geometry = new BufferGeometry()
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))
  geometry.setAttribute('uv', new Float32BufferAttribute(uvs, 2))
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  geometry.computeBoundingBox()
  return geometry
}

/**
 * The film drawn from its path instead of the static GLB, so the perforations travel with the
 * advance: as the sprocket turns one frame, the strip moves 66.5mm along its path and each tooth keeps
 * its perforation.
 */
export const FilmStripModel = memo(function FilmStripModel({ spec, strip }: { spec: PartManifest; strip: FilmStrip }) {
  const { motion } = useViewer()

  const { geometry, material, texture } = useMemo(() => {
    const texture = perforationTile(strip, spec.color)
    const material = new MeshStandardMaterial({
      map: texture,
      // Low enough that a ghosted strip (opacity 0.25) still draws; the holes have alpha 0 and are still cut.
      alphaTest: 0.1, side: DoubleSide, ...SURFACE[spec.kind],
    })
    return { geometry: ribbon(strip), material, texture }
  }, [strip, spec.color, spec.kind])

  // The material is disposed with the part display; its map and the geometry are not.
  useEffect(() => () => { texture.dispose(); geometry.dispose() }, [texture, geometry])

  const materials = useMemo(() => [material], [material])
  const worldBox = useMemo(() => geometry.boundingBox!.clone(), [geometry])
  const { node, mode } = usePartDisplay(spec, materials, worldBox)

  useFrame(() => {
    const travel = motion.get(strip.mechanism) * strip.advance_per_unit
    // Moving the film forward slides the pattern toward higher u, so the texture offset runs back.
    texture.offset.x = -((travel / strip.pitch) % 1)
  })

  return (
    <group ref={node} visible={mode !== 'hidden'}>
      <mesh geometry={geometry} material={material} />
    </group>
  )
})
