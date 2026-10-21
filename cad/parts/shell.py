"""Film-back shell, rear cover, turn buttons, slot plug and the bought parts they hold.

Built in camera coordinates (film-back.md section 17), except the turn buttons, which are built
around their own pivot and placed. Every value comes from cad/params.py. Values the docs leave
open, chosen here and kept as params:

- Gate: velvet groove 1.0mm outside the front aperture; fences 1.2mm wide; rails run on as 2mm
  ribs past the take-up divider to X = 46, where the sprocket teeth take over.
- Rear: the rim face, which is also the cover's inner face, sits at Y = -2.23 (17.3). The rear
  loading opening is open from the film plane back, so no wall crosses the film band. The divider
  walls start at the film plane; the left one is the front land of the 0.6mm film throat and a
  ridge on the cover is its rear land.
- Top lap: the cover overlaps the 3mm rear face of the top wall, then a 2mm lip reaches 3mm over
  the top on 1mm of foam (6mm in all) and stops short of the dark slide slot mouth. The lip is
  notched round the advance knob (26mm, just over the shell top), so the lap there is the 3mm face only.
- Hinge: the shell carries two 30mm end knuckles with the pin pressed in; the cover's one middle
  knuckle spins on it. The axis is at the tongue's mid-depth (Y = -0.98) and 0.3mm under the shell
  bottom (Z = -33.8), so the tongue leaves its groove without binding. The knuckles hang under the
  bottom, so the shell prints bottom-down on a support raft; that keeps the rails, gate, slot,
  rim and body datum vertical and unsupported.
- Turn buttons: centre pivots at X = +/-42.5, Y = 5.6 on raised insert bosses flush with the lip
  top. A full turn clears the rewind tower, sprocket collar, release button, advance knob and the
  dark slide handle, which is 40mm wide for that reason. Each boss overhangs the body bay by 2mm
  above Z = 31.5. The hinge is 68mm under the lip, so opening slides the lip straight back: a flat
  button on the lip would not hold it. Each button carries a 3 x 2 x 1mm dog under its rear end,
  7.5mm from the pivot, in an arc groove in the 2.5mm lip (1.2mm floor); opening drives the
  groove's front wall into the dog. The groove runs the dog's quarter turn counter-clockwise from
  above, out past the lip's front edge, so released the dog hangs over the shell top. The buttons
  print top down, dog up.
- Pawl: cheeks 5.7mm thick so the 15mm pin ends flush; the spring shelf hangs from the front wall
  with a 1.5mm ring that centres the spring. Release button bayonet (as the transport parts model
  it): a plain 6.6mm bore through the top wall, no raised collar since the pressed cap comes down to
  Z = 32.0; the lug's leg runs through the wall on the +X side, open underneath and roofed at the
  top; pressed, the lug turns a quarter turn clockwise under the ceiling, and that sweep is cut out
  of the near cheek.
- Bushings: the sprocket pin goes through the shell bottom (pin Z -30 to +30); the take-up bottom
  bushing is blind with a 1.2mm floor for light, on a 1mm boss under the drive collar; the top one
  is the 3mm top wall alone, so the clutch spring bears on the ceiling. The rewind O-ring
  counterbore is on the underside of the tower top.
- The slot plug is placed in its working pose in the slot mouth, so it overlaps the dark slide,
  which is in at rest. Only one is ever in the slot.
"""
import math
from functools import lru_cache

from build123d import (Axis, Box, Cylinder, Location, Part, Polygon, Pos, RectangleRounded, Rot, SlotCenterToCenter,
                       chamfer, extrude, loft)

from params import Camera
from parts.spec import PartSpec, at_origin


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def zcyl(x: float, y: float, d: float, z0: float, z1: float) -> Part:
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


def xcyl(y: float, z: float, d: float, x0: float, x1: float) -> Part:
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0)


