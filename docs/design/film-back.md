# Film Back Design - Full Specification

**Module:** Shared film back  
**Frame format:** 65 x 24mm on 135 film  
**Design priority:** Simple, printable, mechanically understandable, and easy to repair  
**Reference drawing:** [proto-film-back-rough-design.png](../images/proto-film-back-rough-design.png)  
**Modeling values:** section 17 holds the single value for every dimension the CAD uses. Ranges elsewhere in this document are background; section 17 wins.

This document is the detailed design spec for the film back. The system-level camera architecture remains in [camera.md](camera.md).

---

## 1. Functional Summary

The film back is a self-contained film transport unit. It provides:

- 135 film cartridge chamber on the left
- 65 x 24mm exposure gate in the center
- Film rail/body interface datum for all body modules
- Dark slide slot so the body can be removed without exposing film
- 14-tooth sprocket roller that physically counts 14 perforations
- One-notch cam auto-lock after one sprocket revolution
- Take-up spool driven through a felt friction clutch by the advance knob on the right
- One-piece main film-back shell with one bottom-hinged rear cover
- Hand-cut foam pressure pad on the rear cover over the gate, plus a printed shoe on the cover that holds the film on the sprocket
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
| Film advance | 66.5mm | Exactly 14 perforations |
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

CAD coordinate convention:

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
| Rail location | On the 2.01mm film edge band, outside the perforations | Along film travel |
| Rail width | 1.2mm each | Fits inside the edge band with 0.5mm to the perforations |
| Rail proud above gate recess | 0.15-0.20mm | Film rides on rails, not gate floor |
| Rail edge | Rounded/polished | Prevent film scratching |
| Flatness target | +/-0.1mm across gate | Sand lightly after print if needed |
| Rail span | Gate through sprocket entry | Keeps film controlled until the sprocket teeth engage |
| Lateral fences | Outside 35mm film edges | Shallow guides only; do not clamp film |

The body module contacts the front face around this rail/gate area only. The chambers are clearance geometry, not alignment surfaces.

Gate rules carried from the v01 review:

- The gate aperture stays open through the +Y body datum face.
- The rear loading opening reaches the film plane, so the loaded strip is visible from cartridge exit to sprocket when the cover is open.
- No post or frame crosses the film band between the cartridge exit and the take-up spool.

---

## 5. Dark Slide

The dark slide itself is **not printed**.

Recommended materials:

| Material | Thickness | Notes |
|---|---:|---|
| Aluminum sheet (chosen) | 0.5mm | Opaque, flat, stiff; paint matte black |
| HIPS/PVC black sheet (fallback) | 1.0mm | Needs a 1.3mm slot; check opacity with a flashlight |

Slot design:

| Parameter | Value | Notes |
|---|---:|---|
| Slot direction | Insert from top | User pulls upward to remove |
| Slot position | Body-interface/front side of film | Blocks light entering from detached body side |
| Slot width across frame | at least 70mm | 65mm frame plus margins |
| Slot clearance | 0.8mm for the 0.5mm aluminum sheet | 0.3mm working clearance |
| Stop | Mechanical stop at bottom | Prevents slide from hitting film path |
| Handle clearance | Above top surface | Large enough to grab in the dark |
| Slot plug | Printed 0.5mm tab, 10mm deep, with a grip | Goes into the slot mouth whenever the slide is out (section 17.2) |

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
- To rewind, press the release button and turn it a quarter turn. A pin on the button drops into an L-shaped slot and holds the pawl clear, so the user does not hold the button through about 20 rewind turns. Turn it back after rewinding.
- This keeps the no-clutch rewind of the original design and removes its one tiring step.
- The rewind knob lifts 8mm to free the cassette for loading. An O-ring on the shaft holds it up by friction.

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
| Tooth size | See section 17.6 | 1.4mm along travel, 2.0mm across, 0.7mm tall, tapered flanks |
| Shaft | 3.0mm steel pin, fixed in the shell | Sprocket and cam rotate on it as one printed part |

