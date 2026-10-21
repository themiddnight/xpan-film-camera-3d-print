import { MathUtils, Matrix4, Vector3 } from 'three'
import type { Drive } from '../types'

/** A drive with its axis normalised and its angle in radians, ready to apply every frame. */
export type CompiledDrive =
  | { kind: 'rotate'; axis: Vector3; origin: Vector3; radians: number }
  | { kind: 'slide'; offset: Vector3 }

export function compileDrive(d: Drive): CompiledDrive {
  const axis = new Vector3().fromArray(d.axis).normalize()
  switch (d.kind) {
    case 'rotate':
      return { kind: 'rotate', axis, origin: new Vector3().fromArray(d.origin), radians: MathUtils.degToRad(d.amount) }
    case 'slide':
      return { kind: 'slide', offset: axis.multiplyScalar(d.amount) }
    default: {
      const _exhaustive: never = d
      return _exhaustive
    }
  }
}

const rotated = new Vector3()

/** Writes into `out` the transform of this drive at `value` (0 to 1), in camera mm. */
export function driveMatrix(out: Matrix4, d: CompiledDrive, value: number): Matrix4 {
  switch (d.kind) {
    case 'slide':
      return out.makeTranslation(d.offset.x * value, d.offset.y * value, d.offset.z * value)
    case 'rotate': {
      out.makeRotationAxis(d.axis, d.radians * value)
      // Rotating about a point o is R(p - o) + o, so the translation is o - R o.
      rotated.copy(d.origin).applyMatrix4(out)
      return out.setPosition(d.origin.x - rotated.x, d.origin.y - rotated.y, d.origin.z - rotated.z)
    }
    default: {
      const _exhaustive: never = d
      return _exhaustive
    }
  }
}
