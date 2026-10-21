"""Build every registered part and write STL, STEP and GLB files plus a viewer manifest.

Run from the repository root: uv run python cad/export.py
STL is in print orientation; STEP and GLB are placed in camera coordinates.
"""
import json
import sys
from pathlib import Path

from build123d import Compound, Pos, Rot, export_gltf, export_step, export_stl

from mechanisms import manifest_entries
from params import CAMERA
from parts import PARTS

OUT = Path(__file__).resolve().parent.parent / "out"
GLB_LINEAR_DEFLECTION = 0.02
GLB_ANGULAR_DEFLECTION = 0.2
GLB_UNIT_SCALE = 1000  # export_gltf writes metres; the viewer multiplies back to mm


def main() -> int:
    for sub in ("stl", "step", "glb"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, spec in PARTS.items():
        part = spec.build(CAMERA)
        if not part.is_valid:
            print(f"{name}: invalid solid", file=sys.stderr)
            return 1
        if spec.print_rotation is not None:
            printed = Rot(*spec.print_rotation) * part
            export_stl(Pos(0, 0, -printed.bounding_box().min.Z) * printed, OUT / "stl" / f"{name}.stl")
        location = spec.place(CAMERA)
        placed = location * part
        export_step(placed, OUT / "step" / f"{name}.step")
        # export_gltf rotates the top-level location in place, which would leave the
        # placement translation in Z-up terms; a wrapper compound keeps it consistent.
        export_gltf(
            Compound([placed]),
            OUT / "glb" / f"{name}.glb",
            binary=True,
            linear_deflection=GLB_LINEAR_DEFLECTION,
            angular_deflection=GLB_ANGULAR_DEFLECTION,
        )
        bb = part.bounding_box()
        manifest.append({
            "name": name,
            "glb": f"glb/{name}.glb",
            "group": spec.group,
            "kind": spec.kind,
            "color": spec.color,
            "volume_mm3": round(part.volume, 1),
            "size_mm": [round(bb.size.X, 2), round(bb.size.Y, 2), round(bb.size.Z, 2)],
        })
        print(f"{name}: {part.volume:.0f} mm3, {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
    (OUT / "manifest.json").write_text(json.dumps({
        "glb_unit_scale": GLB_UNIT_SCALE,
        "film_advance_mm": CAMERA.film.advance,
        "parts": manifest,
        "mechanisms": manifest_entries(CAMERA, set(PARTS)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
