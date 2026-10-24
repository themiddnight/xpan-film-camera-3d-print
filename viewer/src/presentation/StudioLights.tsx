import { useLayoutEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { PMREMGenerator, type Texture, type WebGLRenderer } from 'three'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'

/** One prefiltered studio room per renderer, shared by every view on the canvas. */
const rooms = new WeakMap<WebGLRenderer, Texture>()

function studioRoom(gl: WebGLRenderer): Texture {
  let room = rooms.get(gl)
  if (!room) {
    const pmrem = new PMREMGenerator(gl)
    const scene = new RoomEnvironment()
    room = pmrem.fromScene(scene, 0.04).texture
    scene.dispose()
    pmrem.dispose()
    rooms.set(gl, room)
  }
  return room
}

/**
 * Lighting for dark PETG on the light seamless. Black plastic shows its form mostly through
 * reflections, so a soft studio room lights every face and its edges catch the room's panels; one key
 * light from the upper left front separates the top faces from the sides.
 */
export function StudioLights() {
  const gl = useThree(s => s.gl)
  const scene = useThree(s => s.scene)
  useLayoutEffect(() => {
    scene.environment = studioRoom(gl)
    return () => { scene.environment = null }
  }, [gl, scene])
  return <directionalLight position={[-150, 200, 300]} intensity={1.2} />
}
