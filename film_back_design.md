# Film Back Design - Full Specification

**Module:** Shared film back  
**Frame format:** 65 x 24mm on 135 film  
**Design priority:** Simple, printable, mechanically understandable, and easy to repair  
**Reference drawing:** [images/film-back-isometric-plan.svg](images/film-back-isometric-plan.svg)

This document is the detailed design spec for the film back. The system-level camera architecture remains in [camera_design.md](camera_design.md).

---

## 1. Functional Summary

The film back is a self-contained film transport unit. It provides:

- 135 film cartridge chamber on the left
- 65 x 24mm exposure gate in the center
- Film rail/body interface datum for all body modules
- Dark slide slot so the body can be removed without exposing film
- 14-tooth sprocket roller that physically counts 14 perforations
- One-notch cam auto-lock after one sprocket revolution
- Direct-drive take-up spool and advance knob on the right
- One-piece main film-back shell with one bottom-hinged rear cover
- Hand-cut foam pressure pad on the rear cover, covering gate through sprocket
- Top-hook + bottom-latch body module locking interface

Film travels left to right:

```
[135 cartridge] -> [film gate / rails] -> [14T sprocket] -> [take-up spool]
```

---

## 2. Global Film Back Parameters

| Parameter | Value | Notes |
|---|---:|---|
| Frame aperture | 65.0 x 24.0mm | Locked |
| Film advance | about 67.0mm | 66.5mm plus small gap/tolerance |
| Perforation pitch | 4.750mm | KS-1870 pitch |
| Perfs per frame | 14 | One frame advance |
| Sprocket tooth count | 14 | One full turn = one frame |
| Sprocket pitch diameter | 21.17mm | 14 x 4.750 / pi |
| Material | Black PETG | FDM |
| Outer wall thickness | 2.5-3.0mm | Prefer 3.0mm where possible |
| Internal divider thickness | 2.0-2.5mm | Around chambers/gate |
| Screw bosses | 2.5mm wall around hole | If screws are used |
| Body datum | Film rail/front bridge face | Chambers are not datum surfaces |
| Light sealing | Velvet/felt | All door edges, slots, body perimeter |

---

## 3. Overall Layout

The body is a wide, shallow film transport unit with three zones:

```
Top / plan view:

left                    center                         right
┌────────────┐ ┌────────────────────────┐ ┌────────────────────┐
│ cartridge  │ │ film bridge / gate     │ │ sprocket + take-up │
│ chamber    │ │ body interface datum   │ │ chamber            │
└────────────┘ └────────────────────────┘ └────────────────────┘
```

| Zone | Function | Notes |
|---|---|---|
| Left chamber | Holds 135 cartridge | Includes rewind knob and film exit light trap |
| Center bridge | Gate, film rails, dark slide, body interface | Body contacts this area only |
| Right chamber | Sprocket lock + take-up spool | Includes release button and advance knob |

The cartridge and take-up chambers may taper inward toward the center bridge. This keeps the body module from touching chamber walls and makes the bridge face the only mating datum.

OpenSCAD coordinate convention:

| Axis | Direction | Meaning |
|---|---|---|
| X | left to right | Cartridge to take-up spool / film travel |
| Y | rear to front | **+Y is the front body-interface side** |
| Z | bottom to top | Camera height |

The rear/loading side is the low-Y side. The cartridge chamber, gate service opening, sprocket area, and take-up chamber open toward low Y when the rear cover is open. The front/body side is +Y and stays closed except for the exact 65 x 24mm frame aperture, dark slide slot, body interface, and required shaft/button openings.

Main shell split:

| Part | Decision | Notes |
|---|---|---|
| Main film-back body | One printed piece | Keeps the film rail, gate, and chamber alignment in one datum |
| Rear cover | One-piece cover | Opens cartridge, gate, sprocket, and take-up areas together |
| Front plate over bridge | None | Body module mates directly to the film rail/front bridge datum |

The chambers should not have accidental front or side through-holes. Intentional openings are limited to the rear loading openings, film path, dark slide slot, shaft holes, and the exact 65 x 24mm frame aperture.

---

## 4. Film Plane, Gate, and Rails

### 4.1 Gate

