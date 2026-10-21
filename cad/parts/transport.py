"""Pawl, release button, take-up clutch stack, rewind fork and knobs, and the bought rods and springs.

Every part is built at rest in an own frame whose Z is the camera Z and whose origin sits on the part's
axis; `place` moves it to its camera position (docs/superpowers/specs/2026-10-22-phase3-4-parts.md).

Values chosen here where the docs give a range or nothing (all live in params.py, `Pawl`, `TakeUp`, `Rewind`):
- Pawl: the lever runs from u = -(tip_arm + nose_len / 2) to u = button_arm + button_end along the 45 deg line
  (u = 0 at the pivot, + toward the button). A 1.8 x 1.8mm nose drops from the tip underside into the pocket
  and rests 0.05mm above the pocket floor, so the lever underside stays 0.2mm over the cam when the spring
  presses the nose down. Its face toward the sprocket axis is an arc of 7.0mm about the pivot axis, so the
  lower corner does not swing into the pocket wall as the lever turns. The pivot boss is 5.7mm OD. A 2.4mm spigot under the button end seats the spring.
  The lever prints on its side; the nose and spigot need tiny supports.
- Release button: 6.6mm cap, 2.5mm tall, with a coin slot for the quarter turn. The cap is as wide as the
  advance knob allows (1.1mm to it). The lug sits so that pressed it is 0.2mm under the ceiling, and a
  quarter turn puts it under the top wall (bayonet hold). Its stem is guided only by the 3mm top wall.
  Nothing retains the button when the camera is upside down.
- Take-up Z stack (bottom to top): shaft bottom -28.8 (1.2mm of floor left under it), collar hub -25.5 to
  -22.5, collar disc -22.5 to -20.5, felt -20.5 to -19.0, spool -19.0 to +19.0, clutch spring from the
  spool seat (+16.0) to the ceiling (+28.5), knob 32.5 to 42.5. The spring pushes the spool down onto the
  felt on the collar and the shaft down onto the floor; its top end slides on the ceiling. The felt is stuck
  to the collar, so the spool slips on it.
- The leader slot is a chord 4.5mm off the axis, so the shaft bore stays whole.
- Shafts: knobs, fork and collar are epoxied on a rod filed flat, so their bores are D-shaped (3.2mm round,
  flat 1.1mm from the axis on the local -Y side) and the rods carry a deeper flat (1.05mm) over those lengths.
- Take-up shaft 70mm from -28.8 to +41.2 (blind bushing hole in the floor), not -30 to +42 (72mm).
- Rewind shaft stops at the fork slot roof (+27.2) because 3.0mm cannot pass the 2.6mm slot. Its top sits
  0.1mm under the knob bore roof (+48.2), so it is 21mm long, not the 27mm in film-back.md 17.5.
- Rewind O-ring sits in the 4.8mm counterbore at the tower top, Z 37.0 to 38.0. It stays put when the
  shaft lifts.
- Springs are tubes at their working length, not helices.
- Sprocket pin: 60mm, Z -30 to +30, flush with the floor underside and 1mm under the closed hub top.
"""
import math

from build123d import Axis, Box, Cone, Cylinder, GeomType, Location, Part, Polygon, Pos, Rot, Torus, chamfer, extrude, fillet

from params import Camera
from parts.spec import PartSpec

PRINTED_COLOR = "#2f2f33"
LEVER_COLOR = "#c0462d"
STEEL = "#b8bcc4"
SPRING = "#d8b45a"
FELT = "#5b4636"
RUBBER = "#151515"


# Derived positions, shared by the builders, the placements and the checks.

def pawl_lift_deg(c: Camera) -> float:
    """Lever rotation when the button is pressed its full travel; the tip rises by travel x tip_arm / button_arm."""
    return math.degrees(math.asin(c.pawl.button_travel / c.pawl.button_arm))


def lever_z(c: Camera) -> tuple[float, float]:
    """Lever underside and top at rest: a rest gap above the cam."""
    z0 = c.sprocket.cam_z0 + c.sprocket.cam_t + c.pawl.rest_gap
    return z0, z0 + c.pawl.thickness


def button_cap_z0(c: Camera) -> float:
    return c.shell.z_max + c.pawl.button_travel + c.pawl.button_cap_gap


def spool_z(c: Camera) -> tuple[float, float]:
    half = c.takeup.flange_gap / 2 + c.takeup.flange_t
    return -half, half


def felt_z(c: Camera) -> tuple[float, float]:
    spool_bottom = spool_z(c)[0]
    return spool_bottom - c.takeup.felt_t, spool_bottom


