"""Every camera dimension, in mm and degrees. The single source for CAD and checks.

Coordinates: origin at the gate centre on the film plane (emulsion surface).
X = film travel (cassette to take-up), +Y = front toward the pinhole, Z = up.

Values come from docs/design/film-back.md section 17 and docs/design/simple-body.md
sections 7-8. `Fit` holds printer-dependent values that get a test coupon;
`Measured` holds values to confirm with calipers on bought parts.
"""
from dataclasses import dataclass, field
import math


@dataclass(frozen=True)
class Fit:
    """Printer-dependent. Tune from test coupons, then re-export."""
    shaft_bore: float = 3.30          # bore for a 3.0mm pin to spin in
    fdm_clearance: float = 0.30       # sliding fit between printed parts
    tooth_along_root: float = 1.4
    tooth_along_tip: float = 1.0
    tooth_across: float = 2.0
    tooth_height: float = 0.7
    tooth_tip_fillet: float = 0.25
    pad_squeeze: float = 0.15
    insert_hole_m3: float = 4.0
    pin_press_hole: float = 2.90      # press fit for a 3.0mm steel pin


@dataclass(frozen=True)
class Measured:
    """Nominals until the bought parts arrive (docs/bom.md, 'Measure on arrival')."""
    cassette_d: float = 25.0
    cassette_lip_envelope: float = 29.5
    cassette_cap_height: float = 39.0
    spool_top_protrusion: float = 7.5
    spool_key_slot: float = 2.6
    spool_key_depth: float = 4.5
    m42_seat_to_pinhole: float = 2.0
    m42_rear_cap_od: float = 46.0
    m42_rear_cap_h: float = 8.0
    m42_body_cap_od: float = 53.0
    rod_d: float = 3.0


@dataclass(frozen=True)
class Film:
    width: float = 35.0
    thickness: float = 0.13
    perf_pitch: float = 4.750
    perf_along: float = 1.981
    perf_across: float = 2.794
    perf_edge: float = 2.01
    frame_w: float = 65.0
    frame_h: float = 24.0
    perfs_per_frame: int = 14

    @property
    def advance(self) -> float:
        return self.perfs_per_frame * self.perf_pitch

    @property
    def perf_row_z(self) -> float:
        return self.width / 2 - self.perf_edge - self.perf_across / 2


@dataclass(frozen=True)
class Gate:
    rail_w: float = 1.2
    rail_z: float = 16.6
    recess: float = 0.20
    plate: float = 1.2
    corner_r: float = 0.5
    slot: float = 0.8
    slot_w: float = 72.0
    front_wall: float = 2.0
    aperture_w: float = 67.0
    aperture_h: float = 26.0
    velvet_groove_depth: float = 0.6
    fence_gap: float = 35.3
    bevel: float = 0.3                # rear-side 45 deg bevel on the gate aperture
    slot_bottom_z: float = -15.0      # dark slide bottom stop
    velvet_groove_w: float = 3.0
    velvet_groove_inset: float = 1.0  # chosen: groove inner edge to the front aperture
    fence_w: float = 1.2              # chosen: Print.min_wall
    fence_depth: float = 0.8          # fences stand from Y = 0 back to Y = -0.8
    rail_end_x: float = 46.0          # chosen: rails run on as ribs past the divider until the sprocket teeth engage
    rail_rib_depth: float = 2.0       # film-back.md 13: at least a 2.0mm rail base

    @property
    def slot_y0(self) -> float:
        return self.recess + self.plate

    @property
    def datum_y(self) -> float:
        return self.slot_y0 + self.slot + self.front_wall