| Parameter | Value | Notes |
|---|---:|---|
| Gate aperture width | 65.0mm | Horizontal frame |
| Gate aperture height | 24.0mm | Standard 35mm image height |
| Gate corner radius | 0.5-1.0mm | Reduces film scratch risk |
| Gate bevel | Small rear-side bevel | Avoids hard scratch edge |

### 4.2 Film Rails

The film rails are the critical datum surfaces. They control film flatness and body module registration.

| Parameter | Value | Notes |
|---|---:|---|
| Rail location | Top and bottom of gate | Along film travel |
| Rail width | 2.0-2.5mm each | Enough support without excessive friction |
| Rail proud above gate recess | 0.15-0.20mm | Film rides on rails, not gate floor |
| Rail edge | Rounded/polished | Prevent film scratching |
| Flatness target | +/-0.1mm across gate | Sand lightly after print if needed |
| Rail span | Gate through sprocket entry | Keeps film controlled until the sprocket teeth engage |
| Lateral fences | Outside 35mm film edges | Shallow guides only; do not clamp film |

The body module contacts the front face around this rail/gate area only. The chambers are clearance geometry, not alignment surfaces.

CAD v01 gate implementation:

- Printed gate frame surrounds the exact 65 x 24mm aperture; the aperture remains open through the +Y/front body datum.
- Printed gate frame is deliberately shallow, about 1.3mm deep from the film plane, so it does not read as a rear pressure plate.
- The loaded film sits on the rear side of the film plane and must be visible as a continuous strip when the rear cover is open.
- Top and bottom raised rails sit just in front of the loaded film plane, outside the 24mm frame area. CAD v01 rail depth is about 1.15mm.
- Short side guide pads sit outside the exposed frame width.
- Shallow lane fences sit outside the 35mm film edges to prevent lateral drift without pinching the film.
- The rear service opening must reach the film plane; it should not stop behind the film and hide the strip.
- The open-back view uses one continuous film lane from cartridge exit to sprocket/take-up entry. Do not leave internal rear posts or separate gate/chamber frames crossing the film band.
- The visible film preview starts at the cartridge exit slit, not through the cartridge body.
- CAD v01 uses one large rear loading mouth under the single rear cover. The rear side should read as one open loading area, with only the outer cover lip/seal perimeter remaining.

---

## 5. Dark Slide

The dark slide itself is **not printed**.

Recommended materials:

| Material | Thickness | Notes |
|---|---:|---|
| Aluminum sheet | 0.5mm | Stiff, thin, durable; paint matte black |
| HIPS/PVC black sheet | 1.0mm | Easy to cut with knife |

Slot design:

| Parameter | Value | Notes |
|---|---:|---|
| Slot direction | Insert from top | User pulls upward to remove |
| Slot position | Body-interface/front side of film | Blocks light entering from detached body side |
| Slot width across frame | at least 70mm | 65mm frame plus margins |
| Slot clearance | 1.3mm for 1.0mm sheet | 0.3mm working clearance |
| Stop | Mechanical stop at bottom | Prevents slide from hitting film path |
| Handle clearance | Above top surface | Large enough to grab in the dark |

Light sealing:

- Velvet/felt strips at the top slot opening.
- Felt at both side edges of the slide path if practical.
- Matte black paint on metal slide.
- Optional felt tab near slide tip to block the final gap.

---

## 6. Supply Chamber and Rewind

The left chamber holds a normal 135 cartridge.

| Parameter | Value | Notes |
|---|---:|---|
| Cartridge clearance | about 32mm inner relief | 135 cartridge is about 30-31mm diameter |
| Rewind knob | Top-mounted | Coupled to cartridge spool |
| Rewind knob diameter | about 18-22mm | Knurled if printed |
| Film exit | Narrow slit toward gate | Felt/velvet light trap |
| Cartridge loading | From rear cover opening | Cover must give enough hand access |
| Cartridge throat | Straight guide into rail/gate path | Felt/velvet lands above and below film |

Rewind behavior:

- The sprocket lock blocks film motion unless released.
- To rewind a full roll, hold the release button down continuously while turning the rewind knob.
- This is intentional to avoid adding a rewind clutch or separate sprocket bypass.

---

## 7. Sprocket Roller

### 7.1 Chosen Architecture

Use a **single 14-tooth sprocket roller** engaging one perforation row. Do not use 7 x 2, gear reduction, or a separate counter.