def collar_z(c: Camera) -> tuple[float, float]:
    """Hub bottom and disc top."""
    disc_top = felt_z(c)[0]
    return disc_top - c.takeup.collar_disc_t - c.takeup.collar_hub_len, disc_top


def spring_seat_z(c: Camera) -> float:
    return spool_z(c)[1] - c.takeup.spring_seat_depth


def takeup_shaft_z(c: Camera) -> tuple[float, float]:
    return c.takeup.shaft_bottom_z, c.takeup.shaft_bottom_z + c.takeup.shaft_len


def advance_knob_z(c: Camera) -> tuple[float, float]:
    return c.takeup.knob_z0, c.takeup.knob_z0 + c.takeup.knob_h


def rewind_slot_roof_z(c: Camera) -> float:
    return c.rewind.fork_bottom + c.measured.spool_key_depth


def rewind_knob_z(c: Camera) -> tuple[float, float]:
    z0 = c.rewind.tower_top_inside + c.rewind.tower_top_wall + c.rewind.knob_gap
    return z0, z0 + c.rewind.knob_h


def rewind_shaft_z(c: Camera) -> tuple[float, float]:
    bore_roof = rewind_knob_z(c)[1] - c.rewind.knob_roof
    return rewind_slot_roof_z(c) + c.rewind.shaft_gap_to_roof, bore_roof - c.rewind.shaft_end_gap


# Shared shapes.