@dataclass(frozen=True)
class Shell:
    x_min: float = -77.5
    x_max: float = 97.5
    z_min: float = -30.0
    z_max: float = 31.5
    y_front: float = 30.0
    outer_wall: float = 3.0
    inner_wall: float = 2.2
    divider_wall: float = 2.5
    bridge_half_span: float = 40.0
    ceiling_z: float = 28.5
    rear_rim: float = 4.6
    cover_groove_w: float = 2.2
    cover_thickness: float = 2.5
    pad_sheet: float = 0.25
    pad_foam: float = 2.0
    shoe_end_deg: float = -45.0       # cover shoe arc runs from -90 deg to here
    # Chosen values; film-back.md leaves them open or gives a range.
    y_rear: float = -2.23             # rear rim face = cover inner face at the gate (17.3)
    boss_wall: float = 2.5            # film-back.md 13: wall around a pin or insert hole
    throat_gap: float = 0.6           # film throat at the cassette chamber exit (17.5)
    locator_recess_d: float = 7.0     # cassette bottom locator, for the spool stub
    locator_recess_depth: float = 3.0 # 2.5mm stub + 0.5
    tower_id: float = 7.6
    tower_wall: float = 2.0
    oring_bore: float = 4.8           # O-ring counterbore under the tower top, round the shaft
    oring_depth: float = 1.0
    flange_gap: float = 0.5           # bottom bosses stop this far under the sprocket and spool flanges
    takeup_boss_top_z: float = -26.0  # 0.5mm under the drive collar hub (transport: hub bottom Z -25.5)
    collar_bore: float = 8.4          # sprocket top hub (8.0) passes through this collar
    collar_wall: float = 1.6
    index_mark_w: float = 0.6         # fixed index mark on the collar, at the pawl line
    index_mark_depth: float = 0.4
    cheek_half_len: float = 3.0       # pawl cheeks along the lever, each side of the pivot
    cheek_wall: float = 2.0           # cheek material under the pivot pin hole
    shelf_t: float = 3.0              # pawl spring shelf thickness
    spring_cup_h: float = 1.5         # ring that centres the spring on the shelf
    button_lug_rest_z: float = 29.3   # mirrors Pawl.button_lug_z (transport): lug underside at rest
    button_slot_deg: float = 0.0      # vertical leg of the bayonet slot, plan angle from +X (transport: lug on +X)
    button_hold_deg: float = -90.0    # quarter turn clockwise from above, lug toward -Y, under the ceiling


@dataclass(frozen=True)
class Layout:
    cassette_x: float = -58.5
    cassette_y: float = 12.5
    sprocket_x: float = 55.0
    spool_x: float = 81.0
    spool_y: float = 12.0


@dataclass(frozen=True)
class Sprocket:
    teeth: int = 14
    hub_d: float = 21.04
    relief_d: float = 19.0
    relief_half_h: float = 12.4
    flange_d: float = 23.0
    flange_t: float = 1.0
    flange_gap: float = 35.4
    cam_d: float = 17.0
    cam_z0: float = 20.0
    cam_t: float = 3.0
    notch_w: float = 2.2              # tangential, the pawl tip drops into this width
    notch_len: float = 2.4            # radial; a closed pocket, so the cam rim stays whole
    notch_depth: float = 1.8
    notch_r: float = 6.0
    top_hub_d: float = 8.0
    top_hub_z1: float = 32.5
    index_dot_d: float = 1.5
    index_dot_depth: float = 0.8
    index_dot_inset: float = 1.2      # from the top hub edge
    bore_top_wall: float = 1.5        # closed top keeps light out of the hub
    tooth_root_overlap: float = 0.3   # parallel-sided root sunk into the hub so the union is clean