Reasons:

- One sprocket revolution equals one frame advance.
- The auto-lock cam needs only one notch.
- No gear train or two-revolution counter is required.
- The part is large enough to print and tune.

### 7.2 Geometry

| Parameter | Value | Notes |
|---|---:|---|
| Tooth count | 14 | One per perforation |
| Pitch diameter | 21.17mm | 66.5mm circumference |
| Tooth angular spacing | 25.714 deg | 360 / 14 |
| Tooth row | Single row | Bottom perf row preferred |
| Tooth width along film travel | 1.4mm | Conservative fit inside KS perf |
| Tooth height along perf height | 1.2mm | Conservative fit |
| Tooth radial engagement into perf | 0.8-1.0mm | Enough to count without tearing |
| Tooth tip radius/fillet | 0.2-0.3mm | Avoid sharp film damage |
| Shaft | 4.0mm metal rod preferred | Printed shaft acceptable for mockup only |

The tooth dimensions are deliberately smaller than the perforation. The goal is reliable indexing, not tight registration inside the perf. FDM tolerance and film variation make a loose tooth safer.

The film path includes a local sprocket guide around the lower perf row. Its job is only to keep the film seated on the sprocket teeth while the rear cover foam prevents the film from lifting away.

### 7.3 Tooth Orientation

The tooth's long dimension should align with the film travel direction. The tooth enters the lower perforation row just far enough to rotate the sprocket as film moves.

Use rounded teeth rather than square sharp teeth. A small chamfer on the entry/exit side helps the film settle without catching.

### 7.4 Test Requirement

Before modeling the full back around the sprocket, print a small sprocket test coupon:

- 14-tooth sprocket only
- Simple shaft hole
- Small guide rail and scrap film path

Test with real scrap 135 film. The CAD values are starting dimensions; the tooth fit should be tuned from physical tests.

---

## 8. Auto-Lock and Release Button

### 8.1 Chosen Mechanism

Use a **one-notch cam disc** fixed to the same vertical shaft as the sprocket. The cam, pawl, and spring live inside the right chamber/top-cover area. Only the release button or plunger protrudes outside for the user.

```
release button
    |
    v
spring-loaded pawl
    |
    v
one-notch cam disc  -- same shaft -- 14T sprocket
```

### 8.2 Operation

1. Starting state: pawl rests in the cam notch; sprocket is locked.
2. User presses release button; button lifts pawl out of the notch.
3. User turns advance knob; take-up spool pulls film; sprocket rotates with film.
4. Once the cam has rotated out from under the pawl, the user may release the button.
5. Pawl rides on the outer cam surface while the sprocket rotates.
6. After one full revolution, the notch returns under the pawl.
7. Pawl drops into the notch with a click; sprocket locks again.
8. User stops advancing.

### 8.3 Lock Behavior

| Behavior | Decision | Notes |
|---|---|---|
| Advance lock | Yes | Locks after one sprocket revolution |
| Rewind lock | Yes | Rewind requires holding release |
| One-way ratchet | No | Avoid extra complexity |
| Frame counter | No | Not needed for first version |
| Visual indicator | Yes, simple | Dot/mark on cam or shaft top |

This is a deliberately simple lock. It does not prevent user error if the user forces the advance knob after the click. The user must stop when the click is felt/heard.

### 8.4 Cam and Pawl Design

| Part | Starting spec | Notes |
|---|---:|---|
| Cam disc diameter | 16-18mm | Large enough for printable notch |
| Cam thickness | 2.5-3.0mm | PETG |
| Notch width | 2.0-2.5mm | Tune to pawl tip |
| Notch depth | 1.5-2.0mm | Must lock positively |
| Pawl tip width | 1.5-2.0mm | Slightly narrower than notch |
| Pawl material | PETG lever + metal spring | Keep spring separate |
| Spring | 3-4mm compression spring | Preferred over printed spring |
| Button location | Top of take-up/sprocket area, offset from sprocket shaft | Button protrudes; pawl/cam stay internal |

Release button should have enough travel to lift the pawl fully clear of the notch. Target button travel: about 2.0-3.0mm.

CAD v01 places the release button over the free end of the pawl, offset from the sprocket shaft. The sprocket shaft and release plunger use separate top openings with small bosses/collars so the top cover does not look like one large open gap.

