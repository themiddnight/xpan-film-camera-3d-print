"""Geometry checks for the transport parts: pawl, release button, take-up stack, rewind fork, knobs and rods."""
import math

from build123d import Axis, Cylinder, Location, Part, Pos, Rot, Vector

from checklib import check
import mechanisms
from parts import PARTS, transport

TRANSPORT_PARTS = list(transport.PARTS)
INTERFERENCE_MM3 = 0.01  # mirrors checks.INTERFERENCE_TOLERANCE_MM3, which this package cannot import
SWEEP_STEP_DEG = 0.5
TOL = 1e-3  # bisection probes are good to about 1e-8; compare with a little slack
PRESS_STEPS = 16
CONTACT_MM = 0.2  # the button must stay this close to the lever, or it does not drive it
STROKE_MARGIN = 0.5
CEILING_MARGIN = 0.4


def _overlap(a: Part, b: Part) -> float:
    shared = a & b
    return shared.volume if shared else 0.0


def _edge(part: Part, start: tuple, end: tuple, iters: int = 30) -> float:
    """Distance from start to the one place on the segment where solid turns to void or back."""
    a, b = Vector(*start), Vector(*end)
    inside_start = part.is_inside(a)
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = (lo + hi) / 2
        if part.is_inside(a + (b - a) * mid) == inside_start:
            lo = mid
        else:
            hi = mid
    return lo * (b - a).length


def _turned_pawl(c, b, deg: float) -> Part:
    axis, pivot = mechanisms.pawl_axis(c)
    return b.placed("pawl").rotate(Axis(pivot, axis), deg)


def _sweep_overlap(c, b, start_deg: float, end_deg: float) -> tuple[float, float]:
    """Largest overlap of the pawl with the sprocket at rest while the lever turns start to end, and where."""
    sprocket = b.placed("sprocket")
    steps = max(1, math.ceil(abs(end_deg - start_deg) / SWEEP_STEP_DEG))
    worst = (0.0, start_deg)
    for i in range(steps + 1):
        deg = start_deg + (end_deg - start_deg) * i / steps
        worst = max(worst, (_overlap(_turned_pawl(c, b, deg), sprocket), deg))
    return worst


def _lifted_pawl(c, b) -> Part:
    pawl = b.local("pawl").rotate(Axis((0, 0, c.pawl.pivot_z), (0, 1, 0)), transport.pawl_lift_deg(c))
    return PARTS["pawl"].place(c) * pawl


def _min_z_over_cam(c, part: Part) -> float:
    cam = Pos(c.layout.sprocket_x, c.sprocket_y, 0) * Cylinder(c.sprocket.cam_d / 2, 100)
    over = part & cam
    return over.bounding_box().min.Z if over else math.inf


@check("pawl nose sits in the cam pocket at rest (geometry)")
def _(c, b):
    s = c.sprocket
    cam_top = s.cam_z0 + s.cam_t
    pawl = b.placed("pawl")
    x, y = c.pawl_tip
    in_tip = pawl.is_inside(Vector(x, y, cam_top - s.notch_depth / 2))
    low = pawl.bounding_box().min.Z
    clash = _overlap(pawl, b.placed("sprocket"))
    depth = cam_top - low
    ok = in_tip and clash < 1e-3 and s.notch_depth - 0.3 <= depth <= s.notch_depth + TOL
    return ok, f"nose in the pocket {depth:.2f}mm of {s.notch_depth}, over the pocket {in_tip}, overlap with the cam {clash:.3f}mm3"


@check("pawl nose fits the pocket (geometry)")
def _(c, b):
    s, p = c.sprocket, c.pawl
    z = s.cam_z0 + s.cam_t - s.notch_depth / 2
    pawl = b.local("pawl")
    wide = 2 * _edge(pawl, (-p.tip_arm, 0, z), (-p.tip_arm, 5, z))
    long = 2 * _edge(pawl, (-p.tip_arm, 0, z), (-p.tip_arm + 5, 0, z))
    ok = 1.5 <= wide <= s.notch_w - 0.2 + TOL and long <= s.notch_len - 0.2 + TOL
    return ok, f"nose {wide:.2f} x {long:.2f}mm in a {s.notch_w} x {s.notch_len}mm pocket"


