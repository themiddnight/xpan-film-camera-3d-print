# X-Pan DIY Camera - System Design

**Format:** 65 x 24mm panoramic frames on standard 135 film  
**Architecture:** Modular film back + interchangeable body modules + interchangeable M42 lens modules  
**Build method:** PETG black FDM, hand-cut metal/plastic inserts where that is simpler than printing

This document is the system-level source of truth. Detailed mechanical design lives in the module documents:

- [film_back_design.md](film_back_design.md) - shared film transport, gate, dark slide, body interface, and sprocket lock
- [simple_body_design.md](simple_body_design.md) - simple 50mm-depth body for pinhole use
- [lens_design.md](lens_design.md) - lens module and future lens-body research

---

## 1. Project Goal

Build a practical DIY panoramic 135 film camera that exposes **65 x 24mm** frames, matching the Hasselblad XPan frame format. The camera should be mechanically simple, printable on a normal FDM printer, and modular enough that the film back can be reused with different bodies.

The priority is a working, buildable camera. Simple proven mechanisms are preferred over compact or clever mechanisms.

---

## 2. Modular Architecture

```
[Lens Module]  <->  [Body Module]  <->  [Film Back]
  optical            dark chamber        film transport
  or pinhole         + viewfinder        + film gate
  M42 mount          body interface      dark slide
```

| Layer | Responsibility |
|---|---|
| Film Back | Film cartridge, 65 x 24mm gate, dark slide, internal sprocket auto-lock, take-up spool, one-piece rear cover |
| Body Module | Light-tight chamber, body-to-back lock, viewfinder, optional mirror/shutter system |
| Lens Module | Pinhole or optical lens, shutter if needed, aperture/focus if applicable |

The **film back owns the film plane**. Every body module must register against the same film rail/body interface datum.

Coordinate convention for CAD files: X is film travel from cartridge to take-up, +Y is the front/body-interface side, and low Y is the rear/loading-cover side.

---

## 3. Locked Global Parameters

| Parameter | Value | Notes |
|---|---:|---|
| Frame size | 65.0 x 24.0mm | XPan format |
| Frame diagonal | 69.3mm | sqrt(65^2 + 24^2) |
| Film type | 135 / 35mm still film | Standard cartridge |
| Perforation pitch | 4.750mm | KS-1870 pitch |
| Perforations per frame | 14 | 14 x 4.750 = 66.5mm |
| Film advance per frame | 66.5mm | Exactly 14 perforations; the tooth count sets it, so hub diameter error does not accumulate. Gap between 65mm frames is 1.5mm |
| Frames per 36-exp roll | about 19-20 | 36 x 38mm = 1368mm of image film / 66.5mm, minus loading waste. XPan gets 21 |
| Sprocket teeth | 14 | One sprocket revolution = one frame |
| Sprocket pitch diameter | 21.17mm | 66.5 / pi |
| Lens/body module mount | M42 x 1mm | Male lens module, female body mount |
| Pinhole diameter | 0.30mm | For 50mm pinhole-to-film distance |
| Pinhole-to-film distance | 50.0mm | Simple body critical depth |
| Primary material | Black PETG | FDM printed |
| Light sealing | Black velvet/felt | Used at joints, slots, door edges |

---

## 4. Active Module Set

### 4.1 Shared Film Back

Status: **active design**

The film back is the shared transport module. It contains:

- Left 135 cartridge chamber with rewind knob
- Center 65 x 24mm film gate and film rails
- Non-printed dark slide inserted from the top
- Right 14-tooth sprocket roller with one-notch cam auto-lock
- Right take-up spool driven by the advance knob through a felt friction clutch
- One-piece main film-back shell with one bottom-hinged rear cover
- Hand-cut foam pressure pad on the rear cover over the gate, plus a printed shoe on the cover that holds the film on the sprocket
- Top-hook + bottom-latch body module lock

Design detail: [film_back_design.md](film_back_design.md)

### 4.2 Simple Body

Status: **active first body**

The simple body is a dark chamber with:

- 50.0mm pinhole-to-film distance
- M42 female front mount
- Body-to-film-back hook/latch interface
- Wire-frame viewfinder

It does not include a mirror or ground glass. This keeps the first working camera simple.

Design detail: [simple_body_design.md](simple_body_design.md)

### 4.3 Pinhole Module

Status: **active first lens module**

The pinhole module is an M42 male cap containing:

- 0.30mm brass pinhole plate
- Simple sliding blade shutter
- Safety lever or latch to prevent accidental exposure

This module screws into the simple body's M42 mount.

### 4.4 Lens Module

Status: **research / future**

The lens module will use the same M42 interface. Possible approaches:

- Fixed-focus or zone-focus lens module
- Off-the-shelf M42 iris
- DIY leaf shutter if needed
- Higher-quality enlarger or taking lens if image circle covers 69.3mm

Design/research detail: [lens_design.md](lens_design.md)

### 4.5 Lens Body With Mirror / WLF

Status: **future concept**

A more advanced body may include:

- Mirror box
- Ground glass waist-level finder
- Leaf shutter coordination
- Same film back interface
- Same front M42 module mount

