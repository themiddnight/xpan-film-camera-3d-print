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
- `count: int = 1`. Pieces one solid stands for (each viewfinder pins solid models two hinge stubs).
- `inventory: bool = True`. False for what loads into the camera rather than being part of it
  (cassette, film, film roll).
- Rule in `__post_init__`: an inventory part that is not printed needs `bom`; a printed part must not
  have one.

`cad/export.py` writes `bom`, `count` and `inventory` into each manifest part.

Assignments:

| Part | Kind | BOM |
|---|---|---|
| hinge_pin, latch_pin, sprocket_pin, takeup_shaft, rewind_shaft, pawl_pin, shutter_lock_pivot, viewfinder_rear_pins (×2), viewfinder_front_pins (×2) | stock | 1 |
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

- `types.ts` and `manifest.ts`: `KINDS` gains `stock`; parts carry `bom: string | null`, `count`,
  `inventory`. The workshop kind filter picks up the third value from `KINDS`.
- `presentation/parts.ts`: pure `inventory(manifest)` returns modules in `GROUPS` order, each with
  three kind lists in the order printed, stock, bought. It drops `inventory: false` parts, merges a
  `<base>_left`/`<base>_right` pair into one item named `<base>` whose count is the sum, and makes a
  display name from the snake-case name (first letter capitalised: `m42_rear_cap_ring` reads
  "M42 rear cap ring"). Each item keeps the manifest name of its first member for its thumbnail, its
  largest dimension in mm, and its `bom`.
- `bom.ts`: `BomRow` gains `id` from the `#` column; `BomTable` gives each row `id="bom-<id>"`.
- `PartsInventory.tsx`: one block per module with a heading and a count line, then a card grid per kind
  (Print, Make from stock, Buy). A card shows the thumbnail, the name, `×N` when N > 1, the largest
  dimension, and for stock and bought parts a link `BOM #<id>` to `#bom-<id>`. Images are lazy and sized.
  No WebGL on the page.
- `maker.ts`: a `{{parts}}` block. `content/parts.md` holds the section; `DOCS` lists it before `bom`.
  `content/bom.md` no longer claims everything else is printed without showing it.

## Thumbnails

- `?part=<manifest name>` renders that one part through the still pipeline: the same isometric direction
  for every part, framed on the part alone, all others hidden, `window.stillReady` when drawn.
- `pnpm stills` also writes `out/stills/parts/<name>.png` at 320 x 320 for every inventory part.
  The deploy already copies `out/stills/`.
- Every thumbnail fills its frame, so sizes come from the mm figure on the card, not the picture.

## Tests and checks

- Python: the kind/bom rule raises on a printed part with `bom` and on a stock part without one.
- Vitest on the real manifest: module and kind counts, the left/right merge, no film or cassette, every
  `bom` resolves to a row of `docs/bom.md`.
- `verify.mjs`: every inventory thumbnail exists in `dist-public/stills/parts/`, the Parts images load,
  no sideways scroll at 1440 and 375.