def _cylinder(r: float, z0: float, z1: float) -> Part:
    return Pos(0, 0, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def _tube(od: float, wall: float, z0: float, z1: float) -> Part:
    return _cylinder(od / 2, z0, z1) - _cylinder(od / 2 - wall, z0 - 1, z1 + 1)


def _rod_flat_y(c: Camera) -> float:
    """Y of the D bore's flat, on the local -Y side."""
    return -(c.measured.rod_d / 2 - c.takeup.rod_flat_depth)


def _d_bore(c: Camera, z0: float, z1: float) -> Part:
    h = z1 - z0
    return _cylinder(c.takeup.glued_bore / 2, z0, z1) & (Pos(0, _rod_flat_y(c) + 5, (z0 + z1) / 2) * Box(10, 10, h))


def _flatted_rod(c: Camera, z0: float, z1: float, flat_zones: list[tuple[float, float]]) -> Part:
    rod = _cylinder(c.measured.rod_d / 2, z0, z1)
    flat_y = _rod_flat_y(c) + c.takeup.rod_flat_clear
    for a, b in flat_zones:
        if b > a:
            rod -= Pos(0, flat_y - 5, (a + b) / 2) * Box(10, 10, b - a)
    return rod


def _knurled(d: float, z0: float, z1: float, n: int, depth: float) -> Part:
    """Straight knurl (sawtooth outline) with a chamfered top edge."""
    r_out, r_in = d / 2, d / 2 - depth
    points = [((r_out if i % 2 == 0 else r_in) * math.cos(math.pi * i / n),
               (r_out if i % 2 == 0 else r_in) * math.sin(math.pi * i / n)) for i in range(2 * n)]
    body = Pos(0, 0, z0) * extrude(Polygon(*points, align=None), amount=z1 - z0)
    ch = 0.8
    envelope = _cylinder(r_out, z0, z1 - ch) + Pos(0, 0, z1 - ch / 2) * Cone(r_out, r_out - ch, ch)
    return body & envelope


def _knob(c: Camera, d: float, z0: float, z1: float, bore_top: float, n: int, depth: float) -> Part:
    return _knurled(d, z0, z1, n, depth) - _d_bore(c, z0 - 0.1, bore_top)


# Pawl and release button.

def build_pawl(c: Camera) -> Part:
    """Local frame: origin on the pivot axis in plan, +X toward the button, pivot axis along Y."""
    p, s, f = c.pawl, c.sprocket, c.fit
    z0, z1 = lever_z(c)
    u_tip = -p.tip_arm - p.nose_len / 2
    u_end = p.button_arm + p.button_end

    lever = Pos((u_tip + u_end) / 2, 0, (z0 + z1) / 2) * Box(u_end - u_tip, p.width, p.thickness)
    lever = chamfer(lever.edges().filter_by(Axis.Y).filter_by_position(Axis.X, u_tip - 0.01, u_tip + 0.01)
                    .filter_by_position(Axis.Z, z1 - 0.01, z1 + 0.01), p.tip_chamfer)
    lever = fillet(lever.edges().filter_by(Axis.Z).filter_by_position(Axis.X, u_end - 0.01, u_end + 0.01), 1.0)

    boss = Pos(0, 0, p.pivot_z) * Rot(90, 0, 0) * Cylinder(p.boss_od / 2, p.width)
    nose_bottom = s.cam_z0 + s.cam_t - s.notch_depth + p.nose_floor_gap
    nose = Pos(-p.tip_arm, 0, (nose_bottom + z0 + 0.1) / 2) * Box(p.nose_len, p.tip_w, z0 + 0.1 - nose_bottom)
    nose &= Pos(0, 0, p.pivot_z) * Rot(90, 0, 0) * Cylinder(p.nose_swing_r, p.tip_w + 1)
    spigot = Pos(p.button_arm, 0, 0) * _cylinder(p.spigot_d / 2, z0 - p.spigot_len, z0 + 0.1)

    part = lever + boss + nose + spigot
    part -= Pos(0, 0, p.pivot_z) * Rot(90, 0, 0) * Cylinder(f.shaft_bore / 2, p.width + 2)
    return part


def build_release_button(c: Camera) -> Part:
    """Local frame: origin on the button axis. The lug points along +X."""
    p = c.pawl
    lever_top = lever_z(c)[1]
    cap_z0 = button_cap_z0(c)
    cap_z1 = cap_z0 + p.button_cap_h

    stem = chamfer(_cylinder(p.button_d / 2, lever_top, cap_z0 + 0.1).edges().filter_by_position(Axis.Z, lever_top - 0.01, lever_top + 0.01), 0.5)
    cap = chamfer(_cylinder(p.button_cap_d / 2, cap_z0, cap_z1).edges().filter_by_position(Axis.Z, cap_z1 - 0.01, cap_z1 + 0.01), 0.5)
    cap -= Pos(0, 0, cap_z1 - p.button_cap_groove_d / 2 + 0.05) * Box(p.button_cap_d + 1, p.button_cap_groove_w, p.button_cap_groove_d + 0.1)
    lug_x0, lug_x1 = p.button_d / 2 - 0.2, p.button_d / 2 + p.button_lug_len
    lug = Pos((lug_x0 + lug_x1) / 2, 0, p.button_lug_z + p.button_lug_h / 2) * Box(lug_x1 - lug_x0, p.button_lug_w, p.button_lug_h)
    return stem + cap + lug


# Take-up: spool, collar, knob.

def build_takeup_spool(c: Camera) -> Part:
    t, f = c.takeup, c.fit
    z0, z1 = spool_z(c)
    part = _cylinder(t.core_d / 2, z0, z1)
    for lo, hi in ((z0, z0 + t.flange_t), (z1 - t.flange_t, z1)):
        part += _cylinder(t.flange_d / 2, lo, hi)
    part -= _cylinder(f.shaft_bore / 2, z0 - 1, z1 + 1)
    part -= _cylinder(t.spring_seat_d / 2, spring_seat_z(c), z1 + 1)
    part -= Pos(0, t.leader_slot_offset, 0) * Box(t.core_d + 2, t.leader_slot_w, t.leader_slot_h)
    return part


def build_drive_collar(c: Camera) -> Part:
    t = c.takeup
    hub_bottom, disc_top = collar_z(c)
    disc_bottom = disc_top - t.collar_disc_t
    part = _cylinder(t.collar_od / 2, disc_bottom, disc_top) + _cylinder(t.collar_hub_d / 2, hub_bottom, disc_bottom + 0.1)
    return part - _d_bore(c, hub_bottom - 1, disc_top + 1)


def build_advance_knob(c: Camera) -> Part:
    t = c.takeup
    z0, z1 = advance_knob_z(c)
    return _knob(c, t.knob_d, z0, z1, z1 - t.knob_roof, t.knob_knurl_n, t.knob_knurl_depth)


# Rewind: fork and knob.

def build_rewind_fork(c: Camera) -> Part:
    r, m = c.rewind, c.measured
    z0, z1 = r.fork_bottom, r.fork_top_engaged
    fork = _cylinder(r.fork_od / 2, z0, z1)
    fork -= Pos(0, 0, z0 + m.spool_key_depth / 2 - 0.5) * Box(r.fork_od + 2, m.spool_key_slot, m.spool_key_depth + 1)
    mouth = fork.edges().filter_by(GeomType.LINE).filter_by_position(Axis.Z, z0 - 0.01, z0 + 0.01)
    fork = chamfer(mouth, 0.4)
    return fork - _d_bore(c, rewind_slot_roof_z(c) - 0.05, z1 + 1)


def build_rewind_knob(c: Camera) -> Part:
    r = c.rewind
    z0, z1 = rewind_knob_z(c)
    return _knob(c, r.knob_d, z0, z1, z1 - r.knob_roof, r.knob_knurl_n, r.knob_knurl_depth)


# Bought parts.

def build_sprocket_pin(c: Camera) -> Part:
    bottom = c.takeup.sprocket_pin_bottom_z
    return _cylinder(c.measured.rod_d / 2, bottom, bottom + c.takeup.sprocket_pin_len)


def build_takeup_shaft(c: Camera) -> Part:
    z0, z1 = takeup_shaft_z(c)
    return _flatted_rod(c, z0, z1, [(collar_z(c)[0], collar_z(c)[1]), (advance_knob_z(c)[0], z1)])


def build_rewind_shaft(c: Camera) -> Part:
    z0, z1 = rewind_shaft_z(c)
    return _flatted_rod(c, z0, z1, [(z0, c.rewind.fork_top_engaged), (rewind_knob_z(c)[0], z1)])


def build_pawl_pin(c: Camera) -> Part:
    return Pos(0, 0, c.pawl.pivot_z) * Rot(90, 0, 0) * Cylinder(c.measured.rod_d / 2, c.pawl.pivot_pin_len)


def build_pawl_spring(c: Camera) -> Part:
    p = c.pawl
    return _tube(p.spring_od, p.spring_wire, p.spring_shelf_z, lever_z(c)[0])


def build_clutch_spring(c: Camera) -> Part:
    t = c.takeup
    return _tube(t.clutch_spring_od, t.clutch_spring_wire, spring_seat_z(c), c.shell.ceiling_z)


def build_felt_washer(c: Camera) -> Part:
    t = c.takeup
    z0, z1 = felt_z(c)
    return _cylinder(t.felt_od / 2, z0, z1) - _cylinder(t.felt_id / 2, z0 - 1, z1 + 1)


def build_rewind_o_ring(c: Camera) -> Part:
    r = c.rewind
    return Pos(0, 0, r.tower_top_inside + r.o_ring_section / 2) * Torus((r.o_ring_id + r.o_ring_section) / 2, r.o_ring_section / 2)


def _at_spool(c: Camera) -> Location:
    return Location((c.layout.spool_x, c.layout.spool_y, 0))


def _at_cassette(c: Camera) -> Location:
    return Location((c.layout.cassette_x, c.layout.cassette_y, 0))


def _at_sprocket(c: Camera) -> Location:
    return Location((c.layout.sprocket_x, c.sprocket_y, 0))


def _at_pivot(c: Camera) -> Location:
    x, y = c.pawl_pivot
    return Location((x, y, 0), (0, 0, c.pawl.angle_deg))


def _at_button(c: Camera) -> Location:
    x, y = c.pawl_button
    return Location((x, y, 0))


FLIP = (180, 0, 0)

PARTS = {
    "pawl": PartSpec(build_pawl, _at_pivot, "film-back", "printed", LEVER_COLOR, print_rotation=(90, 0, 0)),
    "release_button": PartSpec(build_release_button, _at_button, "film-back", "printed", LEVER_COLOR, print_rotation=FLIP),
    "takeup_spool": PartSpec(build_takeup_spool, _at_spool, "film-back", "printed", PRINTED_COLOR, print_rotation=(0, 0, 0)),
    "drive_collar": PartSpec(build_drive_collar, _at_spool, "film-back", "printed", PRINTED_COLOR, print_rotation=FLIP),
    "advance_knob": PartSpec(build_advance_knob, _at_spool, "film-back", "printed", PRINTED_COLOR, print_rotation=FLIP),
    "rewind_fork": PartSpec(build_rewind_fork, _at_cassette, "film-back", "printed", PRINTED_COLOR, print_rotation=(0, 0, 0)),
    "rewind_knob": PartSpec(build_rewind_knob, _at_cassette, "film-back", "printed", PRINTED_COLOR, print_rotation=FLIP),
    "sprocket_pin": PartSpec(build_sprocket_pin, _at_sprocket, "film-back", "bought", STEEL),
    "takeup_shaft": PartSpec(build_takeup_shaft, _at_spool, "film-back", "bought", STEEL),
    "rewind_shaft": PartSpec(build_rewind_shaft, _at_cassette, "film-back", "bought", STEEL),
    "pawl_pin": PartSpec(build_pawl_pin, _at_pivot, "film-back", "bought", STEEL),
    "pawl_spring": PartSpec(build_pawl_spring, _at_button, "film-back", "bought", SPRING),
    "clutch_spring": PartSpec(build_clutch_spring, _at_spool, "film-back", "bought", SPRING),
    "felt_washer": PartSpec(build_felt_washer, _at_spool, "film-back", "bought", FELT),
    "rewind_o_ring": PartSpec(build_rewind_o_ring, _at_cassette, "film-back", "bought", RUBBER),
}