def sector(x: float, y: float, r_in: float, r_out: float, a0: float, a1: float, z0: float, z1: float) -> Part:
    """Annular sector about a vertical axis, from plan angle a0 to a1 (deg, counter-clockwise)."""
    n = max(2, int(abs(a1 - a0) / 5) + 1)
    far = r_out / math.cos(math.radians((a1 - a0) / (2 * (n - 1))))
    pts = [(0.0, 0.0)] + [(far * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
                            far * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]
    wedge = extrude(Pos(0, 0, z0) * Polygon(*pts, align=None), amount=z1 - z0)
    ring = zcyl(0, 0, 2 * r_out, z0, z1)
    if r_in > 0:
        ring -= zcyl(0, 0, 2 * r_in, z0, z1)
    return Pos(x, y, 0) * (ring & wedge)


def plan_box(cx: float, cy: float, angle_deg: float, u0: float, u1: float, v0: float, v1: float,
             z0: float, z1: float) -> Part:
    """Box in a plan frame turned by angle_deg: u along the angle, v across it."""
    return Location((cx, cy, 0), (0, 0, angle_deg)) * box(u0, u1, v0, v1, z0, z1)


def tongue_path(c: Camera, width: float, z_top: float) -> list[tuple[float, float, float, float]]:
    """Rectangles (x0, x1, z0, z1) of the cover seal path: left side, bottom, right side."""
    s = c.shell
    xl, xr, zb = s.x_min + s.rear_rim / 2, s.x_max - s.rear_rim / 2, s.z_min + s.rear_rim / 2
    h = width / 2
    return [(xl - h, xl + h, zb - h, z_top), (xl - h, xr + h, zb - h, zb + h), (xr - h, xr + h, zb - h, z_top)]


def side_groove_top(c: Camera) -> float:
    return c.shell.z_max - c.print.min_wall


def lip_bottom(c: Camera) -> float:
    return c.shell.z_max + c.cover.lap_foam


def lip_top(c: Camera) -> float:
    return lip_bottom(c) + c.cover.lip_t


def pawl_axes(c: Camera) -> tuple[tuple[float, float], tuple[float, float]]:
    """Unit plan vectors along the lever and along the pivot pin."""
    a = math.radians(c.pawl.angle_deg)
    return (math.cos(a), math.sin(a)), (math.sin(a), -math.cos(a))


def tower_od(c: Camera) -> float:
    return c.shell.tower_id + 2 * c.shell.tower_wall


def tower_top(c: Camera) -> float:
    return c.rewind.tower_top_inside + c.shell.tower_wall


def sprocket_collar_od(c: Camera) -> float:
    return c.shell.collar_bore + 2 * c.shell.collar_wall


def insert_boss_d(c: Camera) -> float:
    return c.fit.insert_hole_m3 + 2 * c.shell.boss_wall


def turn_button_pivots(c: Camera) -> list[tuple[float, float]]:
    return [(-c.cover.button_x, c.cover.button_y), (c.cover.button_x, c.cover.button_y)]


# The shell, built in stages.

def _envelope(c: Camera) -> Part:
    s, g = c.shell, c.gate
    part = box(s.x_min, s.x_max, s.y_rear, s.y_front, s.z_min, s.z_max)
    part -= box(-s.bridge_half_span, s.bridge_half_span, g.datum_y, s.y_front + 1, s.z_min - 1, s.z_max + 1)
    floor, ceiling = s.z_min + s.outer_wall, s.ceiling_z
    inner_front = s.y_front - s.outer_wall
    divider_out = s.bridge_half_span + s.divider_wall
    part -= box(s.x_min + s.outer_wall, -divider_out, s.y_rear - 1, inner_front, floor, ceiling)
    part -= box(divider_out, s.x_max - s.outer_wall, s.y_rear - 1, inner_front, floor, ceiling)
    # Rear loading opening over the bridge, back to the gate recess; the dividers stop at the film plane.
    part -= box(-s.bridge_half_span, s.bridge_half_span, s.y_rear - 1, g.recess, floor, ceiling)
    throat_front = s.throat_gap / 2 - c.film.thickness / 2
    part -= box(-divider_out, -s.bridge_half_span, s.y_rear - 1, throat_front, floor, ceiling)
    part -= box(s.bridge_half_span, divider_out, s.y_rear - 1, g.recess, floor, ceiling)
    return part


def _rim(c: Camera) -> Part:
    """Rear rim: 4.6mm band on the sides and bottom, deep enough for the groove plus a floor."""
    s, cv = c.shell, c.cover
    y1 = s.y_rear + cv.groove_depth + c.print.min_wall
    rim = box(s.x_min, s.x_max, s.y_rear, y1, s.z_min, s.z_min + s.rear_rim)
    rim += box(s.x_min, s.x_min + s.rear_rim, s.y_rear, y1, s.z_min, s.ceiling_z)
    rim += box(s.x_max - s.rear_rim, s.x_max, s.y_rear, y1, s.z_min, s.ceiling_z)
    return rim


def _seal_groove(c: Camera) -> Part:
    s, cv = c.shell, c.cover
    y0, y1 = s.y_rear - 1, s.y_rear + cv.groove_depth
    parts = [box(x0, x1, y0, y1, z0, z1) for x0, x1, z0, z1 in tongue_path(c, s.cover_groove_w, side_groove_top(c))]
    return parts[0] + parts[1] + parts[2]


def _gate(c: Camera, part: Part) -> Part:
    g, f, s = c.gate, c.film, c.shell
    plate_front = g.recess + g.plate
    # Gate aperture: 65 x 24 with rounded corners, bevelled on the film side.
    to_y = Rot(90, 0, 0)  # local +Z becomes camera -Y, local Y becomes camera Z
    part -= to_y * Pos(0, 0, -plate_front - 0.5) * extrude(
        RectangleRounded(f.frame_w, f.frame_h, g.corner_r), amount=g.plate + 1.0)
    bevel = loft([
        (Pos(0, 0, -g.recess - g.bevel) * RectangleRounded(f.frame_w, f.frame_h, g.corner_r)).face(),
        (Pos(0, 0, -g.recess + 0.01) * RectangleRounded(f.frame_w + 2 * g.bevel + 0.02, f.frame_h + 2 * g.bevel + 0.02,
                                                       g.corner_r + g.bevel)).face(),
    ])
    part -= to_y * bevel
    # Front wall aperture and the dark slide slot (open through the top face).
    part -= box(-g.aperture_w / 2, g.aperture_w / 2, g.slot_y0, g.datum_y + 1, -g.aperture_h / 2, g.aperture_h / 2)
    part -= box(-g.slot_w / 2, g.slot_w / 2, g.slot_y0, g.slot_y0 + g.slot, g.slot_bottom_z, s.z_max + 1)
    # Velvet groove on the body datum face.
    ix, iz = g.aperture_w / 2 + g.velvet_groove_inset, g.aperture_h / 2 + g.velvet_groove_inset
    ox, oz = ix + g.velvet_groove_w, iz + g.velvet_groove_w
    y0 = g.datum_y - g.velvet_groove_depth
    part -= box(-ox, ox, y0, g.datum_y + 1, -oz, oz) - box(-ix, ix, y0 - 1, g.datum_y + 2, -iz, iz)
    # Rails: proud of the gate recess on the film edge band, running on as ribs to the sprocket.
    for sz in (-1, 1):
        z0, z1 = sorted((sz * (g.rail_z - g.rail_w / 2), sz * (g.rail_z + g.rail_w / 2)))
        part += box(-s.bridge_half_span, s.bridge_half_span + s.divider_wall, 0, g.recess + 0.01, z0, z1)
        part += box(s.bridge_half_span + s.divider_wall - 0.01, g.rail_end_x, 0, g.rail_rib_depth, z0, z1)
        f0, f1 = sorted((sz * g.fence_gap / 2, sz * (g.fence_gap / 2 + g.fence_w)))
        part += box(-s.bridge_half_span, s.bridge_half_span, -g.fence_depth, g.recess + 0.01, f0, f1)
    return part


def _cassette(c: Camera, part: Part) -> Part:
    s, m, L = c.shell, c.measured, c.layout
    x, y = L.cassette_x, L.cassette_y
    floor = s.z_min + s.outer_wall
    cap_bottom = -m.cassette_cap_height / 2
    part += zcyl(x, y, s.locator_recess_d + 2 * s.boss_wall, floor - 0.01, cap_bottom)
    part -= zcyl(x, y, s.locator_recess_d, cap_bottom - s.locator_recess_depth, cap_bottom + 1)
    top = tower_top(c)
    part += zcyl(x, y, tower_od(c), s.ceiling_z, top)
    part -= zcyl(x, y, s.tower_id, s.ceiling_z - 1, c.rewind.tower_top_inside)
    part -= zcyl(x, y, c.fit.shaft_bore, c.rewind.tower_top_inside - 1, top + 1)
    part -= zcyl(x, y, s.oring_bore, c.rewind.tower_top_inside - 1, c.rewind.tower_top_inside + s.oring_depth)
    return part


def _takeup(c: Camera, part: Part) -> Part:
    s, sp, f, L, p = c.shell, c.sprocket, c.fit, c.layout, c.pawl
    floor = s.z_min + s.outer_wall
    sx, sy = L.sprocket_x, c.sprocket_y
    # Sprocket pin: pressed into a bottom boss, through the shell bottom.
    boss_top = -(sp.flange_gap / 2 + sp.flange_t) - s.flange_gap
    part += zcyl(sx, sy, c.fit.pin_press_hole + 2 * s.boss_wall, floor - 0.01, boss_top)
    part -= zcyl(sx, sy, c.fit.pin_press_hole, s.z_min - 1, boss_top + 1)
    # Collar for the sprocket top hub, with the fixed index mark on the pawl line.
    part += zcyl(sx, sy, sprocket_collar_od(c), s.z_max - 0.01, sp.top_hub_z1)
    part -= zcyl(sx, sy, s.collar_bore, s.ceiling_z - 1, sp.top_hub_z1 + 1)
    part -= plan_box(sx, sy, p.angle_deg, s.collar_bore / 2 - 0.1, sprocket_collar_od(c) / 2 + 0.1,
                     -s.index_mark_w / 2, s.index_mark_w / 2, sp.top_hub_z1 - s.index_mark_depth, sp.top_hub_z1 + 1)
    # Take-up shaft bushings: blind at the bottom, through the top.
    tx, ty = L.spool_x, L.spool_y
    bush_d = f.shaft_bore + 2 * s.boss_wall
    part += zcyl(tx, ty, bush_d, floor - 0.01, s.takeup_boss_top_z)
    part -= zcyl(tx, ty, f.shaft_bore, s.z_min + c.print.min_wall, s.takeup_boss_top_z + 1)
    part -= zcyl(tx, ty, f.shaft_bore, s.ceiling_z - 1, s.z_max + 1)
    return _pawl_mounts(c, part)


def _pawl_mounts(c: Camera, part: Part) -> Part:
    s, p, f = c.shell, c.pawl, c.fit
    (ux, uy), (vx, vy) = pawl_axes(c)
    px, py = c.pawl_pivot
    # Pivot cheeks hang from the ceiling either side of the lever; the pin ends flush with them.
    cheek_t = (p.pivot_pin_len - p.cheek_gap) / 2
    z0 = p.pivot_z - c.fit.pin_press_hole / 2 - s.cheek_wall
    for side in (-1, 1):
        v0, v1 = sorted((side * p.cheek_gap / 2, side * (p.cheek_gap / 2 + cheek_t)))
        part += plan_box(px, py, p.angle_deg, -s.cheek_half_len, s.cheek_half_len, v0, v1, z0, s.ceiling_z + 0.01)
    pin = Location((px, py, p.pivot_z), (0, 0, p.angle_deg)) * Rot(90, 0, 0) * Cylinder(
        c.fit.pin_press_hole / 2, p.pivot_pin_len + 2)
    part -= pin
    # Spring shelf under the button end, hung from the front wall, with a ring that centres the spring.
    bx, by = c.pawl_button
    inner_front = s.y_front - s.outer_wall
    shelf_d = p.spring_od + 2 * f.fdm_clearance + 2 * c.print.min_wall
    zs0, zs1 = p.spring_shelf_z - s.shelf_t, p.spring_shelf_z
    part += zcyl(bx, by, shelf_d, zs0, zs1) + box(bx - shelf_d / 2, bx + shelf_d / 2, by, inner_front + 0.01, zs0, zs1)
    part += zcyl(bx, by, shelf_d, zs1 - 0.01, zs1 + s.spring_cup_h) - zcyl(
        bx, by, p.spring_od + 2 * f.fdm_clearance, zs1 - 1, zs1 + s.spring_cup_h + 1)
    # Release button bayonet: the button passes the top wall; its lug rides in a vertical leg through the
    # wall, open underneath, and pressed below the ceiling it turns a quarter turn to hook under the wall.
    # The lug's sweep under the ceiling is cut out of anything hanging there (the near cheek).
    part -= zcyl(bx, by, p.button_hole_d, s.ceiling_z - 1, s.z_max + 1)
    r_in = p.button_hole_d / 2 - 0.1
    r_out = p.button_d / 2 + p.button_lug_len + f.fdm_clearance
    half_w = p.button_lug_w / 2 + f.fdm_clearance
    rest_top = s.button_lug_rest_z + p.button_lug_h
    part -= plan_box(bx, by, s.button_slot_deg, r_in, r_out, -half_w, half_w, s.ceiling_z - 1, rest_top + f.fdm_clearance)
    half_a = math.degrees(math.atan2(half_w, p.button_d / 2))
    a0, a1 = sorted((s.button_slot_deg, s.button_slot_deg + s.button_hold_deg))
    pressed_bottom = s.button_lug_rest_z - p.button_travel
    part -= sector(bx, by, 0, r_out, a0 - half_a, a1 + half_a, pressed_bottom - f.fdm_clearance, s.ceiling_z)
    return part


def _body_interface(c: Camera, part: Part) -> Part:
    k, g, s = c.body_link, c.gate, c.shell
    hx = k.hook_half_x
    part += box(-hx, hx, g.datum_y - 0.01, k.hook_front_y, k.hook_slot_top_z, s.z_max)
    part += box(-hx, hx, k.hook_slot_y[1], k.hook_front_y, k.hook_bottom_z, s.z_max)
    for side in (-1, 1):
        x0, x1 = sorted((side * k.lug_x[0], side * k.lug_x[1]))
        part += box(x0, x1, g.datum_y - 0.01, k.lug_front_y, *k.lug_z)
    part -= xcyl(k.latch_pin_y, k.latch_pin_z, c.fit.pin_press_hole, -k.lug_x[1] - 1, k.lug_x[1] + 1)
    return part


def _turn_button_bosses(c: Camera, part: Part) -> Part:
    s, cv, f = c.shell, c.cover, c.fit
    d = insert_boss_d(c)
    for x, y in turn_button_pivots(c):
        part += zcyl(x, y, d, s.z_max - 0.01, lip_top(c))
        below = zcyl(x, y, d, s.ceiling_z - cv.insert_below, s.ceiling_z + 0.01)
        part += below - box(-s.bridge_half_span, s.bridge_half_span, c.gate.datum_y, s.y_front, s.z_min, s.z_max)
        part -= zcyl(x, y, f.insert_hole_m3, lip_top(c) - cv.insert_len - 0.5, lip_top(c) + 1)
    return part


def shell_knuckle_spans(c: Camera) -> list[tuple[float, float]]:
    cv = c.cover
    x0 = c.shell.x_min + cv.hinge_inset
    x1 = x0 + cv.hinge_pin_len
    return [(x0, x0 + cv.shell_knuckle_len), (x1 - cv.shell_knuckle_len, x1)]


def cover_knuckle_span(c: Camera) -> tuple[float, float]:
    (_, a1), (b0, _) = shell_knuckle_spans(c)
    return a1 + c.fit.fdm_clearance, b0 - c.fit.fdm_clearance


def _hinge(c: Camera, part: Part) -> Part:
    s, cv = c.shell, c.cover
    ay, az, r = cv.hinge_axis_y, cv.hinge_axis_z, cv.knuckle_od / 2
    web_y0 = s.y_rear + c.fit.fdm_clearance
    for x0, x1 in shell_knuckle_spans(c):
        part += xcyl(ay, az, cv.knuckle_od, x0, x1)
        part += box(x0, x1, web_y0, ay + r, az, s.z_min + 0.01)
        part -= xcyl(ay, az, c.fit.pin_press_hole, x0 - 1, x1 + 1)
    return part


@lru_cache(maxsize=8)
def build_shell(c: Camera) -> Part:
    part = _envelope(c) + _rim(c)
    part = _gate(c, part)
    part -= _seal_groove(c)
    part = _cassette(c, part)
    part = _takeup(c, part)
    part = _body_interface(c, part)
    part = _turn_button_bosses(c, part)
    return _hinge(c, part)


# The rear cover and what it carries.

def throat_lands_y(c: Camera) -> tuple[float, float]:
    """Rear and front land of the film throat, centred on the film."""
    mid, half = -c.film.thickness / 2, c.shell.throat_gap / 2
    return mid - half, mid + half


def shoe_inner_r(c: Camera) -> float:
    return c.sprocket.hub_d / 2 + c.film.thickness + c.cover.shoe_film_gap


def _shoe(c: Camera) -> Part:
    cv, s = c.cover, c.shell
    sx, sy = c.layout.sprocket_x, c.sprocket_y
    r_in, r_out = shoe_inner_r(c), shoe_inner_r(c) + cv.shoe_t
    a0, a1 = cv.shoe_start_deg, s.shoe_end_deg
    n = 10
    arc = [(sx + r_in * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            sy + r_in * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    out_x = sx + r_out * math.cos(math.radians(a1))
    out_y = sy + r_out * math.sin(math.radians(a1))
    base = s.y_rear - 0.01
    pts = [(arc[0][0], base)] + arc + [(out_x, out_y), (out_x, base)]
    shoe = extrude(Polygon(*pts, align=None), amount=cv.shoe_w / 2, both=True)
    tooth_z = -c.film.perf_row_z
    shoe -= sector(sx, sy, 0, r_in + cv.shoe_groove_depth, a0 - 5, a1 + 5,
                   tooth_z - cv.shoe_groove_w / 2, tooth_z + cv.shoe_groove_w / 2)
    return shoe


def advance_knob_keepout(c: Camera) -> Part:
    """The advance knob sits on the shaft just over the shell top and overhangs the lip, so the lip is notched."""
    d = c.takeup.knob_d + 2 * c.fit.fdm_clearance
    return zcyl(c.layout.spool_x, c.layout.spool_y, d, c.shell.z_max + 0.01, lip_top(c) + c.cover.button_t)


def build_cover(c: Camera) -> Part:
    s, cv, f = c.shell, c.cover, c.fit
    y_out = s.y_rear - s.cover_thickness
    part = box(s.x_min, s.x_max, y_out, s.y_rear, s.z_min, lip_top(c))
    part += box(s.x_min, s.x_max, s.y_rear - 0.01, s.y_rear + cv.lap_top, lip_bottom(c), lip_top(c))
    part -= advance_knob_keepout(c)
    for x0, x1, z0, z1 in tongue_path(c, cv.tongue_w, side_groove_top(c) - f.fdm_clearance):
        part += box(x0, x1, s.y_rear - 0.01, s.y_rear + cv.tongue_len, z0, z1)
    # Pressure pad recess: a locating rim round the pad.
    ix, iz = cv.pad_w / 2 + f.fdm_clearance, cv.pad_h / 2 + f.fdm_clearance
    ox, oz = ix + cv.pad_rim_w, iz + cv.pad_rim_w
    y1 = s.y_rear + cv.pad_rim_h
    part += box(-ox, ox, s.y_rear - 0.01, y1, -oz, oz) - box(-ix, ix, s.y_rear - 1, y1 + 1, -iz, iz)
    # Rear land of the film throat, behind the left divider.
    xc = -(s.bridge_half_span + s.divider_wall / 2)
    part += box(xc - cv.throat_ridge_w / 2, xc + cv.throat_ridge_w / 2, s.y_rear - 0.01, throat_lands_y(c)[0],
                -cv.throat_ridge_half_h, cv.throat_ridge_half_h)
    part += _shoe(c)
    # Middle hinge knuckle, spinning on the pin.
    k0, k1 = cover_knuckle_span(c)
    part += box(k0, k1, y_out, s.y_rear, cv.hinge_axis_z, s.z_min + 0.01)
    part += xcyl(cv.hinge_axis_y, cv.hinge_axis_z, cv.knuckle_od, k0, k1)
    part -= xcyl(cv.hinge_axis_y, cv.hinge_axis_z, f.shaft_bore, k0 - 1, k1 + 1)
    for x, y in turn_button_pivots(c):
        part -= latch_groove(c, x, y)
    return part


BUTTON_REST_DEG = 90.0
"""Plan turn of a latched button: its local +X runs forward (+Y), so the dog on local -X points back."""


def latch_groove(c: Camera, x: float, y: float) -> Part:
    """Arc groove in the lip top that holds the latched dog and lets it through its release turn."""
    cv, f = c.cover, c.fit
    r_in, r_out = cv.dog_r - cv.dog_t / 2 - f.fdm_clearance, cv.dog_r + cv.dog_t / 2 + f.fdm_clearance
    half = math.degrees(math.atan2(cv.dog_w / 2 + f.fdm_clearance, r_in))
    a0 = BUTTON_REST_DEG + 180
    lo, hi = sorted((a0, a0 + cv.button_release_deg))
    return sector(x, y, r_in, r_out, lo - half, hi + half, lip_top(c) - cv.dog_h - f.fdm_clearance, lip_top(c) + 1)


def build_turn_button(c: Camera) -> Part:
    cv = c.cover
    part = extrude(SlotCenterToCenter(cv.button_len - cv.button_w, cv.button_w), amount=cv.button_t)
    part = chamfer(part.edges().group_by(Axis.Z)[-1], cv.button_chamfer)
    part += box(-cv.dog_r - cv.dog_t / 2, -cv.dog_r + cv.dog_t / 2, -cv.dog_w / 2, cv.dog_w / 2, -cv.dog_h, 0.01)
    return part - zcyl(0, 0, c.fit.shaft_bore, -1, cv.button_t + 1)


def place_turn_button(side: int):
    def place(c: Camera) -> Location:
        x, y = turn_button_pivots(c)[0 if side < 0 else 1]
        return Location((x, y, lip_top(c)), (0, 0, BUTTON_REST_DEG))
    return place


def slot_mid_y(c: Camera) -> float:
    return c.gate.slot_y0 + c.gate.slot / 2


def build_slot_plug(c: Camera) -> Part:
    cv, s = c.cover, c.shell
    y0 = slot_mid_y(c) - cv.plug_t / 2
    part = box(-cv.slide_w / 2, cv.slide_w / 2, y0, y0 + cv.plug_t, s.z_max - cv.plug_depth, s.z_max + 0.01)
    part += box(-cv.plug_grip_w / 2, cv.plug_grip_w / 2, y0, y0 + cv.plug_grip_t, s.z_max, s.z_max + cv.plug_grip_h)
    return part


# Bought parts.

def build_dark_slide(c: Camera) -> Part:
    cv = c.cover
    y0 = slot_mid_y(c) - cv.slide_t / 2
    part = box(-cv.slide_w / 2, cv.slide_w / 2, y0, y0 + cv.slide_t, c.gate.slot_bottom_z, cv.slide_plate_top_z)
    part += box(-cv.handle_w / 2, cv.handle_w / 2, y0, y0 + cv.slide_t, cv.slide_plate_top_z - 0.01, cv.slide_top_z)
    hole_top = cv.slide_top_z - (cv.handle_w - cv.finger_hole_w) / 2
    return part - box(-cv.finger_hole_w / 2, cv.finger_hole_w / 2, y0 - 1, y0 + 1,
                      hole_top - cv.finger_hole_h, hole_top)


def build_pressure_pad(c: Camera) -> Part:
    cv, s = c.cover, c.shell
    return box(-cv.pad_w / 2, cv.pad_w / 2, s.y_rear, -c.film.thickness, -cv.pad_h / 2, cv.pad_h / 2)


def build_hinge_pin(c: Camera) -> Part:
    cv = c.cover
    x0 = c.shell.x_min + cv.hinge_inset
    return xcyl(cv.hinge_axis_y, cv.hinge_axis_z, c.measured.rod_d, x0, x0 + cv.hinge_pin_len)


def build_latch_pin(c: Camera) -> Part:
    k = c.body_link
    return xcyl(k.latch_pin_y, k.latch_pin_z, c.measured.rod_d, -k.latch_pin_len / 2, k.latch_pin_len / 2)


def build_m3_insert(c: Camera) -> Part:
    cv = c.cover
    return zcyl(0, 0, c.fit.insert_hole_m3, -cv.insert_len, 0) - zcyl(0, 0, c.measured.rod_d, -cv.insert_len - 1, 1)


def build_m3_screw(c: Camera) -> Part:
    cv = c.cover
    head = cv.button_t
    return zcyl(0, 0, c.measured.rod_d, head - cv.m3_len, head + 0.01) + zcyl(0, 0, cv.m3_head_d, head, head + cv.m3_head_h)


def place_on_pivot(side: int):
    def place(c: Camera) -> Location:
        x, y = turn_button_pivots(c)[0 if side < 0 else 1]
        return Location((x, y, lip_top(c)))
    return place


SHELL_COLOR = "#2b2b2e"
COVER_COLOR = "#34343a"
METAL = "#b8bcc2"

PARTS: dict[str, PartSpec] = {
    "shell": PartSpec(build_shell, at_origin, "film-back", "printed", SHELL_COLOR, print_rotation=(0, 0, 0)),
    "rear_cover": PartSpec(build_cover, at_origin, "film-back", "printed", COVER_COLOR, print_rotation=(90, 0, 0)),
    "turn_button_left": PartSpec(build_turn_button, place_turn_button(-1), "film-back", "printed", "#4a4a52",
                                 print_rotation=(180, 0, 0)),
    "turn_button_right": PartSpec(build_turn_button, place_turn_button(1), "film-back", "printed", "#4a4a52",
                                  print_rotation=(180, 0, 0)),
    "slot_plug": PartSpec(build_slot_plug, at_origin, "film-back", "printed", "#4a4a52", print_rotation=(90, 0, 0)),
    "dark_slide": PartSpec(build_dark_slide, at_origin, "film-back", "bought", "#1c1c1f"),
    "pressure_pad": PartSpec(build_pressure_pad, at_origin, "film-back", "bought", "#101012"),
    "hinge_pin": PartSpec(build_hinge_pin, at_origin, "film-back", "bought", METAL),
    "latch_pin": PartSpec(build_latch_pin, at_origin, "film-back", "bought", METAL),
    "m3_insert_left": PartSpec(build_m3_insert, place_on_pivot(-1), "film-back", "bought", "#c8a24a"),
    "m3_insert_right": PartSpec(build_m3_insert, place_on_pivot(1), "film-back", "bought", "#c8a24a"),
    "m3_screw_left": PartSpec(build_m3_screw, place_on_pivot(-1), "film-back", "bought", METAL),
    "m3_screw_right": PartSpec(build_m3_screw, place_on_pivot(1), "film-back", "bought", METAL),
}