@check("button travel lifts the pawl clear of the cam (geometry)")
def _(c, b):
    s = c.sprocket
    cam_top = s.cam_z0 + s.cam_t
    rest = _min_z_over_cam(c, b.placed("pawl"))
    lifted = _lifted_pawl(c, b)
    over_cam = _min_z_over_cam(c, lifted)
    rise = over_cam - rest
    ok = rise >= s.notch_depth and over_cam - cam_top >= STROKE_MARGIN
    return ok, (f"{transport.pawl_lift_deg(c):.1f} deg lifts the nose {rise:.2f}mm (pocket {s.notch_depth}mm), "
                f"{over_cam - cam_top:.2f}mm over the cam top")


@check("pawl nose clears the cam pocket the whole way up and down (geometry)")
def _(c, b):
    lift, ride = transport.pawl_lift_deg(c), mechanisms.pawl_ride_deg(c)
    release = _sweep_overlap(c, b, 0.0, lift)
    drop = _sweep_overlap(c, b, ride, 0.0)
    ok = release[0] < INTERFERENCE_MM3 and drop[0] < INTERFERENCE_MM3
    return ok, (f"release 0-{lift:.1f} deg: worst overlap {release[0]:.3f}mm3 at {release[1]:.1f} deg; "
                f"drop {ride:.1f}-0 deg: {drop[0]:.3f}mm3 at {drop[1]:.1f} deg")


@check("release button drives the pawl without sinking into it the whole press (geometry)")
def _(c, b):
    p = c.pawl
    axis, pivot = mechanisms.pawl_axis(c)
    lift = transport.pawl_lift_deg(c)
    pawl, button = b.placed("pawl"), b.placed("release_button")
    worst_clash, worst_gap = (0.0, 0.0), (0.0, 0.0)
    for i in range(PRESS_STEPS + 1):
        v = i / PRESS_STEPS
        pressed = button.moved(Location((0, 0, -v * p.button_travel)))
        turned = pawl.rotate(Axis(pivot, axis), v * lift)
        worst_clash = max(worst_clash, (_overlap(pressed, turned), v))
        worst_gap = max(worst_gap, (pressed.distance_to(turned), v))
    ok = worst_clash[0] < INTERFERENCE_MM3 and worst_gap[0] <= CONTACT_MM
    return ok, (f"press 0-{p.button_travel}mm: worst overlap {worst_clash[0]:.3f}mm3 at {worst_clash[1]:.2f} of the stroke, "
                f"worst gap {worst_gap[0]:.3f}mm at {worst_gap[1]:.2f}")


@check("lifted pawl lever clears the ceiling (geometry)")
def _(c, b):
    top = _lifted_pawl(c, b).bounding_box().max.Z
    return c.shell.ceiling_z - top >= CEILING_MARGIN, f"lever top {top:.2f} lifted, ceiling {c.shell.ceiling_z}"


@check("pawl spring seats on the spigot and works between free and solid (geometry)")
def _(c, b):
    p = c.pawl
    z0 = transport.lever_z(c)[0]
    pawl = b.local("pawl")
    spigot_d = 2 * _edge(pawl, (p.button_arm, 0, z0 - 0.7), (p.button_arm, 5, z0 - 0.7))
    spigot_bottom = z0 - _edge(pawl, (p.button_arm, 0, z0 - 0.5), (p.button_arm, 0, z0 - 3))
    inside = p.spring_od - 2 * p.spring_wire
    working = z0 - p.spring_shelf_z
    pressed = working - p.button_travel
    spigot_gap = spigot_bottom - p.button_travel - p.spring_shelf_z
    ok = (spigot_d <= inside - 0.3 + TOL and p.spring_free_len - working >= 1.0 - TOL
          and pressed >= p.spring_solid_len + 0.5 - TOL and spigot_gap >= 0.5 - TOL)
    return ok, (f"spigot {spigot_d:.2f} in spring {inside:.2f}mm, spring {working:.1f}mm of {p.spring_free_len}mm free, "
                f"{pressed:.1f}mm pressed (solid about {p.spring_solid_len}), spigot {spigot_gap:.1f}mm over the shelf pressed")


