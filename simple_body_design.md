# Simple Body Design

**Module:** First active body module  
**Use case:** Pinhole camera body for the shared film back  
**Status:** Phase 1 review done 2026-10-21; section 7 holds the modeling values

---

## 1. Purpose

The simple body is the first body module for the camera. It provides a light-tight 50mm-depth chamber between the M42 front mount and the film plane in the shared film back.

It intentionally avoids a mirror, ground glass, and coupled shutter system.

---

## 2. Core Parameters

| Parameter | Value | Notes |
|---|---:|---|
| Pinhole-to-film distance | 50.0mm | Critical optical distance |
| Pinhole diameter | 0.30mm | In pinhole module |
| Front mount | M42 x 1mm female, from a bought M42 rear lens cap with its centre cut out, glued into the printed front plate | Printed M42 threads are unreliable on FDM |
| Film format | 65 x 24mm | Film back owns gate |
| Body-to-back lock | Top hook + bottom latch | Matches film back interface |
| Viewfinder | Foldable wire frame | Simple framing |
| Material | Black PETG | FDM |

---

## 3. Optical Layout

```
[M42 pinhole module] -> [50mm dark chamber] -> [film back gate / film plane]
```

The 50.0mm distance is measured from the pinhole plane to the film plane. The film plane belongs to the film back, so the body depth must be set from the body mating datum to the M42/pinhole module datum after the film back interface is finalized.

---

## 4. Body-to-Film-Back Interface

The simple body uses the shared film back interface:

- Top lip hooks into the film back top rail.
- Bottom latch hook catches the film back lower 3mm pin.
- Body pivots down and clamps against the film rail/body datum.
- Body does not contact cartridge or take-up chambers.

Detailed interface geometry is defined in [film_back_design.md](film_back_design.md).

---

## 5. Viewfinder

Initial viewfinder: foldable wire frame.

| Parameter | Value | Notes |
|---|---:|---|
| Rear-to-front frame distance | 80mm | Starting value |
| Front frame width | about 104mm | For 65mm width at 50mm distance |
| Front frame height | about 38mm | For 24mm height at 50mm distance |
| Rear sight | 3mm peep hole | A small hole fixes the eye position better than a 20 x 8mm frame |
| Wire diameter | 1.0-1.2mm | Steel wire |

---

## 6. Added in the Phase 1 Review

- **Tripod socket.** Pinhole exposures run from seconds to minutes, so the camera needs a 1/4"-20 socket. It is a captured 1/4"-20 hex nut in the body bottom on the optical axis, where the 50mm-deep body has room for the insert. Each future body carries its own.
- **Anti-reflection.** Three internal baffle ribs plus matte black paint or flocking. Light that hits the chamber wall at a grazing angle otherwise fogs the frame edges.

## 7. Modeling Parameters (v02 baseline)

Same origin and axes as [film_back_design.md](film_back_design.md) section 17: film plane at Y = 0, +Y toward the pinhole.

| Item | Value |
|---|---:|
| Rear face (contacts the film-back datum) | Y = +4.20 |
| Rear footprint | X = +/-39, Z = -29.0 to +26.5 (1mm inside the bridge span and the shell bottom; the top stays below the film-back hook) |
| Top tongue | 1.4mm thick (Y = +4.5 to +5.9), rises to Z = +29.7 inside the film-back hook slot, X = +/-34; 0.3mm clearance each side |
| Bottom latch | A notch in the body's rear-bottom corner (Z = -29 to -21, Y = +4.2 to +13, X = +/-25) clears the film-back lugs and pin. A PETG cantilever 18mm long, 2.0mm thick, 8mm wide runs along the notch floor (Z = -29 to -27) from Y = +29 back to its free end at Y = +10. A 1.2mm hook on the free end rises in front of the pin, and its rear face bears on the pin's front, so the body cannot pull away from the datum (strain about 1.1%). While the body swings in, the hook ramps over the pin and the cantilever flexes 1.2mm downward, below the body bottom. Press the free end down to release |
| Walls | 2.5mm |
| Chamber at the rear | 69 x 28mm inside, tapering to the M42 bore at the front |
| Baffle ribs | Three, 1.5mm thick, at Y = +15, +27, +39, openings 1mm outside the image cone |
| Pinhole plane | Y = +50.0 (+/-0.3) |
| Tripod socket | Stainless 1/4"-20 hex nut captured in a printed hex pocket, 14mm boss, body bottom, X = 0. No 1/4"-20 heat-set insert is sold on Lazada TH |
| Viewfinder | 1.0mm steel wire front frame 104 x 38.4mm, 80mm ahead of a 3mm rear peep, folds flat on two printed hinge blocks |

M42 mount values: see section 8.

## 8. M42 Mount From Bought Caps

M42 caps are sold as a pair (body cap + rear lens cap) for about ฿39-50 on Lazada TH. A rear lens cap has the female thread, because it screws onto a lens's male rear thread. A body cap has the male thread.

- **Body (female):** cut the centre out of the rear lens cap to a 36mm opening and glue the threaded ring into a printed pocket in the front plate.
- **Pinhole module (male):** the body cap, drilled through, carries the pinhole and the printed shutter (see [lens_design.md](lens_design.md)).

Neither cap's dimensions are published. Buy the pair and measure before phase 4:

| Measure | Nominal used for layout |
|---|---:|
| Rear cap ring OD | 46mm |
| Rear cap ring height | 8mm |
| Body cap flange OD | 53mm |
| Body cap stack, female seat face to pinhole plane | 2.0mm |

The female seat face sits at Y = 50.0 minus the measured cap stack (48.0 nominal). A printed shim ring under the glued ring absorbs a measured difference, so the 50.0 +/-0.3mm pinhole distance does not depend on cap tolerances. The 36mm bore lies within 10mm behind the pinhole, and the corner rays need only 7mm radius there (`tools/check_layout.py`).

Do not buy T-mount/T2 parts by mistake. T2 is also 42mm but has a 0.75mm pitch; check for "x1" or "SLR" in the listing.
