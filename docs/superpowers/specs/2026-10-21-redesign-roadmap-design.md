# Redesign Roadmap: First Working Pinhole Camera

**Date:** 2026-10-21
**Status:** Approved in chat 2026-10-21

## 1. Why this roadmap exists

The v01 OpenSCAD models never reached a usable state and were removed. They failed because the whole
film back was written in one pass and never rendered or printed. A sprocket-pitch error (film wrapped
on the tooth body instead of the pitch circle, 3.04mm short per frame) survived until a late review.
OpenSCAD is no longer available.

This roadmap restarts the CAD work. It fixes what the round produces, in what order, and how each step
is checked, before any modeling begins.

## 2. Goal and success

**Goal:** a complete, digitally verified, print-ready design for a pinhole camera that shoots
65 x 24mm frames on 135 film: shared film back + simple 50mm body + M42 pinhole module.

**This round is done when:**

- Every printed part exists as a parametric build123d model, exported as STL and STEP.
- Every part fits within 180 x 180mm in its print orientation.
- All automated checks in section 6 pass on the final assembly.
- A BOM lists every non-printed part with a size that can actually be bought.
- A print package gives part list, print settings, print order (test coupons first) and assembly steps.

**Out of scope for this round** (the user does these once a printer is available): printing,
assembly, light-leak testing, the first film roll, and tuning from physical results. The optical lens
module and the mirror/WLF lens body also stay out of scope; the M42 interface keeps room for them.

## 3. Decisions taken in the planning session

| Decision | Choice | Reason |
|---|---|---|
| Baseline | Keep the existing design docs and locked parameters as the baseline; review only the risky or unfinished parts | The architecture is sound; the failure was in execution and verification |
| Round target | Working pinhole camera | Smallest complete camera; avoids lens coverage risk |
| Workflow | Design and preview fully on the computer, print later (approach B), using bought parts wherever printing is weak (approach C) | No printer yet; the user prefers one complete design pass |
| Printer | Unknown, so every part must fit 180 x 180mm | Covers nearly all common printers and print services |
| CAD tool | build123d (Python), written by the agent | Parametric like OpenSCAD, real B-rep with fillets and STEP export, scriptable checks |
| Preview | three.js web viewer loading GLB exports | Interactive review for the user; the agent screenshots the same page to check its own work |

Locked parameters from [docs/design/camera.md](../../design/camera.md) stay unchanged unless phase 1
finds one wrong; any change is logged in that file's decision log.

## 4. Risk handling without early prints

Some properties cannot be proven on screen: tooth fit in real perforations, FDM tolerance on the
user's printer, spring force, and light leaks. The plan handles them in two ways:

1. **Heavier digital verification than v01** (section 6): real renders, interference checks,
   clearance and wall checks, and mechanism math measured from the model geometry.
2. **Every printer-dependent value is a named parameter** (hole clearance, tooth size, latch
   interference, thread or bore fit). The print package starts with small test coupons for these
   values. A bad fit means editing one parameter and re-exporting.

## 5. Phases

| Phase | Work | Output |
|---|---|---|
| 1. Design review and sourcing | Review risky and unfinished items in the module docs. Fill every dimension a printed part needs. Research off-the-shelf parts with standard sizes (M2/M3 screws and inserts, 3-4mm steel shafts or dowel pins, compression and torsion springs, ready-made M42 parts such as extension tubes or adapter rings, 0.1mm brass shim, dark slide sheet, light-seal velvet or foam). Design around sizes that can be bought. | Updated design docs; `docs/bom.md` with part, size, search terms or example source, approximate price |
| 2. Tooling | build123d project: shared parameter module, one module per part, assembly, export script, check script, three.js viewer page | Viewer showing a trial part; check script that catches a seeded error |
| 3. Film back | Model all film-back parts and its assembly. Done 2026-10-22 ([plan](2026-10-22-phase3-4-parts.md)) | Models + check report |
| 4. Body and pinhole module | 50mm dark chamber, M42 mount, body latch, wire-frame viewfinder, pinhole holder, sliding shutter. Done 2026-10-22 | Models + check report |
| 5. Full assembly review | Exploded view, section views, light path, mechanism motion. Optional `/anatomy` explainer figures of the transport and lock. | Review renders and viewer states |
| 6. Print package | Per-part STL and STEP, print orientation and settings, print order starting with test coupons, assembly guide | `out/` export set + print and assembly guide |

Each phase ends with its checks passing and a local commit.

## 6. Verification

Automated checks run from one command and report pass/fail per item:

- **Interference:** no two solids in the assembled state overlap, except intended press fits listed
  by name.
- **Clearances:** every rotating shaft and bore pair meets its named clearance parameter.
- **Mechanism math from geometry:** film path length over one sprocket revolution equals 66.5mm
  within 0.05mm, measured on the pitch circle of the modeled sprocket.
- **Optical distance:** pinhole plane to film plane equals 50.0mm within 0.3mm in the assembled model.
- **Gate:** the gate opening is 65.0 x 24.0mm and sits centered on the film path.
- **Printability:** minimum wall 1.2mm (or the named exception), every part within 180 x 180mm in its
  print orientation.
- **Light path:** no straight line exists from outside into the film chamber except through the
  pinhole (checked on section views of the seams, slot and shaft passages).

Visual checks: the agent opens the three.js viewer in the browser and inspects screenshots of each
part, the assembly, the exploded view and the sections before calling a phase done.

## 7. Repository layout

Revised 2026-10-21 after phase 2: documents moved under `docs/`, and the viewer became a Vite + React + react-three-fiber app.

```
docs/
  design/         camera.md, film-back.md, simple-body.md, lens.md
  research/       background research
  images/         reference photos and sketches
  bom.md          bought parts
  superpowers/    specs and plans
cad/              build123d source
  params.py       every shared dimension and tunable fit value
  parts/          one module per printed part, plus the registry that places them
  export.py       writes STL, STEP and GLB to out/
  checks.py       automated checks from section 6
  tests/          seeded-error tests for the checks
viewer/           Vite + React + react-three-fiber viewer (loads out/manifest.json)
out/              generated exports (rebuilt by export.py; gitignored until phase 6,
                  which commits the final print set)
```

The coordinate convention from [camera.md](../../design/camera.md) applies to all CAD code: X is film travel from
cartridge to take-up, +Y is the front/body side.