This is intentionally deferred until the film back and simple body are working.

---

## 5. System Interface Conclusions

### Film Back to Body

Chosen interface: **top hook rail + bottom latch pin**.

- Body hooks into the top receiving rail on the film back.
- Body pivots down until it contacts the film rail/body interface datum.
- Bottom latch hook catches a 3mm pin on the film back.
- Latch force pulls the body into the velvet-sealed rail face.
- Chambers do not act as datum surfaces.

The body must contact only the film rail/body interface area, not the cartridge or take-up chambers.

### Body to Lens Module

Chosen interface: **M42 x 1mm**.

- Body has female M42 mount.
- Lens/pinhole modules have male M42 thread.
- This allows the first pinhole module and future lens modules to share the same body standard.

---

## 6. Intentional Simplifications

These are deliberate choices for a DIY prototype:

- No frame counter in the first version.
- The take-up clutch is a felt washer and a spring, not a calibrated slip clutch; the user stops advancing when the sprocket clicks.
- Rewind uses the release button held down by a quarter-turn, not a separate rewind clutch.
- Foam pressure pad is hand-cut and stuck to the rear cover instead of printed as a calibrated spring plate.
- Dark slide is cut from 0.5mm aluminum sheet instead of printed.
- M42 threads come from bought caps, not printed threads.
- Light traps use velvet/felt rather than complex printed labyrinths everywhere.

---

## 7. Decision Log

| Date | Decision | Reason |
|---|---|---|
| 2026-04 | Frame size locked at 65 x 24mm | Matches XPan format |
| 2026-04 | 14 perforations per frame | 14 x 4.750mm = 66.5mm advance |
| 2026-04 | M42 front module standard | Simple, available, reusable |
| 2026-05 | Modular architecture | Film back can serve multiple bodies |
| 2026-05-06 | 14-tooth single sprocket | One revolution per frame; no gear reduction |
| 2026-05-06 | One-notch cam auto-lock | Simple physical stop after one sprocket revolution |
| 2026-05-06 | Direct-drive take-up spool (superseded 2026-10-21: felt clutch) | Simplest DIY build; user stops at sprocket click |
| 2026-05-06 | Rewind requires holding release (superseded 2026-10-21: quarter-turn hold) | Avoids extra one-way clutch/ratchet complexity |
| 2026-05-06 | Top hook + bottom latch body lock | Printable, secure, repeatable body registration |
| 2026-05-06 | One-piece film-back shell | Keeps film rail and chamber alignment in one printed datum |
| 2026-05-06 | One-piece bottom-hinged rear cover | Opens the full film path and chambers as one loading door |
| 2026-05-06 | Foam pressure pad, non-printed | Easier to tune by hand |
| 2026-05-06 | Dark slide as cut sheet | More durable and flatter than printed PETG |
| 2026-10-21 | v01 OpenSCAD models removed; redesign in build123d per the roadmap spec | None of the v01 models were usable |
| 2026-10-21 | Film advance is exactly 66.5mm; about 19-20 frames per 36-exp roll | Tooth count sets the advance; the old "about 67mm" and "about 14 frames" were wrong |
| 2026-10-21 | Sprocket hub 21.04mm, film on an S path with 49-63 deg wrap (about 2 teeth) and a cover-mounted shoe | Hub = pitch diameter minus film thickness; two teeth are enough when the clutch limits tension and the shoe keeps the film seated |
| 2026-10-21 | Rails on the film edge band, 1.2mm wide | Keeps rails off the perforations and the image |
| 2026-10-21 | Sprocket and cam printed as one part on a fixed 3mm pin | The notch cannot slip out of phase with the teeth |
| 2026-10-21 | Felt-washer friction clutch on the take-up spool | Without it, thumb torque goes into the perforations once the sprocket locks |
| 2026-10-21 | Quarter-turn hold on the release button for rewind | Avoids holding the button through about 20 rewind turns |
| 2026-10-21 | 3.0mm stainless rod for every shaft and pin | One stock; dowel pins are too short for the shafts |
| 2026-10-21 | M42 from a bought body cap (male) and rear lens cap (female) | Cheap, real threads; printed M42 threads are unreliable |
| 2026-10-21 | Tripod socket: captured 1/4"-20 nut in the body bottom | Pinhole exposures need a tripod; no 1/4"-20 insert is sold locally |
| 2026-10-21 | Every printed part fits 180 x 180mm; film back is 175mm wide | Printer not chosen yet |
| 2026-10-21 | Face-notch cam with a horizontal-pivot pawl lever | A vertical button press can lift only a lever on a horizontal pivot |
| 2026-10-21 | Pressure pad on the gate only, light preload | Pad drag must stay below the clutch slip force |
| 2026-10-21 | Dark slide slot gets flocked lips and a plug | The open slot mouth leads straight to the gate |

---

## 8. Build Order

1. Film back mechanism and body interface
2. Simple body and pinhole module
3. Film transport tests with scrap film
4. Light leak tests
5. First exposure tests
6. Lens module and advanced body research
