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


@dataclass(frozen=True)
class Cover:
    """Rear cover, turn buttons and slot plug (film-back.md 17.3). Owned by cad/parts/shell.py."""


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
    tripod_boss_d: float = 14.0
    tripod_proud: float = 0.5         # boss face below the film-back bottom, so a tripod plate seats on it
    tripod_floor: float = 2.0         # under the nut
    tripod_screw_hole: float = 6.6    # 1/4"-20 screw clearance
    tripod_screw_depth: float = 5.0   # clearance above the nut for a long screw
    nut_af: float = 11.1              # mirrors docs/bom.md (est.)
    nut_t: float = 5.6
    nut_bore: float = 6.35
    nut_clearance: float = 0.3
    hinge_pocket_depth: float = 1.5


@dataclass(frozen=True)
class Viewfinder:
    """Wire-frame finder and its hinge blocks (simple-body.md 5 and 7). Owned by cad/parts/body.py."""
    wire_d: float = 1.0
    frame_w: float = 104.0
    frame_h: float = 38.4
    peep_to_frame: float = 80.0
    peep_d: float = 3.0
    axle_y: float = 42.0
    axle_z: float = 33.0              # folded arms clear the 31.5 film-back top
    hinge_x: float = 22.0
    block_w: float = 6.0
    block_d: float = 8.0
    block_above_axle: float = 2.5
    tenon_w: float = 4.0
    tenon_d: float = 6.0
    wire_hole: float = 1.3
    arm_x: float = 37.5               # rear arms pass outside the 71mm dark slide
    arm_bend_y: float = 8.0


@dataclass(frozen=True)
class PinholeModule:
    """Shutter housing, blade and lock pin on the M42 body cap (lens.md 2). Owned by cad/parts/pinhole.py."""
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
    blade_t: float = 0.5
    blade_len: float = 32.0
    blade_h: float = 23.0
    blade_side_gap: float = 0.5
    blade_travel: float = 10.0        # +X opens: the blade hole moves onto the pinhole
    blade_hole_d: float = 4.0
    detent_x: float = -6.0
    detent_z: float = 8.0
    detent_d: float = 1.2
    detent_h: float = 0.25
    dimple_d: float = 1.5
    pin_z: float = -8.0               # below the pinhole, outside the 27 deg vertical field
    pin_len: float = 20.0
    pin_boss_d: float = 7.0
    pin_boss_len: float = 6.0
    blade_pin_hole: float = 3.2


@dataclass(frozen=True)
class Bought:
    """Cassette and film reference solids (docs/bom.md). Owned by cad/parts/film.py."""
    # Cassette. Shell, lip envelope, cap height and spool protrusion are in `Measured`.
    cassette_cap_t: float = 1.0       # end cap thickness, inside the 39.0mm height
    cassette_cap_chamfer: float = 0.3
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