The tooth dimensions are deliberately smaller than the perforation. The goal is reliable indexing, not tight registration inside the perf. FDM tolerance and film variation make a loose tooth safer.

The film path includes a local sprocket guide around the lower perf row. Its job is only to keep the film seated on the sprocket teeth; the printed shoe on the rear cover stops the film lifting away.

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

Use a **one-notch cam disc** printed as one part with the sprocket, so the notch can never slip out of phase with the teeth. The part spins on a fixed steel pin. The cam, pawl, and spring live inside the right chamber/top-cover area. Only the release button or plunger protrudes outside for the user.

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
| Rewind lock | Yes | Rewind uses the quarter-turn button hold (section 6) |
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

The notch is cut in the cam's top face. The pawl is a lever on a horizontal pivot: its tip drops into the face notch, and the button presses the other end down to lift the tip. A vertical button press cannot lift a pawl that pivots on a vertical axis, so the v01 radial notch is dropped.

Release button should have enough travel to lift the pawl fully clear of the notch. Target button travel: about 2.0-3.0mm.

The release button sits over the free end of the pawl, offset from the sprocket pin. The sprocket hub and the button use separate top openings, each with a collar for light sealing.

### 8.5 Visual Indicator

Add a simple visual indicator, not a frame counter:

- Small painted dot on cam disc or shaft cap.
- Small fixed index mark on the top plate.
- When the dot returns to the index mark and the click occurs, one frame has advanced.

The click is the primary stop cue; the dot is a backup cue.

---

## 9. Take-Up Spool and Advance Knob

### 9.1 Chosen Drive

The advance knob drives the take-up spool through a felt friction washer pressed by a small compression spring.

The v01 design had no clutch. Once the pawl locks the sprocket, every extra bit of knob torque goes into the film perforations and the PETG teeth. A thumb on a 26mm knob can pull roughly 10-25N of film tension on a 16-24mm spool (estimate from about 0.1-0.2Nm thumb torque), enough to tear perforations. The friction washer caps that tension and costs one felt disc and one spring. The operating rule still applies:

> Stop turning the advance knob as soon as the sprocket lock clicks.

### 9.2 Take-Up Spool

| Parameter | Value | Notes |
|---|---:|---|
| Core diameter | 14-16mm | Printable |
| Max wound diameter | about 20-24mm | Depends on leader and roll length |
| Film attachment | Slot or taped leader | Keep simple |
| Shaft | Metal rod preferred | Reduces wear |
| Advance knob | Top-mounted | Drives the spool through the felt clutch |
| Knob diameter | 22-28mm | Thumb-operable |
| Leader guide | Simple angled guide from sprocket to spool | Helps the film leader find the take-up slot during loading |

The leader guide must stay inside the take-up chamber envelope. In CAD review it should not protrude through the outer +X wall, because that would indicate the loaded film path or guide is intersecting the body.

### 9.3 Clutch Tuning

The sprocket lock is the frame stop, not the take-up spool position. The friction washer slips when the film is locked. Tune slip by spring preload: the film must still pull the sprocket round with the rear cover closed, and the knob must slip without tearing scrap film once the lock clicks.

---

## 10. Rear Cover and Pressure Pad

### 10.1 Cover

Chosen cover style: **one-piece bottom-hinged rear cover**.

Reasons:

- The camera body is wide; a bottom-hinged cover opens down and gives broad access.
- One cover keeps loading simple and opens the full film path at once.
- The cover carries the gate pressure pad and the sprocket shoe, so closing it seats the film in one motion.
- It avoids a long side door swinging across the user's hand.

