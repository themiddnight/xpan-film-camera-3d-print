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
| Module base | Bought M42 body cap, drilled through | Male thread without printing one |
| Pinhole plate | 0.05mm brass shim, hand-drilled | Laser-drilled pinholes are not sold in Thailand; import is optional. Thin foil keeps the hole edge sharp and cuts corner vignetting |
| Hole check | Measure under magnification or scan at 2400dpi | Target 0.30mm +/-0.03 |
| Shutter | Sliding blade in a printed housing glued to the cap front | Simple manual exposure |
| Blade material | 0.5mm aluminum, offcut of the dark slide sheet | One purchase covers both; painted matte black |
| Safety | Detent bump plus a removable 3.0mm steel locking pin | Prevents accidental exposure in a bag |

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
| Corner ray angle | 34.7 deg |
| Corner falloff (cos^4) | about 1.1 stops darker than the centre |
| Shim thickness effect | 0.1mm shim cuts about a quarter of the hole area at the corners; 0.05mm about a seventh (estimate) |

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

The pinhole body puts its M42 seat 48.0mm from the film. Standard M42 SLR lenses need 45.46mm, so a lens body must be designed for that distance; the pinhole body cannot focus an SLR lens at infinity.

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

