# Parts inventory section: design

Approved in chat on 2026-10-26.

## Goal

The maker half of the presentation gets a **Parts** section that shows every piece of the camera, grouped
by module (film back, body, pinhole) and, inside each module, by how a builder gets it: print it, make it
from stock in the bill of materials, or buy it ready-made. It is a flat inventory, not a 3D view. It sits
just before the Bill of materials section.

## Data: CAD is the source

`cad/parts/spec.py`:

- `Kind = Literal["printed", "stock", "bought"]`. `stock` is a piece cut, drilled or trimmed from a BOM
  material (rod, sheet, shim, felt, foam, velvet). `bought` is a ready-made piece.
- `bom: str | None`. The `#` of the `docs/bom.md` Parts row it comes from, such as `"1"` or `"7b"`.
- `inventory: bool = True`. False for what loads into the camera rather than being part of it
  (cassette, film, film roll).
- Rule in `__post_init__`: an inventory part that is not printed needs `bom`; a printed part must not
  have one.

`cad/export.py` writes `bom` and `inventory` into each manifest part.

Assignments:

| Part | Kind | BOM |
|---|---|---|
| hinge_pin, latch_pin, sprocket_pin, takeup_shaft, rewind_shaft, pawl_pin, shutter_lock_pivot, viewfinder_{rear,front}_pin_left/right | stock | 1 |
| pinhole_shim | stock | 3 |
| dark_slide, shutter_blade | stock | 4 |
| felt_washer | stock | 9 |
| pressure_pad | stock | 11 |
| slot_velvet | stock | 19 |
| m42_rear_cap_ring, m42_body_cap | bought | 2 |
| m3_insert_left/right | bought | 5 |
| m3_screw_left/right | bought | 6 |
| pawl_spring | bought | 7 |
| clutch_spring | bought | 7b |
| tripod_nut | bought | 8 |
| rewind_o_ring | bought | 13 |
| cassette, film, film_roll | bought, `inventory=False` | none |

Every other part stays printed.

## Viewer

- `types.ts` and `manifest.ts`: `KINDS` gains `stock`; parts carry `bom: string | null` and
  `inventory`. The workshop kind filter picks up the third value from `KINDS`.
- `presentation/parts.ts`: pure `inventory(manifest)` returns modules in `GROUPS` order, each with
  three kind lists in the order printed, stock, bought. It drops `inventory: false` parts, merges a
  `<base>_left`/`<base>_right` pair into one item named `<base>` that counts its members, and makes a
  display name from the snake-case name (first letter capitalised: `m42_rear_cap_ring` reads
  "M42 rear cap ring"). Each item keeps the manifest name of its first member for its drawing, its
  largest dimension in mm, and its `bom`.
- `bom.ts`: `BomRow` gains `id` from the `#` column; `BomTable` gives each row `id="bom-<id>"`.
- `PartsInventory.tsx`: one block per module with a heading and a tally line (`30 pieces: 13 printed, 10 made from stock, 7 bought`, kinds with no pieces left out), then a wrapping row of drawings per kind
  (Print, Make from stock, Buy). An item shows the drawing, the name, `×N` when N > 1, the largest
  dimension, and for stock and bought parts a link `BOM #<id>` to `#bom-<id>`. Images are lazy and sized.
  No WebGL on the page.
- `maker.ts`: a `{{parts}}` block. `content/parts.md` holds the section; `DOCS` lists it before `bom`.
  `content/bom.md` no longer claims everything else is printed without showing it.

## Drawings

Each part is a black-ink line drawing in a true isometric view (from the front, left and above), every
part at one scale (`PX_PER_MM`, 2.2 CSS px per mm), so the shell and a pin show their real size against
each other.

- `presentation/partDrawing.ts` holds the view, the scale and the pure `drawingSize(placed_size_mm)`, the
  CSS size of a drawing. The page sets `<img width height>` from it, and the renderer draws at that size
  times `SS` (3), so the browser downsizes the picture.
- `placed_size_mm` is the part's bounding box where it sits in the camera. `size_mm` is the part as built
  and stays the size a builder reads off the caption; a part placed at an angle is larger in the camera.
- `?drawings` loads `renderPartDrawings.ts` through a dynamic import (the public bundle does not carry it),
  draws the first part of each inventory item and sets `window.partDrawings` (name to PNG data URL) and
  `window.partDrawingsReady`. It throws if a model's real bounding box projects to another size than
  `placed_size_mm`.
- `pnpm stills` loads that route once and writes `out/stills/parts/<name>.png`, removing the PNGs of parts
  no longer drawn. The deploy already copies `out/stills/`.
- Drawings stand on a shared baseline in a wrapping row per kind, with no card frames.

## Tests and checks

- Python: the kind/bom rule raises on a printed part with `bom` and on a stock part without one.
- Vitest on the real manifest: module and kind counts, the left/right merge, no film or cassette, every
  `bom` resolves to a row of `docs/bom.md`.
- `verify.mjs`: the Parts images load and each is its stated width times `SS` pixels wide,
  no sideways scroll at 1440 and 375.
