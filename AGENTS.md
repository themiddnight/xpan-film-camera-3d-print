# X-Pan Film Camera — Project Brief

## What is this project?

DIY wide panoramic film camera shooting **65×24mm frames on standard 135 (35mm) film**, matching the Hasselblad X-Pan format (2.7:1 aspect ratio). The camera is **modular** — a shared film back combines with interchangeable body modules (pinhole or lens) to form a complete camera.

Goal: a camera that works correctly, is mechanically accurate, and is practical to build and use.

---

## Modular Architecture

```
[Lens Module]  ←→  [Body Module]  ←→  [Film Back]
  M42 mount         dark chamber        film transport
  (optical)         + viewfinder        + film gate
```

| Layer | Responsibility |
|---|---|
| **Lens Module** | Optical element, focus, aperture — or pinhole + shutter |
| **Body Module** | Dark chamber, viewfinder, optional mirror/shutter |
| **Film Back** | Film gate, sprocket counting, supply/take-up spools |

### Film Back (shared)
- Supply cartridge chamber (left) + rewind knob
- Film gate: 65×24mm, with dark slide slot
- Sprocket counter + auto-lock (14 perf = 1 frame)
- Take-up spool + advance knob (right)

### Body Modules (attach to film back)
**Pinhole Body** — dark chamber, fixed 50mm depth, M42 front mount, folding two-frame viewfinder
**Lens Body** — dark chamber, mirror box, ground glass WLF, leaf shutter, M42 front mount

### Lens Modules (M42, interchangeable)
**Pinhole Module** — M42 cap + 0.30mm brass pinhole + sliding blade shutter + safety lever
**Lens Module** — helicoid + aperture iris + lens element (TBD)

---

## Key Specifications (locked)

| Parameter | Value |
|---|---|
| Frame size | 65 × 24mm |
| Perforation pitch | 4.750mm (KS-1870) |
| Perforations per frame | 14 |
| Film advance per frame | 66.5mm exactly (set by tooth count, 1.5mm gap between frames) |
| Sprocket pitch Ø | 21.17mm (film-contact hub Ø 21.04 = pitch Ø − film thickness) |
| Sprocket teeth | 14 (1 rev = 1 frame) |
| Frames per 36-exp roll | about 19-20 (XPan gets 21) |
| Lens mount | M42 × 1mm pitch |
| Pinhole diameter | 0.30mm |
| Pinhole-to-film distance | 50.0mm |
| Material | PETG black, FDM |

---

## Software Stack

- **build123d (Python)** — primary tool for all mechanical parts, chosen 2026-10-21 (see `docs/superpowers/specs/2026-10-21-redesign-roadmap-design.md`). The earlier OpenSCAD models were removed; OpenSCAD is no longer available.
- **Vite + React + react-three-fiber** (`viewer/`) — web viewer for GLB exports, for review only. Dependencies are pinned; pnpm's minimum release age policy stays on.
- Whatever the tool, models stay parametric: named variables at the top, no magic numbers.
- **Blender** — visualization or organic shapes only; secondary tool.

### Working with the CAD

Run these from the repository root. `uv sync` installs build123d into `.venv` (Python 3.12).

| Command | What it does |
|---|---|
| `uv run python cad/export.py` | Builds every part in `cad/parts/`, writes `out/stl` (print orientation), `out/step` and `out/glb` (camera coordinates) and `out/manifest.json` |
| `uv run python cad/checks.py` | Layout checks from `cad/params.py` plus geometry checks on the built solids; exit 1 on any failure |
| `uv run python cad/tests/test_checks.py` | Seeds known design errors and proves the checks catch each one |
| `pnpm --dir viewer install` (once), then `pnpm --dir viewer dev` | Serves two pages on `http://localhost:8642/`. `/` is the presentation (public page: the scroll-driven showcase). `/workshop.html` is the private review viewer reading `out/`: the whole camera with part toggles by group and kind, ghosting, section planes and exploded view; **Operate** plays one frame advance (button or Space, Loop, Show mechanism cutaway and camera) with the film moving on its path; a play/scrub slider for each mechanism |
| `pnpm --dir viewer typecheck` | Typechecks the viewer (`tsc --noEmit`) |
| `pnpm --dir viewer test` | Runs the vitest tests: manifest parsing and the story validator, which reads the real `out/manifest.json` (run the export first) |
| `pnpm --dir viewer build` | Typechecks and builds both pages into `viewer/dist/` (private; includes all of `out/`) |
| `pnpm --dir viewer build:public` | Builds the presentation alone into `viewer/dist-public/` with only `manifest.json`, `glb/` and `stills/` from `out/`, then `scripts/check-public.mjs` fails if the workshop page, workshop code or any STL/STEP file got in |
| `node docs/figures/film-transport/build.mjs` | Writes the film-transport figure pages (add `--light` for the light page, `--audit` to check the geometry); needs the anatomy skill (`ANATOMY_HOME`, default `~/.claude/skills/anatomy`) |

- The viewer only reads `out/manifest.json` and `out/glb/`. Run the export first; the dev server picks up new files on reload. Workshop-only code lives in `viewer/src/workshop/`; `scene/`, `state/`, `manifest.ts` and `types.ts` are shared with the presentation in `viewer/src/presentation/`.
- Every dimension lives in `cad/params.py`. `Fit` holds printer-dependent values; `Measured` holds values to confirm on bought parts. Do not put numbers in part files.
- Each module in `cad/parts/` exports `PARTS` (a `PartSpec` per part: build, assembled placement, group, printed or bought, print rotation); `cad/parts/__init__.py` merges them. Add geometry checks for anything a part must get right in `cad/check_areas/<area>.py`, each with a seeded error in `cad/tests/test_<area>.py`.
- `cad/mechanisms.py` holds the moving systems the viewer animates and the frame-advance cycle, all derived from params. `cad/checks.py` holds the assembly checks: no overlaps beyond the named fits in `INTENDED_OVERLAPS`, every printed part on the 180mm bed, and the lock and ride checks.
- `out/` is generated and gitignored until the final print package.

---

## Design Document

`docs/design/camera.md` is the system-level source of truth. Detailed module design is split into:
- `docs/design/film-back.md` — film transport, gate, dark slide, body interface, and sprocket lock
- `docs/design/simple-body.md` — simple 50mm-depth pinhole body
- `docs/design/lens.md` — M42 pinhole module and future lens module notes

Other documents: `docs/bom.md` (bought parts), `docs/research/` (background research; the optics study uses an older 60x24mm frame), `docs/images/` (reference photos and sketches), `docs/superpowers/specs/` (roadmap and specs).

### Repository layout

| Path | Contents |
|---|---|
| `docs/` | Design docs, BOM, research, images, specs |
| `cad/` | build123d source: `params.py`, `parts/`, `export.py`, `checks.py`, `tests/` |
| `viewer/` | Vite + React + react-three-fiber viewer for the GLB exports |
| `out/` | Generated exports (gitignored) |

---

## Instructions for agents

- **Design first, model later** — finalize all dimensions and mechanisms before opening any CAD tool
- If uncertain about camera mechanics, film standards, or optical principles — **search the web before answering**
- Key film standard: 135 perforation pitch = 4.750mm (KS-1870)
- Prefer simple and proven mechanisms over clever and complex ones
- Always model parametrically (variables at top, no magic numbers)