| Parameter | Value | Notes |
|---|---:|---|
| Hinge side | Bottom | Door opens downward |
| Cover count | 1 | One cover across cartridge, gate, sprocket, and take-up zones |
| Latch side | Top | Two printed turn-buttons, each on an M3 screw into a heat-set insert. A dog under each button sits in a groove in the cover's top lip |
| Hinge pin | 3.0mm steel pin | Same stock as the other shafts |
| Cover seal | Velvet/felt around perimeter | Required |
| Cover stop | Printed stop/ledge | Repeatable closed position |

The hinge axis is about 68mm below the top lip, so opening the cover slides the lip almost straight back, rising at most 0.02mm. A button that only rests on the lip does not hold the cover. Each button therefore has a dog under its rear end that drops into an arc groove in the lip top. When the cover starts to open, the groove's front wall moves back into the dog and stops it. A quarter turn of the button, counter-clockwise from above, carries the dog along the groove and out past the lip's front edge, and the cover is then free to swing.

The rear opening is one large loading opening under one cover. Seal geometry should sit around the outer perimeter only. Do not add internal rear cover seals between cartridge, gate, and take-up zones because they block loading access and visually interrupt the film strip.

The +Y/front exterior of both side chambers must remain closed. The rear access voids follow the tapered chamber walls and stop before the +Y/front chamber face. Do not add separate visual cap pieces to hide accidental through-holes; the main shell geometry itself must be closed. Only the required top shaft/button openings are allowed.

### 10.2 Foam Pressure Pad

The pressure plate is not printed. Use foam or sponge adhered to the inner rear cover.

| Parameter | Value | Notes |
|---|---:|---|
| Material | 2mm closed-cell foam with a 0.25mm smooth black plastic sheet on the film side | The sheet keeps foam dust and texture off the film |
| Thickness | 2mm foam + 0.25mm sheet | Tune physically |
| Compression | Light compression only | Enough to keep film seated |
| Coverage | Gate zone only | Pad drag must stay below the clutch slip force; the printed cover shoe handles the sprocket |

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
6. Close rear cover; the foam pad holds the film on the rails and the cover shoe holds it on the sprocket.
7. Advance until film is seated and the sprocket lock clicks.

### Shooting / Advancing

0. Before the first frame: pull the dark slide and push the slot plug into the slot mouth. Reverse this before removing the body.

1. Make exposure.
2. Press release button to lift pawl.
3. Turn advance knob.
4. Release button after cam has moved off the notch.
5. Continue turning until the sprocket clicks.
6. Stop turning immediately.

### Rewinding

1. Press the release button and turn it a quarter turn to hold it down.
2. Turn rewind knob until film returns to cartridge.
3. Turn the release button back.
4. Open back in subdued light only after rewind is complete.

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
- Confirm film does not jump off the sprocket under the cover shoe.
- Measure film drag with a luggage scale: at most 1.0N with the cover closed.

### 15.4 Light Leak Test

- Put bright flashlight inside dark room or inside camera body side.
- Check dark slide slot, rear cover, shafts, and body interface.
- Add velvet/felt or matte black paint where needed.

---

## 16. Resolved v01 Open Items

| Item | Resolution |
|---|---|
| Overall width | 175mm, from the X layout in section 17 |
| Chamber depth | Set by the cassette and the forward-mounted sprocket; see section 17 |
| Release button details | Section 17, plus the quarter-turn rewind hold in section 6 |
| Rear cover latch | Two turn-buttons on M3 screws |
| Body latch spring | Printed PETG cantilever hook on a 3mm steel pin; strain about 1.7% |
| Dark slide material | 0.5mm aluminum, painted matte black |

---

## 17. Modeling Parameters (v02 baseline)

Single values for CAD. Every value becomes a named parameter in `cad/params.py`. Values marked **tune** depend on the printer and get a test coupon in the print package. Values marked **measure** come from a real cassette or bought part and must be checked with calipers before phase 3. `cad/checks.py` recomputes the derived values.

### 17.1 Origin and film

Origin: center of the 65 x 24mm gate, on the film plane. The film plane is the emulsion surface, which lies against the rails. The film occupies Y = -0.13 to 0.

