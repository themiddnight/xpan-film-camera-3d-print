import {
  Box3, DepthTexture, FloatType, Group, Mesh, MeshBasicMaterial, MeshNormalMaterial, OrthographicCamera, PlaneGeometry,
  Scene, ShaderMaterial, SRGBColorSpace, Vector2, Vector3, WebGLRenderer, WebGLRenderTarget, type Object3D,
} from 'three'
import { MANIFEST_URL } from '../manifest'
import { gltfToWorld } from '../scene/frames'
import { loadPart } from '../scene/partLoader'
import type { Manifest, PartManifest } from '../types'
import { drawingSize, PAD_MM, projectedSizeMm, PX_PER_MM, SS, VIEW_DIRECTION } from './partDrawing'
import { inventory } from './parts'

/** The ink sits where the depth of the white pass bends or where the normals turn. Widths are in drawn pixels. */
const INK_WIDTH_PX = 2.2
const DEPTH_BEND = 0.004
const NORMAL_TURN = 0.45
/** The render path projects the real bounding box; the manifest size must agree with it to this many mm. */
const SIZE_TOLERANCE_MM = 0.05
const CAMERA_DISTANCE_MM = 2000

const composite = new ShaderMaterial({
  uniforms: {
    tColor: { value: null },
    tNormal: { value: null },
    tDepth: { value: null },
    texel: { value: new Vector2() },
    width: { value: INK_WIDTH_PX },
    depthBend: { value: DEPTH_BEND },
    normalTurn: { value: NORMAL_TURN },
  },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
  fragmentShader: `
    uniform sampler2D tColor, tNormal, tDepth;
    uniform vec2 texel;
    uniform float width, depthBend, normalTurn;
    varying vec2 vUv;
    void main(){
      vec3 c = texture2D(tColor, vUv).rgb;
      float d0 = texture2D(tDepth, vUv).r;
      vec3 n0 = texture2D(tNormal, vUv).rgb;
      float ink = 0.;
      for (int i = 0; i < 4; i++) {
        float a = float(i) * 0.785398;
        vec2 o = vec2(cos(a), sin(a)) * texel * width;
        float da = texture2D(tDepth, vUv + o).r, db = texture2D(tDepth, vUv - o).r;
        // A plane has linear depth in an orthographic view, so its second difference is zero.
        ink = max(ink, step(depthBend, abs(da + db - 2. * d0)));
        ink = max(ink, step(normalTurn, length(texture2D(tNormal, vUv + o).rgb - n0)));
        ink = max(ink, step(normalTurn, length(texture2D(tNormal, vUv - o).rgb - n0)));
      }
      gl_FragColor = vec4(mix(c, vec3(0.), ink), 1.);
    }`,
})

const whiteFaces = new MeshBasicMaterial({ color: 0xffffff })
const normals = new MeshNormalMaterial()

/** A full-screen quad that draws the ink over the white pass; one renderer and its targets serve every part. */
function createDrawer() {
  const renderer = new WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, alpha: false })
  renderer.setPixelRatio(1)
  renderer.outputColorSpace = SRGBColorSpace
  const colorTarget = new WebGLRenderTarget(1, 1)
  const normalTarget = new WebGLRenderTarget(1, 1, { depthTexture: new DepthTexture(1, 1, FloatType) })
  composite.uniforms.tColor.value = colorTarget.texture
  composite.uniforms.tNormal.value = normalTarget.texture
  composite.uniforms.tDepth.value = normalTarget.depthTexture
  const quad = new Scene()
  quad.add(new Mesh(new PlaneGeometry(2, 2), composite))
  const quadCamera = new OrthographicCamera(-1, 1, 1, -1, 0, 1)

  return {
    dispose() {
      renderer.dispose()
      colorTarget.dispose()
      normalTarget.dispose()
    },
    /** The PNG data URL of `model` seen through `camera`, `width` x `height` pixels. */
    draw(model: Object3D, camera: OrthographicCamera, width: number, height: number): string {
      renderer.setSize(width, height, false)
      colorTarget.setSize(width, height)
      normalTarget.setSize(width, height)
      const scene = new Scene()
      scene.add(model)
      scene.background = null
      scene.overrideMaterial = whiteFaces
      renderer.setClearColor(0xffffff, 1)
      renderer.setRenderTarget(colorTarget)
      renderer.render(scene, camera)
      scene.overrideMaterial = normals
      renderer.setClearColor(0x000000, 1)
      renderer.setRenderTarget(normalTarget)
      renderer.render(scene, camera)
      renderer.setRenderTarget(null)
      composite.uniforms.texel.value.set(1 / width, 1 / height)
      renderer.render(quad, quadCamera)
      scene.remove(model)
      return renderer.domElement.toDataURL('image/png')
    },
  }
}

