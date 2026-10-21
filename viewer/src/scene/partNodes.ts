import type { Object3D } from 'three'

/** The scene node of each loaded part, so one frame callback can move all of them. */
export class PartNodes {
  /** Increments when a node appears or goes, so the driver knows to place it. */
  version = 0
  private readonly nodes = new Map<string, Object3D>()

  set(name: string, node: Object3D | null): void {
    if (node) this.nodes.set(name, node)
    else this.nodes.delete(name)
    this.version++
  }

  get(name: string): Object3D | undefined {
    return this.nodes.get(name)
  }

  forEach(fn: (node: Object3D, name: string) => void): void {
    this.nodes.forEach(fn)
  }
}