| Parameter | Value | Source |
|---|---:|---|
| Film width | 35.00mm | ISO 1007 nominal 34.975 |
| Film thickness | 0.13mm | Typical acetate/PET base + emulsion |
| Perforation pitch | 4.750mm | SMPTE ST 139 KS long pitch |
| Perforation size along travel | 1.981mm | SMPTE ST 139 |
| Perforation size across film | 2.794mm | SMPTE ST 139 |
| Film edge to perforation | 2.01mm | SMPTE ST 139 |
| Perforation row centre | Z = +/-14.09mm | 17.5 - 2.01 - 2.794/2 |
| Gap between perforation rows | 25.39mm | Leaves 0.70mm each side of the 24mm image |

### 17.2 Front stack (Y, from the film plane toward the body)

| Surface | Y | Notes |
|---|---:|---|
| Rail contact face | 0.00 | Rails 1.2mm wide on the film edge band, centred at Z = +/-16.6, 0.5mm clear of the perforations |
| Gate plate rear face | +0.20 | Gate recess keeps the film off the plate |
| Gate plate front face | +1.40 | 1.2mm plate; 65.0 x 24.0 aperture, 0.5mm corner radius, 0.3mm rear bevel |
| Dark slide slot | +1.40 to +2.20 | 0.8mm slot for 0.5mm aluminum, 72mm wide, bottom stop at Z = -15 |
| Front wall | +2.20 to +4.20 | 2.0mm; 67 x 26mm aperture |
| **Body datum face** | **+4.20** | Spans X = +/-40, Z = -30 to +30. Velvet sits in a 3mm wide, 0.6mm deep groove around the aperture, leaving 1.4mm of wall over the slot, so the seal never sets the distance |

Lateral fences: inner gap 35.3mm, from Y = 0 back to Y = -0.8.

**Dark slide slot light trap.** The slot mouth on the top face stays open while shooting, and it leads straight to the gate. Line both faces of the mouth with flocking so the faces meet when the slot is empty, and insert a printed slot plug (0.5mm tab, 10mm deep, with a grip) whenever the slide is out.

### 17.3 Rear stack

| Item | Value |
|---|---:|
| Pressure pad | 0.25mm black plastic sheet on 2.0mm closed-cell foam, compressed by 0.15mm (light preload; **tune** with tape shims under the foam, since print tolerance is as large as the squeeze) |
| Pad size | 75 x 33mm, gate zone only |
| Cover inner face at the gate | Y = -2.23 |
| Cover thickness | 2.5mm |
| Sprocket shoe | Printed on the cover. Arc from the bottom of the hub (-90 deg) to -45 deg, inner radius 10.95mm (hub + film + 0.3mm), 34.6mm wide so it fits between the sprocket flanges, with a 2.6 x 1.0mm groove for the teeth. It holds the film on the teeth over the whole contact arc |
| Cover seal | Sides and bottom: tongue 1.6 x 2.5mm on the cover, into a 2.2 x 3.0mm groove in a 4.6mm shell rim (1.2mm each side of the groove), 1.5mm foam strip in the groove bottom. Top: lap joint, the cover overlaps the shell top by 6mm with foam between, so the rear opening reaches the chamber ceiling at Z = +28.5 and the cassette spool tip (Z = +27) passes under it |
| Hinge | Bottom edge, three knuckles of 7mm OD on a 3.0mm steel pin, 171mm long, inset 2mm each end |
| Latch | Two turn-buttons (20 x 8 x 3mm) on M3 screws into heat-set inserts in the shell top, pivots at X = +/-42.5, Y = 5.6. Each has a 3 x 2 x 1mm dog under its rear end, centred 7.5mm from the pivot. The dog sits in an arc groove in the top lip, which is 2.5mm thick for it: the groove is 1.3mm deep (1.2mm floor) with 0.3mm clearance round the dog, and runs a quarter turn counter-clockwise from above out past the lip's front edge. Latched, the cover stops after about 0.3mm of travel. Released, the dog hangs over the shell top clear of the cover's swing. The buttons print top down |

