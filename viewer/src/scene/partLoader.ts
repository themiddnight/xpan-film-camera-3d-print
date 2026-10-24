import type { Object3D } from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const loads = new Map<string, Promise<Object3D | Error>>()

/**
 * Loads a part GLB once per page, however many views show it; each view clones the scene graph and
 * shares the geometry. A failed load resolves to its Error instead of throwing, because a missing part
 * is an expected outcome the scene renders around, not a render error. It is logged here, once.
 */
export function loadPart(name: string, url: string): Promise<Object3D | Error> {
  let load = loads.get(url)
  if (!load) {
    load = new GLTFLoader().loadAsync(url).then(
      gltf => gltf.scene,
      (e: unknown) => {
        const error = e instanceof Error ? e : new Error(String(e))
        console.error(`Part ${name} failed to load from ${url}:`, error.message)
        return error
      },
    )
    loads.set(url, load)
  }
  return load
}