async function loadInWorld(part: PartManifest, glbUnitScale: number): Promise<Object3D> {
  const url = new URL(part.glb, MANIFEST_URL).href
  const loaded = await loadPart(part.name, url)
  if (loaded instanceof Error) throw new Error(`Part ${part.name} did not load from ${url}: ${loaded.message}`)
  const holder = new Group()
  holder.matrixAutoUpdate = false
  holder.matrix.copy(gltfToWorld(glbUnitScale))
  holder.add(loaded)
  holder.updateMatrixWorld(true)
  return holder
}

/**
 * The camera for a part: the shared isometric direction, framed on the part's centre at the size
 * `drawingSize` gives. Throws when the part's real bounding box projects to another size than its
 * manifest `placed_size_mm`, because then the card and the picture would disagree.
 */
function frameCamera(part: PartManifest, model: Object3D): { camera: OrthographicCamera; width: number; height: number } {
  const box = new Box3().setFromObject(model)
  const world = box.getSize(new Vector3())
  const real = projectedSizeMm([world.x, world.y, world.z])
  const expected = projectedSizeMm(part.placed_size_mm)
  if (Math.abs(real.width - expected.width) > SIZE_TOLERANCE_MM || Math.abs(real.height - expected.height) > SIZE_TOLERANCE_MM) {
    throw new Error(`${part.name}: the model projects to ${real.width.toFixed(2)} x ${real.height.toFixed(2)} mm but placed_size_mm says ${expected.width.toFixed(2)} x ${expected.height.toFixed(2)} mm`)
  }
  const centre = box.getCenter(new Vector3())
  const camera = new OrthographicCamera()
  camera.up.set(0, 0, 1)
  camera.position.copy(centre).addScaledVector(new Vector3(...VIEW_DIRECTION).normalize(), CAMERA_DISTANCE_MM)
  camera.lookAt(centre)
  camera.updateMatrixWorld(true)

  // The part's centre is the picture's centre, so the picture spans half the drawn size either way.
  const size = drawingSize(part.placed_size_mm)
  const halfWidth = size.width / PX_PER_MM / 2
  const halfHeight = size.height / PX_PER_MM / 2
  const depth = (world.length() / 2) + PAD_MM
  Object.assign(camera, { left: -halfWidth, right: halfWidth, top: halfHeight, bottom: -halfHeight, near: CAMERA_DISTANCE_MM - depth, far: CAMERA_DISTANCE_MM + depth })
  camera.updateProjectionMatrix()
  return { camera, width: size.width * SS, height: size.height * SS }
}

/** Every drawn part of the inventory as a PNG data URL, keyed by manifest name. */
export async function renderPartDrawings(manifest: Manifest): Promise<Record<string, string>> {
  const drawer = createDrawer()
  const byName = new Map(manifest.parts.map(p => [p.name, p]))
  const names = inventory(manifest).flatMap(m => m.lists.flatMap(l => l.items.map(i => i.part)))
  const drawings: Record<string, string> = {}
  try {
    for (const name of names) {
      const part = byName.get(name)!
      const model = await loadInWorld(part, manifest.glb_unit_scale)
      const { camera, width, height } = frameCamera(part, model)
      drawings[name] = drawer.draw(model, camera, width, height)
    }
  } finally {
    drawer.dispose()
  }
  return drawings
}