@dataclass(frozen=True)
class Pawl:
    """Lever on a horizontal pivot. Tip over the cam notch; the button presses the far end."""
    angle_deg: float = 45.0           # plan direction from the sprocket axis toward +X/+Y
    tip_arm: float = 6.0              # tip to pivot
    button_arm: float = 6.0           # pivot to button
    thickness: float = 2.0
    rest_gap: float = 0.2             # lever underside above the cam top at rest
    button_d: float = 6.0
    button_travel: float = 2.5
    # Interface values shared by the shell (cheeks, spring shelf, button collar) and the transport
    # parts (lever, button). Fixed before parallel modeling; change only with both sides.
    pivot_z: float = 24.2             # pivot pin axis, the lever's mid-thickness at rest
    pivot_pin_len: float = 15.0
    width: float = 3.0                # lever width in plan, across its length
    cheek_gap: float = 3.6            # between the shell's pivot cheeks: width + 2 x fdm_clearance
    spring_od: float = 3.5
    spring_free_len: float = 8.0
    spring_shelf_z: float = 17.2      # shell shelf under the button end; spring works at 6.0mm
    button_hole_d: float = 6.6        # collar bore: button_d + 2 x fdm_clearance
    button_lug_w: float = 1.5         # quarter-turn lug on the button, in an L-slot in the collar
    button_lug_len: float = 1.0
    button_lug_h: float = 1.5
    # Chosen while modeling cad/parts/transport.py (film-back.md 8.4 and 17.6 give no values).
    tip_w: float = 1.8                # film-back.md 17.6: tip 1.8mm wide over the 2.2mm pocket
    nose_len: float = 1.8             # along the lever; the pocket is notch_len = 2.4 long
    nose_floor_gap: float = 0.05      # nose underside above the pocket floor at rest
    # The nose face toward the sprocket axis is an arc about the pivot axis of this radius. Turning the
    # lever then slides the face along itself, where a square face swings its bottom corner (7.5mm from
    # the pivot axis) into the pocket wall (7.2mm away). From 7.5 up the nose stays square.
    nose_swing_r: float = 7.0
    button_end: float = 1.5           # lever runs this far past the button axis, so the button face bears on it
    boss_od: float = 5.7              # pivot boss: shaft_bore + 2 x min_wall, rounded up
    tip_chamfer: float = 0.8          # on the tip's top edge, keeps the lifted tip under the ceiling
    spigot_d: float = 2.4             # spring seat under the button end; spring inside diameter is 2.9
    spigot_len: float = 1.5
    spring_wire: float = 0.3          # film-back.md 17.6
    spring_solid_len: float = 2.5     # estimate: about 8 coils of 0.3mm wire
    button_cap_d: float = 6.6         # the advance knob leaves room for no more (cap edge 1.1mm from it)
    button_cap_h: float = 2.5
    button_cap_gap: float = 0.5       # pressed, the cap underside stays this far above the shell top
    button_cap_groove_w: float = 1.0  # fingernail or coin slot across the cap, for the quarter turn
    button_cap_groove_d: float = 0.6
    # The button bears on the lever through a hemispherical nose centred on its axis, so contact is one
    # point at button_arm. A flat face would touch at its inner edge first, because the lever turns about
    # the pivot while the button slides straight down. The pressed contact point is tangent to the lever
    # top at exactly 1.5 (the lever top sits 1.0 above the pivot axis, the button end 6.0 along it); a
    # slightly smaller radius leaves a gap under 0.01mm instead of a tangent clash. The stem face around
    # the nose is relieved by this radius, which also clears the lever top under the stem edge pressed.
    button_nose_r: float = 1.4
    # Lug underside at rest. Pressed 2.5mm, the lug top sits 0.2mm under the ceiling (Z=28.5), so a
    # quarter turn puts it under the top wall and the spring holds the button down (bayonet).
    # The shell's slot for it is a vertical leg through the top wall (28.5 to 31.5), open underneath.
    button_lug_z: float = 29.3


@dataclass(frozen=True)
class TakeUp:
    core_d: float = 16.0
    roll_d_max: float = 24.0
    flange_d: float = 26.0
    knob_d: float = 26.0
    clutch_spring_od: float = 5.0
    clutch_spring_wire: float = 0.4
    # Chosen while modeling cad/parts/transport.py. Z stack of the clutch, bottom to top:
    # shaft bottom -28.8, collar hub -25.5, collar disc -22.5 to -20.5, felt to -19.0, spool -19.0 to +19.0,
    # spring from the spool seat (+16.0) to the ceiling (28.5), knob 32.5 to 42.5.
    flange_t: float = 1.2             # film-back.md 17.7
    flange_gap: float = 35.6          # film-back.md 17.7
    leader_slot_w: float = 1.0        # film-back.md 17.7
    leader_slot_h: float = 20.0       # film-back.md 17.7
    leader_slot_offset: float = 4.5   # chord offset from the axis, toward +Y (front), so the shaft bore stays whole
    spring_seat_d: float = 5.6        # counterbore in the spool top for the clutch spring
    spring_seat_depth: float = 3.0
    clutch_spring_free: float = 15.0  # works at 12.5mm between the seat and the ceiling: 2.5mm preload (tune)
    felt_t: float = 1.5               # bom.md 9: 1-2mm self-adhesive felt, stuck to the collar
    felt_od: float = 14.0
    felt_id: float = 3.5
    collar_od: float = 14.0
    collar_disc_t: float = 2.0
    collar_hub_d: float = 8.0
    collar_hub_len: float = 3.0
    shaft_len: float = 70.0           # bom.md 1
    shaft_bottom_z: float = -28.8     # blind bushing in the floor: leaves 1.2mm (= min_wall) of the 3mm floor
    knob_h: float = 10.0
    knob_z0: float = 32.5             # 1.0mm over the shell top (Z=31.5)
    knob_roof: float = 1.2            # closed top over the shaft end (= min_wall)
    knob_knurl_n: int = 48
    knob_knurl_depth: float = 0.5
    sprocket_pin_len: float = 60.0    # film-back.md 17.6: pressed into the shell floor boss, flush with the floor underside
    sprocket_pin_bottom_z: float = -30.0
    glued_bore: float = 3.2           # epoxy fit on a rod filed flat (collar, knobs, fork)
    rod_flat_depth: float = 0.4       # the D bore's flat sits this far inside the rod radius
    rod_flat_clear: float = 0.05      # the rod's own flat is this much deeper, so flat faces never touch