@check("pawl bore and spool bore fit the 3mm pin (geometry)")
def _(c, b):
    pin = c.measured.rod_d
    pawl_d = 2 * _edge(b.local("pawl"), (0, 0, c.pawl.pivot_z), (0, 0, c.pawl.pivot_z + 2.5))
    spool_d = 2 * _edge(b.local("takeup_spool"), (0, 0, 0), (2.5, 0, 0))
    gaps = (pawl_d - pin, spool_d - pin)
    ok = all(0.15 <= g <= 0.5 and abs(g + pin - c.fit.shaft_bore) < 0.02 for g in gaps)
    return ok, f"pawl bore {pawl_d:.2f}, spool bore {spool_d:.2f} on a {pin}mm pin (Fit.shaft_bore {c.fit.shaft_bore})"


@check("take-up spool leader slot passes the film and spares the shaft bore (geometry)")
def _(c, b):
    t = c.takeup
    spool = b.local("takeup_spool")
    y, x = t.leader_slot_offset, t.core_d / 4
    width = 2 * _edge(spool, (x, y, 0), (x, y + 3, 0))
    height = 2 * _edge(spool, (x, y, 0), (x, y, 15))
    web = y - width / 2 - c.fit.shaft_bore / 2
    ok = width >= c.film.thickness + 0.4 and abs(width - t.leader_slot_w) < 0.01 and abs(height - t.leader_slot_h) < 0.01 and web >= c.print.min_wall - TOL
    return ok, f"slot {width:.2f} x {height:.1f}mm, {web:.2f}mm of core between it and the bore"


@check("glued bores fit the filed rod without touching it (geometry)")
def _(c, b):
    pin = c.measured.rod_d
    pairs = (("drive_collar", "takeup_shaft", transport.collar_z(c)[1] - 1.0),
             ("advance_knob", "takeup_shaft", transport.advance_knob_z(c)[0] + 2.0),
             ("rewind_fork", "rewind_shaft", c.rewind.fork_top_engaged - 0.5),
             ("rewind_knob", "rewind_shaft", transport.rewind_knob_z(c)[0] + 2.0))
    worst_gap, worst_clash = 9.0, 0.0
    for printed, rod, z in pairs:
        gap = 2 * _edge(b.local(printed), (0, 0, z), (0, 2.5, z)) - pin
        worst_gap = min(worst_gap, gap)
        worst_clash = max(worst_clash, _overlap(b.placed(printed), b.placed(rod)))
    return 0.1 <= worst_gap <= 0.4 and worst_clash < 1e-3, f"smallest bore gap {worst_gap:.2f}mm, largest overlap with a rod {worst_clash:.3f}mm3"


@check("release button fits its collar bore (geometry)")
def _(c, b):
    z = transport.button_cap_z0(c) - 2.0
    stem_d = 2 * _edge(b.local("release_button"), (0, 0, z), (0, 5, z))
    gap = (c.pawl.button_hole_d - stem_d) / 2
    return c.fit.fdm_clearance - TOL <= gap <= 0.5, f"stem {stem_d:.2f}mm in a {c.pawl.button_hole_d}mm bore, {gap:.2f}mm each side"


@check("release button rests on the pawl button end (geometry)")
def _(c, b):
    lever_top = transport.lever_z(c)[1]
    pawl, button = b.placed("pawl"), b.placed("release_button")
    bx, by = c.pawl_button
    under = pawl.is_inside(Vector(bx, by, lever_top - 0.1))
    past_x, past_y = c.pawl_point(c.sprocket.notch_r + c.pawl.tip_arm + c.pawl.button_arm + 1.0)
    past = pawl.is_inside(Vector(past_x, past_y, lever_top - 0.1))
    bottom = button.bounding_box().min.Z
    return under and past and abs(bottom - lever_top) < 0.05, f"button underside {bottom:.2f}, lever top {lever_top:.2f}, lever under the axis {under}, 1mm past it {past}"


@check("release button stroke fits under the cap (geometry)")
def _(c, b):
    p = c.pawl
    button = b.local("release_button")
    cap_z0 = transport.lever_z(c)[1] + _edge(button, (3.15, 0, transport.lever_z(c)[1]), (3.15, 0, transport.lever_z(c)[1] + 14))
    left = cap_z0 - p.button_travel - c.shell.z_max
    return left >= c.fit.fdm_clearance - TOL, f"cap underside {cap_z0:.2f}, pressed {cap_z0 - p.button_travel:.2f}, shell top {c.shell.z_max}"


