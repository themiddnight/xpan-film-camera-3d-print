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
    pin_press_hole: float = 2.90      # press fit for a 3.0mm steel pin (tune; a Fit value, kept here until Fit has one)
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


@dataclass(frozen=True)
class TakeUp:
    core_d: float = 16.0
    roll_d_max: float = 24.0
    flange_d: float = 26.0
    knob_d: float = 26.0
    clutch_spring_od: float = 5.0
    clutch_spring_wire: float = 0.4


@dataclass(frozen=True)
class Rewind:
    fork_top_engaged: float = 28.2
    fork_bottom: float = 22.5
    lift: float = 8.0
    tower_top_inside: float = 37.0
    rear_opening_top: float = 28.5


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
    lip_t: float = 2.0                # chosen
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


@dataclass(frozen=True)
class Viewfinder:
    """Wire-frame finder and its hinge blocks (simple-body.md 5 and 7). Owned by cad/parts/body.py."""


@dataclass(frozen=True)
class PinholeModule:
    """Shutter housing, blade and lock pin on the M42 body cap (lens.md 2). Owned by cad/parts/pinhole.py."""


@dataclass(frozen=True)
class Bought:
    """Cassette and film reference solids (docs/bom.md). Owned by cad/parts/film.py."""


@dataclass(frozen=True)
class Optics:
    pinhole_d: float = 0.30
    pinhole_y: float = 50.0
    wavelength: float = 0.00055
    m42_bore: float = 36.0
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