@dataclass(frozen=True)
class Rewind:
    fork_top_engaged: float = 28.2
    fork_bottom: float = 22.5
    lift: float = 8.0
    tower_top_inside: float = 37.0
    rear_opening_top: float = 28.5
    # Chosen while modeling cad/parts/transport.py (film-back.md 17.5).
    tower_id: float = 7.6
    tower_top_wall: float = 2.0
    fork_od: float = 7.0
    knob_d: float = 20.0
    knob_h: float = 10.0
    knob_gap: float = 0.5             # knob underside over the tower top at rest
    knob_roof: float = 1.2
    knob_knurl_n: int = 36
    knob_knurl_depth: float = 0.4
    shaft_gap_to_roof: float = 0.2    # shaft end sits this far above the fork slot roof, inside the fork bore
    shaft_end_gap: float = 0.1        # shaft end to the knob bore roof
    o_ring_id: float = 3.0            # bom.md 13: 3mm ID x 1mm section
    o_ring_section: float = 1.0
    o_ring_counterbore_d: float = 4.8


@dataclass(frozen=True)
class BodyLink:
    hook_slot_y: tuple = (4.2, 6.2)
    hook_slot_top_z: float = 30.0
    tongue_y: tuple = (4.5, 5.9)
    tongue_top_z: float = 29.7
    latch_pin_z: float = -25.5
    latch_pin_y: float = 8.5
    body_rear_wall: float = 2.5
    latch_cantilever_top_z: float = -27.0
    latch_hook_h: float = 1.8         # reaches 0.3mm above the pin centre so the pin cannot ride out
    detach_deg: float = 5.0           # tilt the tongue's clearance in the hook slot allows (film-back.md 17.8)
    # Film-back side of the interface (film-back.md 17.8); added by the shell stream.
    hook_half_x: float = 36.0
    hook_front_y: float = 7.7
    hook_bottom_z: float = 27.0
    latch_pin_len: float = 48.0
    lug_x: tuple = (22.0, 24.0)       # each lug spans this |X| range
    lug_z: tuple = (-30.0, -22.0)     # chosen: inside the body's latch notch (Z -29 to -21)
    lug_front_y: float = 11.5         # chosen: pin hole + boss wall; the body notch reaches Y +13


