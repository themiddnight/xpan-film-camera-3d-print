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
**Pinhole Body** — dark chamber, fixed 50mm depth, M42 front mount, wire frame viewfinder
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
- **three.js** — web viewer for GLB exports, for review only.
- Whatever the tool, models stay parametric: named variables at the top, no magic numbers.
- **Blender** — visualization or organic shapes only; secondary tool.

---

## Design Document

`camera_design.md` is the system-level source of truth. Detailed module design is split into:
- `film_back_design.md` — film transport, gate, dark slide, body interface, and sprocket lock
- `simple_body_design.md` — simple 50mm-depth pinhole body
- `lens_design.md` — M42 pinhole module and future lens module notes

---

## Instructions for agents

- **Design first, model later** — finalize all dimensions and mechanisms before opening any CAD tool
- If uncertain about camera mechanics, film standards, or optical principles — **search the web before answering**
- Key film standard: 135 perforation pitch = 4.750mm (KS-1870)
- Prefer simple and proven mechanisms over clever and complex ones
- Always model parametrically (variables at top, no magic numbers)
