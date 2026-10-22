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
| Viewfinder | Folding front frame and optional rear sight, the eye at the rear cover | Frames the 65 x 24 field; nothing behind the camera |
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

Detailed interface geometry is defined in [film-back.md](film-back.md).

---

## 5. Viewfinder

A front frame with an optional rear sight on the body top (revised 2026-10-22). The first wire frame put a peep 33mm behind the camera's back, and its 104mm front frame stood far wider than the body.

Hold the camera against your face, with your eye at the rear cover. From there the front frame shows the 65 x 24 field at 50mm. The rear sight is a small window of the same 65:24 shape at the body's rear edge. Raise it when you want to centre your eye more exactly: its edges line up with the front frame's edges only when your eye is centred. Otherwise leave it folded. Without it, an eye 5mm off centre shifts the framing by about 7 degrees. Pressing the camera to your face fixes the eye distance to about +/-3mm, which changes the field by about +/-7%.

| Parameter | Value | Notes |
|---|---:|---|
| Field | 0.65 across, 0.24 up (tan of the half-angles) | 32.5 / 50 and 12 / 50; the checks measure it on the built frames |
| Eye point | Y = -4.73, Z = +40.4 | The rear cover's outer face: the camera rests against your face |
| Front frame | 46.32 x 17.10mm window, plane at Y = +30.9 | Window width = 1.3 x (plane - eye). It stands as far forward as its hinge can while it stays outside the field and fits the tapering body top |
| Rear sight | 26.17 x 9.66mm window, plane at Y = +15.4 | Same rule. A round peep cannot do this job: 20mm from the eye, a small hole shows only a few degrees |
| Finder axis | Z = +40.4 | The field's lower edge passes 0.26mm over the M42 body cap rim |
| Frames | Printed PETG leaves, 1.6mm thick, 1.6mm border | A hand-bent 1mm wire cannot hold the windows' corners; a printed window holds about 0.2mm |
| Hinges | Two knuckles per leaf on 3mm rod stubs pressed into a printed hinge base glued to the body top. The front knuckles sit just outside the field's corners; the rear knuckles sit outboard of the folded front frame | Nothing crosses the field |
| Detent | Two flats on each knuckle, 0.3mm inside its 6.4mm diameter: one at the bottom and one on the side the leaf folds toward. A sprung tongue in the hinge base presses a pad on the lower flat | Each leaf clicks into its raised and folded positions. The flat on the pad holds the raised leaf square |
| Fold | The rear sight folds forward, the front frame folds back over it. Fold the rear sight first. Unfold the front frame first | The rear sight swings freely under the raised front frame and lies below the field when folded. Folded, the finder rises 9.0mm over the body top (Z = +35.5) and stays inside the body outline |

Pull the dark slide before framing. The slide's handle stands in the line of sight while the slide is in, but it does not touch the frames.

---

## 6. Added in the Phase 1 Review

- **Tripod socket.** Pinhole exposures run from seconds to minutes, so the camera needs a 1/4"-20 socket. It is a captured 1/4"-20 hex nut in a boss under the body, where the 50mm-deep body has room for the insert. Each future body carries its own.
- **Feet (phase 4 review).** The film back's rear-cover hinge knuckles hang 7.3mm under its bottom, which left the first draft's tripod boss (0.5mm under the film-back bottom) above them: the camera tipped about 11 degrees on a table and a tripod plate reaching back past Y = +3 sat on the knuckles. The body now carries the camera's whole footprint. The tripod boss and two rear pads end in one plane, 0.75mm below the lowest knuckle, so the camera stands level on three feet and a plate seats on all three and clears the knuckles. The nut moved down into the boss so a 5mm tripod screw still reaches it.
- **Anti-reflection.** Three internal baffle ribs plus matte black paint or flocking. Light that hits the chamber wall at a grazing angle otherwise fogs the frame edges.

## 7. Modeling Parameters (v02 baseline)

Same origin and axes as [film-back.md](film-back.md) section 17: film plane at Y = 0, +Y toward the pinhole.