@dataclass(frozen=True)
class Cover:
    """Rear cover, turn buttons, slot plug and their bought parts (film-back.md 5, 10, 17.2-17.3).

    Owned by cad/parts/shell.py. Values marked chosen are left open by the docs.
    """
    tongue_w: float = 1.6
    tongue_len: float = 2.5
    groove_depth: float = 3.0
    groove_foam: float = 1.5          # foam strip in the groove bottom
    lap_top: float = 3.0              # chosen: 3mm on the rear face of the top wall + 3mm over the top = 6mm lap
    lap_foam: float = 1.0             # chosen: compressed foam under the top lip
    lip_t: float = 2.5                # chosen: holds the latch groove over a min_wall floor
    pad_w: float = 75.0
    pad_h: float = 33.0
    pad_rim_h: float = 0.5            # chosen: the pad recess is a locating rim on the inner face
    pad_rim_w: float = 1.2
    shoe_start_deg: float = -90.0
    shoe_t: float = 2.0               # chosen: radial thickness of the shoe arc
    shoe_w: float = 34.6
    shoe_film_gap: float = 0.3        # shoe inner radius = hub + film + this
    shoe_groove_w: float = 2.6
    shoe_groove_depth: float = 1.0
    throat_ridge_w: float = 1.9       # chosen: rear land of the film throat, a ridge on the cover
    throat_ridge_half_h: float = 18.5 # chosen: covers the 35mm film band
    # Hinge. Chosen split: the shell carries two 30mm end knuckles with the pin pressed in; the cover's one
    # middle knuckle spins on the pin. The axis sits at the tongue's mid-depth, so the tongue leaves its
    # groove with under 0.2mm of sideways drift, and 0.3mm under the shell bottom so the cover knuckle
    # clears it.
    hinge_pin_len: float = 171.0
    hinge_inset: float = 2.0
    knuckle_od: float = 7.0
    shell_knuckle_len: float = 30.0
    hinge_axis_y: float = -0.98       # Shell.y_rear + tongue_len / 2
    hinge_axis_z: float = -33.8       # Shell.z_min - fdm_clearance - knuckle_od / 2
    open_deg: float = 100.0
    # Turn buttons. Chosen: centre pivot at X = +/-button_x, Y = button_y, clear of the rewind tower,
    # sprocket collar, release button, advance knob and the dark slide handle over a full turn.
    button_len: float = 20.0
    button_w: float = 8.0
    button_t: float = 3.0
    button_x: float = 42.5
    button_y: float = 5.6             # boss edge 0.3mm in front of the cover lip
    button_chamfer: float = 0.5
    # Latch dog: a block under the rear end of each button that drops into an arc groove in the lip top.
    # Opening drives the groove's front wall back into the dog; the groove follows the dog's quarter turn
    # out over the shell top. Chosen: walls each side of the groove >= min_wall, floor = min_wall.
    dog_r: float = 7.5                # dog centre, from the pivot along the button
    dog_t: float = 2.0                # radial
    dog_w: float = 3.0                # across the button
    dog_h: float = 1.0                # below the lip top
    button_release_deg: float = 90.0  # mirrors the turn_buttons drive (mechanisms.py): counter-clockwise from above
    insert_len: float = 5.0           # docs/bom.md M3 x 5 x 4 (measure)
    insert_below: float = 2.0         # insert boss hangs under the ceiling so the hole keeps a floor
    m3_len: float = 8.0
    m3_head_d: float = 5.5
    m3_head_h: float = 3.0
    # Dark slide (docs/bom.md: 71mm wide, about 75mm tall with handle) and slot plug (film-back.md 17.2).
    slide_t: float = 0.5
    slide_w: float = 71.0
    slide_plate_top_z: float = 32.0   # chosen: plate stands 0.5mm proud of the slot mouth
    slide_top_z: float = 60.0
    handle_w: float = 40.0            # chosen: narrower than the slot so the turn buttons sweep past it
    finger_hole_w: float = 24.0
    finger_hole_h: float = 8.0
    plug_t: float = 0.5
    plug_depth: float = 10.0
    plug_grip_w: float = 40.0
    plug_grip_h: float = 5.0
    plug_grip_t: float = 1.6


@dataclass(frozen=True)
class Body:
    """Simple 50mm body (simple-body.md 7-8). Owned by cad/parts/body.py."""
    rear_half_w: float = 39.0         # rear footprint X = +/-39, 1mm inside the bridge span
    z_min: float = -29.0
    z_max: float = 26.5
    wall: float = 2.5
    tongue_half_w: float = 34.0       # mirrors the hook slot X = +/-36 less 2mm (film-back.md 17.8)
    chamber_rear_w: float = 69.0
    chamber_h: float = 28.0
    chamber_front_w: float = 36.0     # the chamber narrows to the M42 bore width
    front_face_y: float = 47.5        # 0.5 behind the cap seat, so the cap seats on the ring only
    m42_floor_y: float = 39.0         # pocket floor; the shim ring fills floor-to-ring
    m42_pocket_gap: float = 0.2       # radial glue gap around the rear cap ring
    m42_shim_min: float = 0.6         # thinnest shim ring worth printing
    m42_shim_id: float = 38.0         # clears the 36mm ring bore
    m42_ring_lip: float = 1.5         # what is left of the rear cap's end wall after cutting it to 36mm
    baffle_y: tuple = (15.0, 27.0)    # rib centres; the M42 pocket floor is the third baffle (doc: Y = +39)
    baffle_t: float = 1.5             # at the opening edge; the rear side runs out at 45 deg to the wall
    baffle_clearance: float = 1.0     # opening outside the image cone
    notch_half_w: float = 25.0
    notch_y1: float = 13.0
    notch_top_z: float = -21.0
    latch_half_w: float = 4.0         # 8mm cantilever
    latch_root_y: float = 25.0        # free length 20.8mm to the hook, strain about 1.2% at 1.8mm flex
    latch_gap: float = 1.0            # air gap around the cantilever in its slot
    latch_ramp: float = 1.8           # 45 deg lead-in on the hook's rear top edge
    tripod_y: float = 32.0
    tripod_boss_d: float = 16.0       # 13.2 across the nut corners + 2 x 1.2 wall (was 14 before the nut moved into the foot)
    seat_clear: float = 0.75          # seat plane below the lowest rear-cover knuckle: a tripod plate clears them, the camera stands on the feet
    tripod_floor: float = 1.2         # under the nut (Print.min_wall); a 5mm screw then engages 3.8mm of it
    foot_x: tuple = (27.0, 35.0)      # each rear foot spans this |X|, clear of the latch notch (|X| <= 25) and the body side wall
    foot_y1: float = 14.0             # rear feet run from the datum face to here
    tripod_screw_hole: float = 6.6    # 1/4"-20 screw clearance
    tripod_screw_depth: float = 5.0   # clearance above the nut for a long screw
    nut_af: float = 11.1              # mirrors docs/bom.md (est.)
    nut_t: float = 5.6
    nut_bore: float = 6.35
    nut_clearance: float = 0.3