The pad and the clutch work against each other: pad drag must stay well below the clutch slip force, or the knob slips before the film moves. That is why the pad covers the gate only and is barely compressed. The print package includes a drag test with go/no-go limits: pull scrap film through the closed back with a luggage scale. Drag must be at most 1.0N, and the clutch must transmit at least 3.0N before slipping.

### 17.4 X layout and envelope

| Item | Value |
|---|---:|
| Bridge clear span (body fits here) | X = -40 to +40 |
| Chamber divider walls at the bridge | 2.5mm thick, X = +/-40 to +/-42.5 (an exception to the 2.2mm internal walls; they carry the bridge) |
| Cassette chamber interior | X = -74.5 to -42.5 (32mm), Y = -2.2 to +27 |
| Cassette centre | X = -58.5, Y = +12.5 |
| Sprocket centre | X = +55.0, Y = +10.52 (hub touches the emulsion side at Y = 0) |
| Take-up spool centre | X = +81.0, Y = +12.0 |
| Take-up chamber interior | to X = +94.5 (sprocket flange clears the divider wall by 1.0mm; wound roll clears the sprocket flange by 2.5mm) |
| Outer walls | 3.0mm |
| Internal walls | 2.2mm |
| Overall shell | X = -77.5 to +97.5 (175mm), Z = -30 to +31.5 (61.5mm) plus the rewind tower, Y = -4.8 to +30 |

The film follows an S path: past the rear of the sprocket, round its +X side, then across to the -X/front side of the take-up spool. The wrap on the sprocket is 49-63 degrees (empty to full spool), so 1.9-2.5 teeth engage. That is normal for a 35mm camera. The sprocket only counts perforations; the clutch limits film tension, and the cover shoe stops the film lifting off the teeth. A straight path tangent to both rolls would wrap only a few degrees.

The S path winds the take-up roll emulsion-out, against the curl the film has from the cassette. Check that the leader catches and winds cleanly in the scrap-film test.

### 17.5 Cassette chamber and rewind (measure)

| Item | Value |
|---|---:|
| Cassette shell | 25.0mm diameter, 39.0mm between end caps, centred on Z = 0 (**measure**) |
| Felt lip envelope | 29.5mm across (**measure**) |
| Spool ends | Top 7.5mm above the cap with the rewind key (tip at Z = +27), bottom stub 2.5mm (**measure**) |
| Chamber ceiling | Z = +28.5 inside, top wall to +31.5; 1.5mm over the spool tip |
| Bottom locator | 7mm recess for the spool stub |
| Rewind tower | Hollow boss over the cassette axis, 7.6mm inside diameter, from the top wall up to Z = +37 (inside top), 2.0mm walls, closed top with a 3.3mm bushing bore |
| Rewind fork | 7mm OD, 2.6mm slot, 4.5mm deep (**measure** the spool key); engaged it spans Z = +22.5 to +28.2, lifted 8mm it sits inside the tower (top at +36.2, 0.8mm under the tower top) |
| Rewind shaft | 3.0mm steel pin, 21mm (Z = +27.2 to +48.2). It stops at the roof of the fork's 2.6mm slot, since a 3.0mm rod cannot pass the slot. Revised in phase 3 (2026-10-22) from 27mm |
| Rewind knob | 20mm OD, 10mm tall, knurled, on top of the tower; lifts 8mm. An O-ring on the shaft sits in a 4.8mm counterbore in the tower top and holds the knob up by friction |
| Film throat | 0.6mm slot at the chamber exit, velvet on both lands |

### 17.6 Sprocket and lock (one printed part)