@check("release button lug passes under the ceiling when pressed (geometry)")
def _(c, b):
    p = c.pawl
    button = b.local("release_button")
    lug_x = p.button_d / 2 + p.button_lug_len / 2
    mid = p.button_lug_z + p.button_lug_h / 2
    top = mid + _edge(button, (lug_x, 0, mid), (lug_x, 0, mid + 3))
    ok = top - p.button_travel <= c.shell.ceiling_z - 0.1 and p.button_lug_z >= c.shell.ceiling_z - TOL and top <= c.shell.z_max + TOL
    return ok, f"lug {p.button_lug_z:.1f} to {top:.1f} at rest, top {top - p.button_travel:.1f} pressed, ceiling {c.shell.ceiling_z}, shell top {c.shell.z_max}"


@check("release button cap clears the advance knob (geometry)")
def _(c, b):
    gap = b.placed("release_button").distance_to(b.placed("advance_knob"))
    return gap >= 1.0 - TOL, f"{gap:.2f}mm"


@check("knobs clear the shell top and the rewind tower (geometry)")
def _(c, b):
    advance_gap = b.placed("advance_knob").bounding_box().min.Z - c.shell.z_max
    tower_top = c.rewind.tower_top_inside + c.rewind.tower_top_wall
    rewind_gap = b.placed("rewind_knob").bounding_box().min.Z - tower_top
    ok = min(advance_gap, rewind_gap) >= c.fit.fdm_clearance - TOL
    return ok, f"advance knob {advance_gap:.2f}mm over the shell top, rewind knob {rewind_gap:.2f}mm over the tower top"


@check("take-up spool flanges clear the sprocket flange (geometry)")
def _(c, b):
    gap = b.placed("takeup_spool").distance_to(b.placed("sprocket"))
    return gap >= 1.0 - TOL, f"{gap:.2f}mm"


@check("take-up clutch stack closes with spring preload (geometry)")
def _(c, b):
    t = c.takeup
    collar_top = b.placed("drive_collar").bounding_box().max.Z
    felt, spool, spring = (b.placed(n).bounding_box() for n in ("felt_washer", "takeup_spool", "clutch_spring"))
    seat = transport.spool_z(c)[1] - _edge(b.local("takeup_spool"), (2.2, 0, transport.spool_z(c)[1]), (2.2, 0, transport.spool_z(c)[1] - 6))
    working = spring.size.Z
    preload = t.clutch_spring_free - working
    stack_ok = abs(felt.min.Z - collar_top) < 0.05 and abs(felt.max.Z - spool.min.Z) < 0.05 and abs(spring.min.Z - seat) < 0.05
    ok = stack_ok and 1.0 <= preload <= 4.0 and spring.max.Z <= c.shell.ceiling_z + TOL
    return ok, (f"collar top {collar_top:.2f}, felt {felt.min.Z:.2f} to {felt.max.Z:.2f}, spool from {spool.min.Z:.2f}, "
                f"spring {spring.min.Z:.2f} to {spring.max.Z:.2f} on a seat at {seat:.2f}, {preload:.1f}mm preload")


@check("take-up shaft seats in the floor and the knob (geometry)")
def _(c, b):
    shaft = b.placed("takeup_shaft").bounding_box()
    knob = b.local("advance_knob")
    z0, z1 = transport.advance_knob_z(c)
    roof = z0 + 2.0 + _edge(knob, (0, 0.5, z0 + 2.0), (0, 0.5, z1 + 1))
    floor_left = shaft.min.Z - c.shell.z_min
    ok = floor_left >= c.print.min_wall - TOL and shaft.max.Z <= roof + TOL and z1 - roof >= c.print.min_wall - TOL
    return ok, f"{floor_left:.2f}mm of floor under the shaft, shaft top {shaft.max.Z:.2f} under a knob roof at {roof:.2f} ({z1 - roof:.2f}mm thick)"