@dataclass(frozen=True)
class Viewfinder:
    """Front frame and optional rear sight on the body top (simple-body.md 5 and 7). Owned by cad/parts/body.py.

    The eye point is the rear cover's outer face, Y -4.73: you frame with the camera against your face.
    Each window has the 65:24 shape, sized width = 1.3 x (window plane - eye), the field of the 65 x 24
    frame at 50mm being 0.65 across and 0.24 up. Each window plane is its leaf's front face, axle_y + 2.9.
    The rear sight folds forward, under the raised front frame, and lies low enough to stay out of the field;
    the front frame folds back over it.
    """
    axis_z: float = 40.4              # 0.26mm over 40.14, where the field's lower edge grazes the M42 body cap rim (Z 26.5, Y 50)
    rear_axle_y: float = 12.5         # rear hinge's back edge 0.8mm in front of the film-back top hook
    rear_axle_z: float = 32.3         # 1.1mm over the lowest: the folded sight stays under the field, yet swings clear of the front frame
    front_axle_y: float = 28.0        # the front hinge, kept outside the field, fits the tapering body top up to about Y 28
    front_axle_z: float = 31.2        # the lowest a hinge base carries (min_axle_z); folded, the frame lies over the folded sight
    rear_w: float = 26.17             # 1.3 x 20.13 (eye to rear plane)
    rear_h: float = 9.66              # rear_w x 24 / 65
    front_w: float = 46.32            # 1.3 x 35.63 (eye to front plane)
    front_h: float = 17.10            # front_w x 24 / 65
    leaf_t: float = 1.6
    bar: float = 1.6                  # border round each window
    knuckle_d: float = 6.4            # flats 2.9 from the axis leave min_wall round the 3.3mm bore
    detent_depth: float = 0.3         # knuckle flats sit this far inside its radius; the click
    knuckle_len: float = 3.0
    front_knuckle_inset: float = 0.7  # front knuckles just outside the field's corners behind the window
    rear_knuckle_inset: float = 12.2  # rear knuckles outboard of the folded front frame, 0.5mm clear
    cheek_w: float = 3.0              # pin pressed this deep
    base_t: float = 1.2               # hinge base plate and detent tongue thickness
    base_d: float = 8.0               # hinge base along Y: tongue + two slots + two 1.4mm strips
    tongue_w: float = 4.0
    tongue_len: float = 10.0          # root to the knuckle's inner end: 0.4% strain at the click
    tongue_slot: float = 0.6
    tongue_relief: float = 0.6        # recess in the body top under each tongue, room to flex
    peg_d: float = 3.0                # two pegs on the body top locate each glued hinge base
    peg_h: float = 1.0                # under the 1.2mm base plate, so the plate's holes run through
    peg_inset: float = 3.0            # peg centre inboard of the tongue root
    fold_height: float = 9.5          # folded, nothing rises more than this above the body top (Z 36.0)