| Item | Value |
|---|---:|
| Pitch diameter | 21.17mm |
| Hub diameter at the film lands | 21.04mm |
| Centre relief (image zone, Z = -12.4 to +12.4) | 19.0mm, so the emulsion image area never touches the hub |
| Teeth | 14, on the lower perforation row centred at Z = -14.09 |
| Tooth size | 1.4mm along travel at the root, 2.0mm across, 0.7mm above the hub, flanks tapered to 1.0mm at the tip, 0.25mm tip fillet (**tune**). A 0.9mm parallel tooth would drag on the trailing perforation edge as it leaves the film |
| Flanges | 23mm OD, 1.0mm thick, 35.4mm apart |
| Cam disc | 17mm OD, 3mm thick, Z = +20 to +23 (1.3mm above the top flange). One closed pocket in the top face, 2.2mm wide (tangential) x 2.4mm long (radial), 1.8mm deep, centred at 6.0mm radius so 1.3mm of rim stays outside it, aligned with a tooth gap. In the assembled pose the part is turned so the pocket sits under the pawl tip |
| Top hub | 8mm OD through an 8.4mm collar in the top wall, index dot on top, closed top |
| Pin | 3.0mm steel, 60mm, pressed into a bottom boss, part spins on it |
| Bore clearance | 3.30mm bore on a 3.0mm pin (**tune**) |
| Pawl | Lever 12mm long, 2.0mm thick, pivot in the middle on a horizontal 3.0mm pin 15mm long, tip 1.8mm wide over the notch pocket. In plan it runs at 45 degrees toward +X/+Y from the sprocket axis: tip at (59.2, 14.8), pivot (63.5, 19.0), button end (67.7, 23.2). That keeps the button 17mm from the take-up axis, clear of the 26mm advance knob, and inside the chamber front wall |
| Pawl height | Lever body Z = +23.2 to +25.2 at rest, +25.7 to +27.7 lifted; 0.8mm under the 28.5 ceiling |
| Pawl spring | 0.3mm wire, 3-4mm OD compression spring, about 8mm free; target 1-2N on the tip at working length (**tune**). A 0.4mm-wire spring this short is about 3N/mm (estimate), too stiff for a 2mm PETG lever |
| Release button | 6mm OD at (67.7, 23.2), presses the far end of the pawl, 2.5mm travel (lifts the tip 2.5mm over a 1.8mm notch), quarter-turn L-slot hold for rewind |

### 17.7 Take-up and advance

| Item | Value |
|---|---:|
| Spool core | 16mm OD with a 1.0 x 20mm leader slot |
| Spool flanges | 26mm OD, 1.2mm thick, 35.6mm apart |
| Wound roll | 24mm max at 20 frames (estimate: 1.5m x 0.13mm) |
| Drive shaft | 3.0mm steel pin, 70mm, Z = -28.8 to +41.2: it turns in a top bushing and a blind floor hole that leaves 1.2mm of floor, since the clutch spring pushes it down. 70mm cannot span the full -30 to +42. Revised in phase 3 (2026-10-22) |
| Clutch | Drive collar fixed to the shaft, felt washer, spool free on the shaft, coaxial compression spring of 5mm OD (inside diameter over 3.2mm) for preload (**tune**) |
| Advance knob | 26mm OD, 10mm tall, knurled, fixed to the shaft with epoxy on a filed flat |

### 17.8 Body interface on the film back

| Item | Value |
|---|---:|
| Top hook | L-shaped lip, X = +/-36. Top arm Z = +30.0 to +31.5 reaching from the datum face to Y = +7.7; down arm Y = +6.2 to +7.7, Z = +27.0 to +31.5 |
| Hook slot | Y = +4.2 to +6.2 (2.0mm), Z = +27.0 to +30.0 (3.0mm deep, open downward) |
| Bottom latch pin | 3.0mm steel pin, 48mm, X = +/-24, centred at Z = -25.5, Y = +8.5, held by two lugs on the datum face at X = +/-22 to +/-24 |

The body's tongue rises into the hook slot with 0.3mm clearance each side, so the body can tilt about 5 degrees while its bottom swings in to the latch.