@check("rewind fork engages the spool key over its full depth (geometry)")
def _(c, b):
    m, r = c.measured, c.rewind
    tip = m.cassette_cap_height / 2 + m.spool_top_protrusion
    fork = b.local("rewind_fork")
    bottom = fork.bounding_box().min.Z
    roof = bottom + 0.1 + _edge(fork, (2.0, 0, bottom + 0.1), (2.0, 0, r.fork_top_engaged))
    slot_w = 2 * _edge(fork, (2.0, 0, bottom + 1.0), (2.0, 4, bottom + 1.0))
    ok = roof >= tip - TOL and bottom <= tip - m.spool_key_depth + TOL and slot_w >= m.spool_key_slot - TOL
    return ok, f"key tip {tip}, key from {tip - m.spool_key_depth}; fork bottom {bottom:.2f}, slot roof {roof:.2f}, slot {slot_w:.2f}mm wide (key slot {m.spool_key_slot})"


@check("rewind fork lifts inside the tower and clear of the spool (geometry)")
def _(c, b):
    r, m = c.rewind, c.measured
    fork = b.local("rewind_fork").bounding_box()
    tip = m.cassette_cap_height / 2 + m.spool_top_protrusion
    room = r.tower_top_inside - (fork.max.Z + r.lift)
    side = (r.tower_id - fork.size.X) / 2
    above_tip = fork.min.Z + r.lift - tip
    ok = room >= 0.5 - TOL and side >= c.fit.fdm_clearance - TOL and above_tip >= 1.0 - TOL
    return ok, f"{room:.2f}mm under the tower top lifted, {side:.2f}mm each side in the tower, bottom {above_tip:.1f}mm over the spool tip lifted"


@check("rewind shaft clears the fork slot and stops in the knob (geometry)")
def _(c, b):
    shaft = b.placed("rewind_shaft").bounding_box()
    knob = b.local("rewind_knob")
    z0, z1 = transport.rewind_knob_z(c)
    roof = z0 + 2.0 + _edge(knob, (0, 0.5, z0 + 2.0), (0, 0.5, z1 + 1))
    slot_roof = transport.rewind_slot_roof_z(c)
    ok = shaft.min.Z >= slot_roof - TOL and shaft.max.Z <= roof + TOL and z1 - roof >= c.print.min_wall - TOL
    return ok, f"shaft {shaft.min.Z:.2f} to {shaft.max.Z:.2f}, slot roof {slot_roof:.2f}, knob roof {roof:.2f} ({z1 - roof:.2f}mm thick)"


@check("sprocket pin passes the bore and stops under the hub top (geometry)")
def _(c, b):
    pin = b.placed("sprocket_pin").bounding_box()
    s = c.sprocket
    roof = s.cam_z0 + _edge(b.local("sprocket"), (0, 0, s.cam_z0), (0, 0, s.top_hub_z1))
    ok = pin.max.Z <= roof - 0.5 + TOL and pin.min.Z >= c.shell.z_min - TOL and abs(pin.size.Z - c.takeup.sprocket_pin_len) < 1e-6
    return ok, f"pin {pin.min.Z:.1f} to {pin.max.Z:.1f}, bore roof {roof:.1f}, floor underside {c.shell.z_min}"


@check("transport parts do not overlap each other (geometry)")
def _(c, b):
    placed = {n: b.placed(n) for n in TRANSPORT_PARTS}
    boxes = {n: p.bounding_box() for n, p in placed.items()}
    clashes = []
    for i, a in enumerate(TRANSPORT_PARTS):
        for n in TRANSPORT_PARTS[i + 1:]:
            ba, bn = boxes[a], boxes[n]
            apart = any(hi_a <= lo_n or hi_n <= lo_a for lo_a, hi_a, lo_n, hi_n in zip(
                tuple(ba.min), tuple(ba.max), tuple(bn.min), tuple(bn.max)))
            if not apart and _overlap(placed[a], placed[n]) > 1e-3:
                clashes.append(f"{a}/{n}")
    return not clashes, f"overlapping pairs: {clashes or 'none'}"


@check("printed transport parts fit the print bed (geometry)")
def _(c, b):
    worst = 0.0
    for name in TRANSPORT_PARTS:
        spec = PARTS[name]
        if spec.print_rotation is not None:
            size = (Rot(*spec.print_rotation) * b.local(name)).bounding_box().size
            worst = max(worst, size.X, size.Y)
    return worst <= c.print.bed, f"largest footprint {worst:.1f}mm of {c.print.bed}mm"