@dataclass(frozen=True)
class PinholeModule:
    """Shutter housing, blade, two push tabs and captive lock lever on the M42 body cap (lens.md 2).

    Owned by cad/parts/pinhole.py. X and Z below are camera coordinates on the housing front face.
    """
    cap_boss_len: float = 5.0
    cap_boss_wall: float = 1.5
    cap_drill_d: float = 6.0
    shim_d: float = 12.0
    shim_t: float = 0.05
    shim_recess: float = 0.1
    housing_half: float = 14.0
    rear_plate: float = 1.5
    slot: float = 0.8
    front_plate: float = 1.5
    rear_opening_d: float = 4.0
    front_opening: tuple = (7.0, 4.0)
    # Blade: 0.5mm aluminium, closed pose. +X opens: the blade hole moves onto the pinhole. A full-height
    # middle carries the stop slot; lower tongues run out of both housing ends into the push tabs.
    blade_t: float = 0.5
    blade_h: float = 23.0
    body_x0: float = -13.0            # full-height part, closed; it never leaves the housing
    body_x1: float = 3.5
    blade_side_gap: float = 0.5
    blade_travel: float = 10.0
    blade_hole_d: float = 4.0
    stop_clearance: float = 0.15      # stop slot around the pivot pin, each side; stops sit +/-0.15 from nominal
    # Blade detent: a bump on the channel's rear face, touching the centred blade, and one dimple hole
    # in the blade for each end of the travel.
    detent_x: float = 4.0
    detent_z: float = -7.0
    detent_d: float = 1.2
    dimple_d: float = 1.5
    # Push tabs, glued on the tongue ends. Push the -X tab in to open and the +X tab in to close. At
    # each end of the travel the tab that moves next stands out by the travel more than the other.
    tab_gap: float = 0.5              # near-flush tab to the housing edge
    tab_len: float = 3.5              # along X
    tab_wall: float = 1.5             # above and below the tongue slit
    tab_end_wall: float = 1.2         # push face to the slit bottom
    tab_rear_gap: float = 0.3         # rear face to the body cap front face it slides over
    tab_proud: float = 4.0            # front face ahead of the housing front face
    glue_gap: float = 0.05
    # Lock lever on the upper housing front face, its thumb pad above the housing. The pivot pin also
    # carries the blade's stop slot. The tooth drops into a notch in the top edge of the -X tongue,
    # which is outside the housing only while the shutter is closed. The tongue's top edge sits half
    # the engagement above the pivot, so the push on the tooth runs through the pivot.
    lock_pivot_x: float = 0.0
    lock_pivot_z: float = 7.5
    lock_gap: float = 0.2             # lever rear face to the housing front face
    lock_t: float = 3.0
    lock_hub_r: float = 4.0
    lock_unlock_deg: float = 25.0     # about +Y; the tooth swings up out of the notch, the pad toward +X
    lock_arm_w: float = 3.2
    tooth_x: float = -18.0            # 2mm clear of the housing edge, so it swings up past the corner
    tooth_w: float = 4.0
    tooth_h: float = 4.0
    tooth_engage: float = 2.5         # into the tongue's top edge
    tooth_behind: float = 0.45        # reaches this far behind the blade's rear face
    notch_clearance: float = 0.3
    flag_w: float = 4.0
    flag_len: float = 12.5            # pivot to the thumb pad centre, straight up when locked
    pad_w: float = 8.0
    pad_h: float = 5.0
    pad_depth: float = 6.0            # back from the lever's front face, over the housing top
    # Lever detent: an arc spring finger on the lever, concentric with the pivot, whose nose clicks into
    # two notches in a printed rail on the housing face.
    finger_r: float = 6.5             # beam centre radius
    finger_t: float = 1.2
    finger_root_deg: float = 85.0     # angles in the lever's X-Z frame, 0 = +X, 90 = straight up
    finger_tip_deg: float = 30.0
    nose_r: float = 0.7
    detent_depth: float = 0.4         # radial flex of the finger tip between the notches
    rail_w: float = 1.7
    rail_overrun_deg: float = 8.0     # rail past each notch, so the nose must climb out either way
    notch_play: float = 0.05
    # Pivot: 3mm steel rod pressed into both housing plates; a printed cap pressed on its tip keeps
    # the lever on.
    pivot_len: float = 9.0
    cap_d: float = 7.0
    cap_t: float = 2.5
    cap_gap: float = 0.1              # lever front face to cap