### 8.5 Visual Indicator

Add a simple visual indicator, not a frame counter:

- Small painted dot on cam disc or shaft cap.
- Small fixed index mark on the top plate.
- When the dot returns to the index mark and the click occurs, one frame has advanced.

The click is the primary stop cue; the dot is a backup cue.

---

## 9. Take-Up Spool and Advance Knob

### 9.1 Chosen Drive

The advance knob drives the take-up spool directly. No slip clutch is included in the first version.

This is mechanically simple but comes with an explicit operating rule:

> Stop turning the advance knob as soon as the sprocket lock clicks.

### 9.2 Take-Up Spool

| Parameter | Value | Notes |
|---|---:|---|
| Core diameter | 14-16mm | Printable |
| Max wound diameter | about 20-24mm | Depends on leader and roll length |
| Film attachment | Slot or taped leader | Keep simple |
| Shaft | Metal rod preferred | Reduces wear |
| Advance knob | Top-mounted | Directly coupled |
| Knob diameter | 22-28mm | Thumb-operable |
| Leader guide | Simple angled guide from sprocket to spool | Helps the film leader find the take-up slot during loading |

The leader guide must stay inside the take-up chamber envelope. In CAD review it should not protrude through the outer +X wall, because that would indicate the loaded film path or guide is intersecting the body.

### 9.3 Known Limitation

Because there is no slip clutch, take-up tension increases as the take-up roll grows. This is accepted for the simple DIY version. The sprocket lock is the frame stop, not the take-up spool position.

If physical testing shows film tearing or excessive tension, the first upgrade should be a felt/washer friction clutch under the advance knob.

---

## 10. Rear Cover and Pressure Pad

### 10.1 Cover

Chosen cover style: **one-piece bottom-hinged rear cover**.

Reasons:

- The camera body is wide; a bottom-hinged cover opens down and gives broad access.
- One cover keeps loading simple and opens the full film path at once.
- The cover can carry one continuous hand-cut foam pressure pad from gate through sprocket.
- It avoids a long side door swinging across the user's hand.

| Parameter | Value | Notes |
|---|---:|---|
| Hinge side | Bottom | Door opens downward |
| Cover count | 1 | One cover across cartridge, gate, sprocket, and take-up zones |
| Latch side | Top | One or two top latches |
| Hinge pin | 2-3mm metal rod | More durable than printed pin |
| Cover seal | Velvet/felt around perimeter | Required |
| Cover stop | Printed stop/ledge | Repeatable closed position |

The rear opening is one large loading opening under one cover. Seal geometry should sit around the outer perimeter only. Do not add internal rear cover seals between cartridge, gate, and take-up zones because they block loading access and visually interrupt the film strip.

The +Y/front exterior of both side chambers must remain closed. In CAD v01 the rear access voids follow the tapered chamber walls and stop before the +Y/front chamber face. Do not add separate visual cap pieces to hide accidental through-holes; the main shell geometry itself must be closed. Only the required top shaft/button openings are allowed.

### 10.2 Foam Pressure Pad

The pressure plate is not printed. Use foam or sponge adhered to the inner rear cover.

| Parameter | Value | Notes |
|---|---:|---|
| Material | EVA foam or camera light-seal foam | Closed-cell preferred |
| Thickness | 1-2mm starting point | Tune physically |
| Compression | Light compression only | Enough to keep film seated |
| Coverage | Gate through sprocket area | One continuous piece preferred |
| Sprocket relief | Cut by hand | Leave clearance for sprocket teeth |

Do not over-compress the film. Too much pressure will make advance rough and may scratch film.

---

## 11. Body Module Lock

### 11.1 Chosen Interface

Use **top hook rail + bottom latch pin**, similar in principle to classic removable film backs.

Film back side:

- Top receiving hook rail above the film bridge.
- Bottom 3mm pin or metal rod near the lower bridge edge.
- Velvet seal around the body opening.

Body side:

- Top lip hooks into the film back rail.
- Bottom latch hook catches the lower pin.
- Body pivots into the film back until it contacts the rail/gate datum.

### 11.2 Attachment Motion

1. Angle the body module into the film back.
2. Engage the top lip into the top hook rail.
3. Pivot the lower body edge toward the film back.
4. Latch hook clicks over the lower 3mm pin.
5. Body is pulled against the film rail/body datum and velvet seal.

