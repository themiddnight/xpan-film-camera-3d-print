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
| Handles | Two printed push tabs, one glued on each end of the blade | Push the -X tab in to open, the +X tab in to close; 3.5mm along X, 20.5mm tall; slide 10mm |
| Travel stops | Stadium slot in the blade around the lock pivot pin | Stops the blade at closed and at 10mm open, and keeps it captive |
| Safety | Captive lock lever on top of the housing, on a pressed 3.0mm steel pin, with a click detent | Positive lock in a bag; nothing to remove |

### 2.1 Shutter operation

Every move is a push. Nothing has to be gripped and pulled.

To open, push the lock lever's thumb pad, on top of the housing, toward +X until it clicks (25
degrees). Then push the -X tab in toward the housing until it stops. The blade's 4mm hole is then on
the pinhole. To close, push the +X tab in until it stops, then push the pad back (-X) until it
clicks. Seen from the front, opening is two pushes in one direction and closing is two pushes in the
other.

The state reads by feel. With the shutter closed, the -X tab stands 14mm past its housing edge and
the +X tab 4mm. With it open, the two swap. The tab that stands out is always the one to push next.
The near-flush tab stops 0.5mm off the housing, so the stop pin, not the tab, ends the travel.

The blade is a 23mm tall middle that never leaves the housing, with a 17.5mm tall tongue out of
each end. Each tongue is glued into a 2.3mm deep slit in its tab. The lever's 4mm tooth drops 2.5mm
into a notch in the top edge of the -X tongue, 2mm clear of the housing edge. The pivot sits 7.5mm
above the pinhole, level with the middle of that engagement, so a push on the -X tab loads the tooth
straight through the pivot and cannot turn the lever: the lock holds by shape, not friction. The
notch is outside the housing only while the shutter is closed, and with the shutter open the -X tab
sits under the tooth, so the lever cannot be locked with the shutter open. Unlocked, the tooth swings
up clear of the tongue and of the tab that slides under it.

The same pin carries the blade's stop slot. The thumb pad stands on a flag 12.5mm above
the pivot, below the finder's field: the finder check holds every part 0.5mm clear of its sight
lines.

The lever stays where it is put. An arc spring finger on the lever clicks into one of two notches in
a printed rail on the housing face, 0.4mm deep, at the locked and unlocked positions. A printed cap
pressed and glued on the pivot tip keeps the lever on. The pivot is a 9mm length of the 3mm rod,
pressed into both housing plates, with its rear end on the body cap face.

A bump on the blade channel's rear face meets a dimple hole in the blade at closed and at open. It
clicks only when the blade is pressed rearward, so the lock, not the bump, keeps the shutter shut.

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