@dataclass(frozen=True)
class Bought:
    """Cassette and film reference solids (docs/bom.md). Owned by cad/parts/film.py."""
    # Cassette. Shell, lip envelope, cap height and spool protrusion are in `Measured`.
    cassette_cap_t: float = 1.0       # end cap thickness, inside the 39.0mm height
    cassette_cap_chamfer: float = 0.3
    spool_key_blade: float = 2.0      # crossbar on the spool tip, inside the fork's 2.6mm slot (measure)
    spool_end_d: float = 6.0          # top key end; not in the BOM, chosen
    spool_stub_len: float = 2.5       # bottom stub, film-back.md 17.5
    spool_stub_d: float = 5.0         # not in the BOM, chosen; fits the 7mm bottom locator recess
    lip_t: float = 0.6                # each felt lip plate
    lip_clearance: float = 0.10       # film to lip, each side
    lip_back: float = 3.0             # lip block starts this far behind the cassette axis
    chamber_y_min: float = -2.2       # cassette chamber rear limit, film-back.md 17.4
    # Film strip.
    film_in_lip: float = 3.0          # the strip starts this far inside the lip tip
    film_phase: float = 0.0           # mm along the strip; 0 puts a perforation on every tooth at rest
    perf_cut_depth: float = 0.5       # perforation cutter thickness; only has to exceed the film
    perf_end_margin: float = 0.2      # no perforation within this of the strip ends
    roll_d: float = 20.0              # mid-roll outer diameter on the take-up spool
    roll_wrap_deg: float = 300.0      # outer wrap shown as a sheet; the rest of the roll is a solid annulus


@dataclass(frozen=True)
class Optics:
    pinhole_d: float = 0.30
    pinhole_y: float = 50.0
    wavelength: float = 0.00055
    m42_bore: float = 36.0
    m42_thread_d: float = 42.0
    m42_depth_behind_pinhole: float = 10.0


@dataclass(frozen=True)
class Print:
    bed: float = 180.0
    min_wall: float = 1.2


@dataclass(frozen=True)
class Camera:
    """All parameter groups. Pass a modified copy (dataclasses.replace) to seed errors."""
    fit: Fit = field(default_factory=Fit)
    measured: Measured = field(default_factory=Measured)
    film: Film = field(default_factory=Film)
    gate: Gate = field(default_factory=Gate)
    shell: Shell = field(default_factory=Shell)
    layout: Layout = field(default_factory=Layout)
    sprocket: Sprocket = field(default_factory=Sprocket)
    pawl: Pawl = field(default_factory=Pawl)
    takeup: TakeUp = field(default_factory=TakeUp)
    rewind: Rewind = field(default_factory=Rewind)
    body_link: BodyLink = field(default_factory=BodyLink)
    cover: Cover = field(default_factory=Cover)
    body: Body = field(default_factory=Body)
    viewfinder: Viewfinder = field(default_factory=Viewfinder)
    pinhole: PinholeModule = field(default_factory=PinholeModule)
    bought: Bought = field(default_factory=Bought)
    optics: Optics = field(default_factory=Optics)
    print: Print = field(default_factory=Print)

    @property
    def pitch_d(self) -> float:
        return self.sprocket.teeth * self.film.perf_pitch / math.pi

    @property
    def sprocket_y(self) -> float:
        return self.sprocket.hub_d / 2

    def pawl_point(self, distance: float) -> tuple[float, float]:
        """Plan position along the pawl line, measured from the sprocket axis."""
        a = math.radians(self.pawl.angle_deg)
        return (self.layout.sprocket_x + distance * math.cos(a), self.sprocket_y + distance * math.sin(a))

    @property
    def pawl_tip(self) -> tuple[float, float]:
        return self.pawl_point(self.sprocket.notch_r)

    @property
    def pawl_pivot(self) -> tuple[float, float]:
        return self.pawl_point(self.sprocket.notch_r + self.pawl.tip_arm)

    @property
    def pawl_button(self) -> tuple[float, float]:
        return self.pawl_point(self.sprocket.notch_r + self.pawl.tip_arm + self.pawl.button_arm)

    @property
    def pawl_tip_lift(self) -> float:
        return self.pawl.button_travel * self.pawl.tip_arm / self.pawl.button_arm

    @property
    def pawl_lifted_top_z(self) -> float:
        cam_top = self.sprocket.cam_z0 + self.sprocket.cam_t
        return cam_top + self.pawl.rest_gap + self.pawl.thickness + self.pawl_tip_lift


CAMERA = Camera()
