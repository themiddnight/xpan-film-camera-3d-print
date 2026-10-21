# Lens Design

**Module:** Lens and pinhole module design notes  
**Status:** Pinhole module active; optical lens module future/research  
**Shared mount:** M42 x 1mm male module into M42 x 1mm female body

---

## 1. Module Strategy

All front optical modules use the same M42 interface. This lets the camera start as a pinhole camera and later accept lens modules without changing the film back.

```
[front optical module] -> [M42 body mount] -> [body chamber] -> [film back]
```

---

## 2. Active First Module: M42 Pinhole Module

The first working module should be the pinhole module because it is the simplest optical system and avoids image circle, focus, and lens correction risk.

| Parameter | Value | Notes |
|---|---:|---|
| Mount | M42 x 1mm male | Screws into simple body |
| Pinhole diameter | 0.30mm | For 50mm pinhole-to-film distance |
| Pinhole plate | 0.1mm brass shim | Hand-drilled or laser-drilled |
| Shutter | Sliding blade | Simple manual exposure |
| Blade material | Thin brass or spring steel | Not printed |
| Safety | Mechanical catch/lever | Prevent accidental exposure |

---

## 3. Pinhole Optical Reference

| Parameter | Value |
|---|---:|
| Pinhole-to-film distance | 50.0mm |
| Frame size | 65 x 24mm |
| Horizontal FOV | about 66 deg |
| Vertical FOV | about 27 deg |
| Diagonal FOV | about 69 deg |
| f-number | about f/167 |

---

## 4. Future Lens Module Direction

Future lens modules must cover the 65 x 24mm frame diagonal of 69.3mm.

Possible architectures:

- Fixed-focus lens module
- Zone-focus barrel
- Off-the-shelf M42 iris module
- DIY leaf shutter if the lens does not include a shutter
- Better corrected enlarger or medium-format taking lens

The lens module should remain removable so lens experiments do not affect the film back.

---

## 5. Known Research Notes

Earlier research considered enlarger lenses and simple biconvex lenses. The useful conclusion is:

- A lens needs an image circle of at least 69.3mm.
- Simple single-element lenses are likely to have severe field curvature over this wide frame.
- Enlarger lenses around 60-80mm are more plausible candidates.
- Exact lens choice remains open and should be tested before a lens body is modeled.

---

## 6. Deferred Details

- Exact lens element choice.
- Focus mechanism.
- Aperture module.
- Leaf shutter mechanism.
- Lens body with mirror/ground glass.