| Item | Value |
|---|---:|
| Rear face (contacts the film-back datum) | Y = +4.20 |
| Rear footprint | X = +/-39, Z = -29.0 to +26.5 (1mm inside the bridge span and the shell bottom; the top stays below the film-back hook) |
| Top tongue | 1.4mm thick (Y = +4.5 to +5.9), rises to Z = +29.7 inside the film-back hook slot, X = +/-34; 0.3mm clearance each side |
| Bottom latch | A notch in the body's rear-bottom corner clears the film-back lugs and pin. A PETG cantilever, 2.0mm thick and 8mm wide, runs along the notch floor (Z = -29 to -27) from its root at Y = +25 back to a free end at the rear face (about 20.8mm free length). The 1.8mm hook on the free end sits behind the pin (Y = +4.2 to +6.7) and rises 0.3mm past the pin centre, with its front face 0.3mm from the pin, so the body cannot pull away from the datum (strain about 1.2%). A 45 degree lead-in on the hook lets it ramp over the pin as the body swings in, flexing the cantilever downward. Press the free end down to release. Revised in phase 4 (2026-10-22): the first draft put the hook in front of the pin, where it could not hold the body |
| Walls | 2.5mm |
| Chamber at the rear | 69 x 28mm inside, tapering to the M42 bore at the front |
| Baffle ribs | Three, 1.5mm thick, at Y = +15, +27, +39, openings 1mm outside the image cone |
| Pinhole plane | Y = +50.0 (+/-0.3) |
| Tripod socket | Stainless 1/4"-20 hex nut captured in a printed hex pocket inside a 16mm boss at Y = +32, X = 0, with 1.2mm of plastic under the nut. The nut slides in from the +X side. No 1/4"-20 heat-set insert is sold on Lazada TH |
| Feet | Seat plane Z = Cover.hinge_axis_z - knuckle_od / 2 - 0.75 = -38.05 (derived, so it follows the hinge). Three feet end in it: the tripod boss (the boss runs out at 45 degrees on its rear side to print without support) and two rear pads at X = +/-27 to +/-35, Y from the datum face to +14. Every other part stays at least 0.5mm above the plane, so a tripod plate of any size seats flat. A 5mm screw engages 3.8mm (3.0 threads) of the nut; the check asks for 2.5 threads, which a 4.5mm screw still meets. On a table the rear cover can open to about 72 degrees before the dark slide holder on its back touches the table (about 90 degrees without the holder, film-back.md 5.1); at the 100 degree film-loading angle its edge dips about 11mm below the table, so load film with the camera held up or tilted back |
| Viewfinder | Front frame and rear sight (section 5). Rear hinge axis Y = +12.5, Z = +32.3, folds -90 degrees about +X; front hinge axis Y = +28.0, Z = +31.2, folds +90 degrees. Hinge bases sit on the body top, located by two 3mm pegs each, and the body has a 0.6mm relief under each detent tongue |

M42 mount values: see section 8.

## 8. M42 Mount From Bought Caps

M42 caps are sold as a pair (body cap + rear lens cap) for about ฿39-50 on Lazada TH. A rear lens cap has the female thread, because it screws onto a lens's male rear thread. A body cap has the male thread.

- **Body (female):** cut the centre out of the rear lens cap to a 36mm opening and glue the threaded ring into a printed pocket in the front plate.
- **Pinhole module (male):** the body cap, drilled through, carries the pinhole and the printed shutter (see [lens.md](lens.md)).

Neither cap's dimensions are published. Buy the pair and measure before phase 4:

| Measure | Nominal used for layout |
|---|---:|
| Rear cap ring OD | 46mm |
| Rear cap ring height | 8mm |
| Body cap flange OD | 53mm |
| Body cap stack, female seat face to pinhole plane | 2.0mm |

The female seat face sits at Y = 50.0 minus the measured cap stack (48.0 nominal). A printed shim ring under the glued ring absorbs a measured difference, so the 50.0 +/-0.3mm pinhole distance does not depend on cap tolerances. The 36mm bore lies within 10mm behind the pinhole, and the corner rays need only 7mm radius there (`cad/checks.py`).

Do not buy T-mount/T2 parts by mistake. T2 is also 42mm but has a 0.75mm pitch; check for "x1" or "SLR" in the listing.