### 11.3 Datum Strategy

| Datum | Role |
|---|---|
| Film rail/front bridge face | Primary optical and mechanical datum |
| Top hook rail | Locates body vertically and prevents top separation |
| Bottom latch/pin | Pulls body tight; not the primary optical datum |
| Chamber walls | Clearance only; must not touch body |
| Velvet seal | Light seal, not dimensional reference |

The latch should provide clamping force, not optical alignment. Alignment must come from the rail/body interface surfaces.

---

## 12. Light Sealing Strategy

Use velvet/felt where printed geometry alone is not worth the complexity.

Required seal points:

- Film cartridge exit slit
- Dark slide top slot
- Dark slide side guides if exposed
- Rear cover perimeters
- Body-to-film-back perimeter
- Rewind shaft opening
- Advance shaft opening
- Release button opening if it penetrates the chamber

Additional protection:

- Matte black paint inside the film path and chambers.
- Test printed PETG wall opacity with a flashlight.
- If light passes through printed walls, paint the inside with matte black acrylic.

---

## 13. PETG / FDM Build Rules

| Feature | Starting value | Notes |
|---|---:|---|
| Outer walls | 2.5-3.0mm | Use 3.0mm where possible |
| Internal walls | 2.0-2.5mm | Avoid flex near film rail |
| Body lock lugs | 4.0mm | Higher stress area |
| Screw boss wall | 2.5mm around hole | For heat-set inserts/screws |
| Film rail height | At least 2.0mm base | Enough material to sand/polish |
| Layer height | 0.2mm | Practical default |
| Wall lines | 4 | Helps light tightness |
| Top/bottom layers | 5 | Helps light tightness |
| Infill | 25-35% gyroid | General structure |

Post-processing:

- Deburr all film contact edges.
- Sand/polish film rails lightly.
- Paint interior matte black if needed.
- Add velvet/felt after test fitting.

---

## 14. Operating Sequence

### Loading

1. Open the bottom-hinged rear cover.
2. Insert 135 cartridge into left chamber.
3. Pull film across gate and rails.
4. Engage lower perf row with sprocket teeth.
5. Feed leader into take-up spool slot.
6. Close rear cover; foam pad holds film against rails and sprocket.
7. Advance until film is seated and the sprocket lock clicks.

### Shooting / Advancing

1. Make exposure.
2. Press release button to lift pawl.
3. Turn advance knob.
4. Release button after cam has moved off the notch.
5. Continue turning until the sprocket clicks.
6. Stop turning immediately.

### Rewinding

1. Hold release button down.
2. Turn rewind knob until film returns to cartridge.
3. Open back in subdued light only after rewind is complete.

---

## 15. Prototype Test Plan

### 15.1 Sprocket Test

- Print sprocket and simple guide first.
- Test with scrap 135 film.
- Confirm the teeth enter perforations without tearing.
- Confirm one full sprocket turn advances 14 perforations.
- Tune tooth size if needed.

### 15.2 Lock Test

- Test cam and pawl outside the full body.
- Confirm button lift clears notch.
- Confirm pawl drops reliably after one rotation.
- Confirm audible/tactile click.

### 15.3 Transport Test

- Load scrap film through the full back.
- Advance repeatedly.
- Confirm frame spacing by marking 14-perf increments.
- Confirm film does not jump off sprocket under foam pressure pad.

### 15.4 Light Leak Test

- Put bright flashlight inside dark room or inside camera body side.
- Check dark slide slot, rear cover, shafts, and body interface.
- Add velvet/felt or matte black paint where needed.

---

## 16. Open Items After v01 Layout

These are the remaining local layout decisions, not architectural blockers:

| Item | Needed decision |
|---|---|
| Exact overall width | Set after cartridge, gate, sprocket, and spool center positions are drawn |
| Exact chamber depth | Set from cartridge access and take-up spool clearance |
| Exact release button details | Cap shape, spring pocket, and travel stop |
| Exact rear cover latch details | Final latch geometry and metal/printed spring choice |
| Exact body latch spring | Printed flex latch vs. separate metal spring |
| Exact dark slide material | 0.5mm aluminum or 1.0mm HIPS/PVC |
