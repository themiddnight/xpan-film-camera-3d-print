"""Geometry checks for the film-back shell, rear cover, turn buttons and their bought parts."""
import math

from build123d import Axis, Part, Pos, Rot, Vector

import mechanisms
from checklib import EPS, check
from params import Camera
from parts import PARTS
from parts import shell as sh

LOCKED_FRAME = (65.0, 24.0)  # AGENTS.md key specifications; checked against, never built from


def _edge(part: Part, origin: Vector, direction: Vector, d0: float, d1: float, step: float = 0.1) -> float:
    """Distance along a ray to the first inside/outside change after d0, searched up to d1; nan if none."""
    u = direction.normalized()
    s0 = part.is_inside(origin + u * d0)
    d = d0
    while True:
        nxt = min(d + step, d1)
        if part.is_inside(origin + u * nxt) != s0:
            d0, d1 = d, nxt
            break
        if nxt >= d1:
            return math.nan
        d = nxt
    for _ in range(18):
        mid = (d0 + d1) / 2
        if part.is_inside(origin + u * mid) == s0:
            d0 = mid
        else:
            d1 = mid
    return (d0 + d1) / 2


def _hole_d(part: Part, centre: Vector, across: tuple[Vector, Vector], r_max: float = 5.0) -> float:
    """Diameter of an empty bore at centre, from four rays in its cross-section plane."""
    a, b = across
    radii = [_edge(part, centre, d, 0, r_max, step=0.5) for d in (a, -a, b, -b)]
    return min(radii[0] + radii[1], radii[2] + radii[3])


X, Y, Z = Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)

LATCH_STOP_MM3 = 1.0
"""Least peak overlap of the opening cover with a latched button that counts as a stop, not a graze."""


def _turned_button(c: Camera, b, side: str, fraction: float) -> Part:
    """A turn button as the viewer's turn_buttons drive turns it, fraction 0 latched to 1 released."""
    drive = next(d for m in mechanisms.mechanisms(c) if m.id == "turn_buttons" for d in m.drives
                 if d.part == f"turn_button_{side}")
    axis = Axis(drive.origin, drive.axis)
    return b.placed(drive.part).rotate(axis, drive.amount * fraction)


def _cover_axis(c: Camera) -> Axis:
    return Axis((0, c.cover.hinge_axis_y, c.cover.hinge_axis_z), (1, 0, 0))


@check("gate aperture 65.0 x 24.0, centred, rounded and bevelled (geometry)")
def _(c, b):
    g = c.gate
    shell = b.local("shell")
    y = g.recess + g.plate / 2
    o = Vector(0, y, 0)
    right, left = _edge(shell, o, X, 0, 40, step=1), _edge(shell, o, -X, 0, 40, step=1)
    top, bottom = _edge(shell, o, Z, 0, 20, step=1), _edge(shell, o, -Z, 0, 20, step=1)
    w, h = right + left, top + bottom
    centred = max(abs(right - left), abs(top - bottom)) / 2 < 0.02
    size_ok = abs(w - LOCKED_FRAME[0]) < 0.02 and abs(h - LOCKED_FRAME[1]) < 0.02
    corner = Vector(w / 2, y, h / 2)
    rounded = shell.is_inside(corner + Vector(-0.1, 0, -0.1)) and not shell.is_inside(corner + Vector(-0.35, 0, -0.35))
    bevel = not shell.is_inside(Vector(w / 2 + g.bevel / 2, g.recess + 0.05, 0))
    ok = size_ok and centred and rounded and bevel
    return ok, f"{w:.3f} x {h:.3f}mm, centre offset {(right - left) / 2:+.3f}/{(top - bottom) / 2:+.3f}, rounded corner {rounded}, rear bevel {bevel}"


@check("rails on the film edge band, proud of the gate recess (geometry)")
def _(c, b):
    g, f = c.gate, c.film
    shell = b.local("shell")
    perf_outer = f.width / 2 - f.perf_edge
    float_ = (g.fence_gap - f.width) / 2
    details, ok = [], True
    for sz in (-1, 1):
        mid = Vector(0, g.recess / 2, sz * g.rail_z)
        inner = g.rail_z - _edge(shell, mid, -Z * sz, 0, 3)
        outer = g.rail_z + _edge(shell, mid, Z * sz, 0, 3)
        face = _edge(shell, Vector(0, -1, sz * g.rail_z), Y, 0, 1.5) - 1
        recess = _edge(shell, Vector(0, -1, sz * (perf_outer - 0.5)), Y, 0, 3) - 1
        proud = recess - face
        side_ok = (abs(face) < 0.01 and 0.15 - EPS <= proud <= 0.20 + EPS
                   and inner >= perf_outer + 0.5 - 0.01 and outer <= f.width / 2 - float_)
        ok &= side_ok
        details.append(f"Z {inner:.2f}..{outer:.2f}, face Y {face:+.3f}, proud {proud:.3f}")
    return ok, f"{'; '.join(details)}; perforations end at {perf_outer:.2f}"


@check("body datum face at Y = 4.20 and the body bay clear (geometry)")
def _(c, b):
    k, s, g = c.body_link, c.shell, c.gate
    shell = b.local("shell")
    span = s.bridge_half_span - 1.5
    probes = [(span, 0), (-span, 0), (0, 22), (0, -22), (span, 28), (-span, -28)]
    faces = [_edge(shell, Vector(x, g.datum_y + 1, z), -Y, 0, 2) for x, z in probes]
    faces = [g.datum_y + 1 - d for d in faces]
    flat = all(abs(y - k.hook_slot_y[0]) < 0.01 for y in faces)
    bay = sh.box(-s.bridge_half_span + 0.1, s.bridge_half_span - 0.1, k.hook_slot_y[0] + 0.01, s.y_front + 1,
                 k.lug_z[1] + 0.01, k.hook_bottom_z - 0.01)
    slot = sh.box(-k.hook_half_x, k.hook_half_x, k.hook_slot_y[0] + 0.01, k.hook_slot_y[1] - 0.01,
                  k.hook_bottom_z, k.hook_slot_top_z - 0.01)
    clash = (shell & bay).volume + (shell & slot).volume
    return flat and clash < 1e-3, f"face Y {min(faces):.3f}..{max(faces):.3f} (body reads {k.hook_slot_y[0]}), bay and hook slot overlap {clash:.3f}mm3"


@check("dark slide slot width, depth and mouth (geometry)")
def _(c, b):
    g, cv, s = c.gate, c.cover, c.shell
    shell = b.local("shell")
    mid = Vector(0, sh.slot_mid_y(c), g.aperture_h / 2 + 3)
    width = _edge(shell, mid, Y, 0, 2) + _edge(shell, mid, -Y, 0, 2)
    across = _edge(shell, mid, X, 0, 45, step=1) + _edge(shell, mid, -X, 0, 45, step=1)
    bottom = mid.Z - _edge(shell, mid, -Z, 0, 60, step=1)
    mouth_open = not shell.is_inside(Vector(0, mid.Y, s.z_max - 0.01))
    slide_bottom = b.placed("dark_slide").bounding_box().min.Z
    play = width - cv.slide_t
    ok = (0.2 <= play <= 0.4 and across >= max(70.0, cv.slide_w + 0.5) and mouth_open
          and bottom <= -g.aperture_h / 2 - 1.0 and abs(slide_bottom - bottom) < 0.01)
    return ok, f"{width:.2f} x {across:.1f}mm ({play:.2f}mm play on the slide), stop Z {bottom:.2f}, slide bottom {slide_bottom:.2f}, mouth open {mouth_open}"


def _bores(c: Camera, b) -> list[tuple[str, str, float]]:
    """(label, kind, measured diameter) for every pin, shaft and screw bore in the shell module's parts."""
    s, p, cv, k, L = c.shell, c.pawl, c.cover, c.body_link, c.layout
    shell, cover = b.local("shell"), b.local("rear_cover")
    out = [
        ("sprocket pin", "press", _hole_d(shell, Vector(L.sprocket_x, c.sprocket_y, s.z_min + 2), (X, Y))),
        ("take-up bottom bushing", "spin", _hole_d(shell, Vector(L.spool_x, L.spool_y, s.z_min + s.outer_wall), (X, Y))),
        ("take-up top bushing", "spin", _hole_d(shell, Vector(L.spool_x, L.spool_y, s.ceiling_z), (X, Y))),
        ("rewind tower bushing", "spin", _hole_d(shell, Vector(L.cassette_x, L.cassette_y, sh.tower_top(c) - 0.5), (X, Y))),
    ]
    for sx in (-1, 1):
        out.append((f"latch lug {sx:+d}", "press", _hole_d(shell, Vector(sx * sum(k.lug_x) / 2, k.latch_pin_y, k.latch_pin_z), (Y, Z))))
    for x0, x1 in sh.shell_knuckle_spans(c):
        out.append((f"shell knuckle X {x0:.0f}", "press", _hole_d(shell, Vector((x0 + x1) / 2, cv.hinge_axis_y, cv.hinge_axis_z), (Y, Z))))
    k0, k1 = sh.cover_knuckle_span(c)
    out.append(("cover knuckle", "spin", _hole_d(cover, Vector((k0 + k1) / 2, cv.hinge_axis_y, cv.hinge_axis_z), (Y, Z))))
    (ux, uy), (vx, vy) = sh.pawl_axes(c)
    px, py = c.pawl_pivot
    off = p.cheek_gap / 2 + (p.pivot_pin_len - p.cheek_gap) / 4
    for side in (-1, 1):
        centre = Vector(px + side * off * vx, py + side * off * vy, p.pivot_z)
        out.append((f"pawl cheek {side:+d}", "press", _hole_d(shell, centre, (Vector(ux, uy, 0), Z))))
    out.append(("turn button", "spin", _hole_d(b.local("turn_button_left"), Vector(0, 0, cv.button_t / 2), (X, Y))))
    for x, y in sh.turn_button_pivots(c):
        out.append((f"insert hole X {x:+.1f}", "insert", _hole_d(shell, Vector(x, y, sh.lip_top(c) - 1), (X, Y))))
    bx, by = c.pawl_button
    out.append(("release button bore", "button", _hole_d(shell, Vector(bx, by, s.ceiling_z + 0.5), (-X, -Y))))
    out.append(("sprocket collar", "hub", _hole_d(shell, Vector(L.sprocket_x, c.sprocket_y, s.ceiling_z + 0.5), (X, Y))))
    return out


@check("pin, shaft, insert and collar bore fits (geometry)")
def _(c, b):
    rod, f, p, sp = c.measured.rod_d, c.fit, c.pawl, c.sprocket
    bad, seen = [], {}
    for label, kind, d in _bores(c, b):
        if kind == "press":
            ok = rod - 0.2 <= d <= rod - 0.02
        elif kind == "spin":
            ok = abs(d - f.shaft_bore) < 0.02 and d - rod >= 0.15
        elif kind == "insert":
            ok = abs(d - f.insert_hole_m3) < 0.02
        elif kind == "button":
            ok = (d - p.button_d) / 2 >= f.fdm_clearance - 0.01
        else:
            ok = (d - sp.top_hub_d) / 2 >= 0.15
        seen.setdefault(kind, []).append(d)
        if not ok:
            bad.append(f"{label} {d:.3f}")
    summary = ", ".join(f"{k} {min(v):.2f}-{max(v):.2f}" for k, v in seen.items())
    return not bad, (f"BAD: {', '.join(bad)}; " if bad else "") + summary + f" on a {rod}mm rod"


@check("cover tongue fits its groove with clearance (geometry)")
def _(c, b):
    s, cv = c.shell, c.cover
    shell, cover = b.local("shell"), b.local("rear_cover")
    y = s.y_rear + cv.tongue_len / 2
    sites = [("bottom", Vector(0, y, s.z_min + s.rear_rim / 2), Z),
             ("left", Vector(s.x_min + s.rear_rim / 2, y, 0), X),
             ("right", Vector(s.x_max - s.rear_rim / 2, y, 0), X)]
    ok, details = True, []
    for name, p, axis in sites:
        g_hi, g_lo = _edge(shell, p, axis, 0, s.rear_rim), _edge(shell, p, -axis, 0, s.rear_rim)
        t_hi, t_lo = _edge(cover, p, axis, 0, s.rear_rim), _edge(cover, p, -axis, 0, s.rear_rim)
        floor = _edge(shell, p, Y, 0, 5)
        tip = _edge(cover, p, Y, 0, 5)
        gaps = (g_hi - t_hi, g_lo - t_lo)
        site_ok = all(0.2 <= gp <= 0.5 for gp in gaps) and floor - tip > 0
        ok &= site_ok
        details.append(f"{name} {gaps[0]:.2f}/{gaps[1]:.2f} side, {floor - tip:.2f} tip")
    return ok, "; ".join(details)


@check("rear cover closes on the shell and swings open clear of it and the released latches (geometry)")
def _(c, b):
    cv = c.cover
    released = _turned_button(c, b, "left", 1) + _turned_button(c, b, "right", 1)
    fixed = b.placed("shell") + b.placed("sprocket") + sh.advance_knob_keepout(c) + released
    cover = b.placed("rear_cover")
    axis = _cover_axis(c)
    worst = max(((cover.rotate(axis, a) & fixed).volume, a) for a in (0, 2, 5, 10, 15, 20, 30, 45, 60, 80, cv.open_deg))
    return worst[0] < 1e-3, f"worst overlap {worst[0]:.3f}mm3 at {worst[1]} deg over 0-{cv.open_deg} deg"


@check("latched turn buttons stop the cover opening (geometry)")
def _(c, b):
    cover, axis = b.placed("rear_cover"), _cover_axis(c)
    ok, details = True, []
    for side in ("left", "right"):
        button = b.placed(f"turn_button_{side}")
        v = {a: (cover.rotate(axis, a) & button).volume for a in (0, 0.5, 1, 1.5, 2, 2.5, 3)}
        opening = [x for a, x in v.items() if a > 0]
        side_ok = v[0] < 1e-3 and max(opening) >= LATCH_STOP_MM3 and min(opening) >= 0.01
        ok &= side_ok
        details.append(f"{side} " + ", ".join(f"{a}:{x:.2f}" for a, x in v.items()))
    return ok, f"overlap mm3 by deg open, closed clear, peak >= {LATCH_STOP_MM3}, never clear to 3 deg: " + "; ".join(details)


@check("turn buttons turn a quarter to release, clear of everything round them (geometry)")
def _(c, b):
    reach = math.hypot(c.cover.button_len / 2, c.cover.button_w / 2) + 1
    ok, details = True, []
    for side, (x, y) in zip(("left", "right"), sh.turn_button_pivots(c)):
        own = {f"turn_button_{side}", f"m3_screw_{side}", f"m3_insert_{side}"}
        z = _turned_button(c, b, side, 0).bounding_box()
        near = [n for n in PARTS if n not in own and _boxes_meet(b.placed(n).bounding_box(), x - reach, x + reach,
                                                                 y - reach, y + reach, z.min.Z, z.max.Z)]
        blockers = b.placed(near[0])
        for n in near[1:]:
            blockers += b.placed(n)
        worst = max(((_turned_button(c, b, side, i / 9) & blockers).volume, i / 9) for i in range(10))
        ok &= worst[0] < 1e-3
        details.append(f"{side} worst {worst[0]:.3f}mm3 at {worst[1]:.0%} of the turn, against {len(near)} parts")
    return ok, "; ".join(details)


def _boxes_meet(box, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> bool:
    return (box.min.X <= x1 and x0 <= box.max.X and box.min.Y <= y1 and y0 <= box.max.Y
            and box.min.Z <= z1 and z0 <= box.max.Z)


@check("hinge axis at the tongue mid-depth, cover knuckle under the shell bottom")
def _(c, b):
    cv, s = c.cover, c.shell
    y = s.y_rear + cv.tongue_len / 2
    z = s.z_min - c.fit.fdm_clearance - cv.knuckle_od / 2
    ok = abs(cv.hinge_axis_y - y) < 0.01 and abs(cv.hinge_axis_z - z) < 0.01
    return ok, f"axis Y {cv.hinge_axis_y} (tongue mid-depth {y:.2f}), Z {cv.hinge_axis_z} (knuckle under the bottom {z:.2f})"


@check("turn buttons clear the tower, collars, knob, release button and slide handle (geometry)")
def _(c, b):
    cv, t, p = c.cover, c.takeup, c.pawl
    bb = b.local("turn_button_left").bounding_box()
    sweep_r = math.hypot(max(abs(bb.min.X), bb.max.X), max(abs(bb.min.Y), bb.max.Y))
    blockers = b.placed("shell") + b.placed("dark_slide") + b.placed("slot_plug")
    z0, z1 = sh.lip_top(c) + 0.05, sh.lip_top(c) + cv.button_t
    details, ok = [], True
    for x, y in sh.turn_button_pivots(c):
        disc = sh.zcyl(x, y, 2 * (sweep_r + c.fit.fdm_clearance), z0, z1)
        hit = (disc & blockers).volume
        knob = math.hypot(x - c.layout.spool_x, y - c.layout.spool_y) - t.knob_d / 2 - sweep_r
        bx, by = c.pawl_button
        button = math.hypot(x - bx, y - by) - p.button_d / 2 - sweep_r
        side_ok = hit < 1e-3 and knob >= 0.5 and button >= 0.5
        ok &= side_ok
        details.append(f"X {x:+.1f}: printed/slide overlap {hit:.2f}mm3, knob {knob:.1f}mm, button {button:.1f}mm")
    return ok, f"sweep radius {sweep_r:.2f}mm; " + "; ".join(details)


@check("shell-module printed parts fit the print bed (geometry)")
def _(c, b):
    sizes = {}
    for name, spec in sh.PARTS.items():
        if spec.kind == "printed":
            size = (Rot(*spec.print_rotation) * b.local(name)).bounding_box().size
            sizes[name] = (size.X, size.Y)
    worst = max(sizes, key=lambda n: max(sizes[n]))
    return all(max(v) <= c.print.bed for v in sizes.values()), f"largest {worst} {sizes[worst][0]:.1f} x {sizes[worst][1]:.1f}mm on a {c.print.bed}mm bed"


@check("pawl cheeks, spring shelf and button bayonet match the pawl interface (geometry)")
def _(c, b):
    p, s, f, sp = c.pawl, c.shell, c.fit, c.sprocket
    shell = b.local("shell")
    (ux, uy), (vx, vy) = sh.pawl_axes(c)
    px, py = c.pawl_pivot
    v = Vector(vx, vy, 0)
    above = Vector(px, py, p.pivot_z + c.fit.pin_press_hole / 2 + 0.5)
    gap = _edge(shell, above, v, 0, 5) + _edge(shell, above, -v, 0, 5)
    cheek = Vector(px + (p.cheek_gap / 2 + 1) * vx, py + (p.cheek_gap / 2 + 1) * vy, p.pivot_z)
    hole_top, hole_bottom = _edge(shell, cheek, Z, 0, 3), _edge(shell, cheek, -Z, 0, 3)
    axis_z = p.pivot_z + (hole_top - hole_bottom) / 2
    u = Vector(ux, uy, 0)
    axis_u = (_edge(shell, cheek, u, 0, 3) - _edge(shell, cheek, -u, 0, 3)) / 2
    bx, by = c.pawl_button
    shelf = Vector(bx, by, p.spring_shelf_z + 0.5)
    shelf_z = shelf.Z - _edge(shell, shelf, -Z, 0, 2)
    cup = _hole_d(shell, shelf, (X, Y))
    working = sp.cam_z0 + sp.cam_t + p.rest_gap - shelf_z
    # Bayonet: the lug's leg is open at rest but roofed over, and its pressed quarter turn under the ceiling is clear.
    r_lug = p.button_d / 2 + p.button_lug_len / 2
    leg = math.radians(s.button_slot_deg)
    leg_xy = Vector(bx + r_lug * math.cos(leg), by + r_lug * math.sin(leg), 0)
    leg_open = not shell.is_inside(leg_xy + Vector(0, 0, s.button_lug_rest_z + p.button_lug_h / 2))
    roofed = shell.is_inside(leg_xy + Vector(0, 0, s.z_max - 0.1))
    turn_z = s.button_lug_rest_z - p.button_travel + p.button_lug_h / 2
    turn = [math.radians(s.button_slot_deg + s.button_hold_deg * i / 18) for i in range(19)]
    turn_clear = not any(shell.is_inside(Vector(bx + r_lug * math.cos(a), by + r_lug * math.sin(a), turn_z)) for a in turn)
    held = shell.is_inside(Vector(bx + r_lug * math.cos(turn[-1]), by + r_lug * math.sin(turn[-1]), s.ceiling_z + 0.1))
    bayonet = leg_open and roofed and turn_clear and held
    ok = (abs(gap - (p.width + 2 * f.fdm_clearance)) < 0.02 and abs(axis_z - p.pivot_z) < 0.02 and abs(axis_u) < 0.02
          and abs(shelf_z - p.spring_shelf_z) < 0.02 and cup >= p.spring_od + 0.4
          and 0.5 * p.spring_free_len <= working <= 0.9 * p.spring_free_len and bayonet)
    return ok, (f"cheek gap {gap:.2f} for a {p.width}mm lever, pin axis Z {axis_z:.2f} ({axis_u:+.2f} along the lever), "
                f"shelf Z {shelf_z:.2f}, cup {cup:.2f}mm, spring works at {working:.1f}/{p.spring_free_len}mm; "
                f"bayonet leg open {leg_open}, roofed {roofed}, turn clear {turn_clear}, held under the ceiling {held}")


@check("film throat centres the film with clearance (geometry)")
def _(c, b):
    s = c.shell
    x = -(s.bridge_half_span + s.divider_wall / 2)
    o = Vector(x, -c.film.thickness / 2, 0)
    front = _edge(b.local("shell"), o, Y, 0, 2)
    rear = _edge(b.local("rear_cover"), o, -Y, 0, 3)
    side = ((front + rear) - c.film.thickness) / 2
    ok = 0.15 <= side <= 0.4 and abs(front - rear) < 0.05
    return ok, f"lands {front + rear:.2f}mm apart, {side:.2f}mm each side of the {c.film.thickness}mm film"


@check("cover shoe holds the film on the sprocket teeth (geometry)")
def _(c, b):
    sp, cv, f = c.sprocket, c.cover, c.film
    cover = b.local("rear_cover")
    hub_r = sp.hub_d / 2
    a = math.radians((cv.shoe_start_deg + c.shell.shoe_end_deg) / 2)
    ray = Vector(math.cos(a), math.sin(a), 0)
    land_z = -(f.perf_row_z + c.fit.tooth_across / 2 + sp.flange_gap / 2) / 2
    centre = Vector(c.layout.sprocket_x, c.sprocket_y, land_z)
    shoe_r = sh.shoe_inner_r(c) + (cv.shoe_groove_depth + cv.shoe_t) / 2
    r_land = _edge(cover, centre, ray, hub_r, shoe_r)
    r_teeth = _edge(cover, centre + Vector(0, 0, -f.perf_row_z - land_z), ray, hub_r, shoe_r)
    probe = centre + ray * shoe_r
    top = land_z + _edge(cover, probe, Z, 0, sp.flange_gap, step=1)
    bottom = land_z - _edge(cover, probe, -Z, 0, sp.flange_gap, step=1)
    film_gap = r_land - hub_r - f.thickness
    tooth_gap = r_teeth - hub_r - c.fit.tooth_height
    inside_flanges = top <= sp.flange_gap / 2 - 0.2 and bottom >= -sp.flange_gap / 2 + 0.2
    ok = 0.15 <= film_gap <= 0.5 and tooth_gap >= 0.3 and inside_flanges
    return ok, f"film gap {film_gap:.2f}mm, tooth gap {tooth_gap:.2f}mm, shoe Z {bottom:.2f}..{top:.2f} inside flanges +/-{sp.flange_gap / 2}"


@check("pressure pad squeeze and coverage (geometry)")
def _(c, b):
    s, g, f = c.shell, c.gate, c.film
    pad = b.placed("pressure_pad").bounding_box()
    cover_face = s.y_rear + 1 - _edge(b.local("rear_cover"), Vector(0, s.y_rear + 1, 0), -Y, 0, 3)
    space = -f.thickness - cover_face
    squeeze = s.pad_sheet + s.pad_foam - space
    on_rails = pad.max.Z >= g.rail_z - g.rail_w / 2 + 0.2 and pad.max.Z <= g.fence_gap / 2 - 0.3
    ok = abs(squeeze - c.fit.pad_squeeze) < 0.02 and abs(pad.max.Y + f.thickness) < 0.01 and on_rails
    return ok, f"cover face Y {cover_face:.2f}, {space:.2f}mm for a {s.pad_sheet + s.pad_foam:.2f}mm pad, squeeze {squeeze:.2f}, pad Z +/-{pad.max.Z:.1f}"


PINCH_MIN_H, PINCH_MAX_H = 8.0, 10.0
"""Tab height a thumb-and-finger pinch needs above whatever stands behind it, and the most worth carrying."""
PINCH_MIN_W = 15.0
"""About one fingertip pad."""
FACE_REST_HALF_W, FACE_REST_Z0 = 15.0, 0.0
"""Rear cover face kept free either side of the eye line, from this height to the top, for nose and brow."""
SEAT_CLEAR = 0.5
"""Mirrors the body area's tripod plate clearance under every part but the feet."""


def _stowed_slide(c: Camera, b) -> Part:
    """The dark slide moved the way the viewer moves it: pulled, carried over the cover, dropped into the holder."""
    shape = b.placed("dark_slide")
    for m in mechanisms.mechanisms(c):
        if m.id in ("dark_slide", "slide_carry", "slide_stow"):
            for d in m.drives:
                shape = Pos(*(a * d.amount for a in d.axis)) * shape
    return shape


def _clashes_with(shape: Part, others: list[Part]) -> float:
    box = shape.bounding_box()
    worst = 0.0
    for o in others:
        if _boxes_meet(o.bounding_box(), box.min.X, box.max.X, box.min.Y, box.max.Y, box.min.Z, box.max.Z):
            worst = max(worst, (shape & o).volume)
    return worst


@check("dark slide pull tab is a pinch grip, low over the cover lip (geometry)")
def _(c, b):
    slide = b.local("dark_slide")
    top = slide.bounding_box().max.Z
    height = top - sh.lip_top(c)
    mid = Vector(0, sh.slot_mid_y(c), sh.lip_top(c) + height / 2)
    width = _edge(slide, mid, X, 0, 40, step=0.5) + _edge(slide, mid, -X, 0, 40, step=0.5)
    ok = PINCH_MIN_H - EPS <= height <= PINCH_MAX_H + EPS and width >= PINCH_MIN_W
    return ok, (f"tab {width:.1f}mm wide (need {PINCH_MIN_W}), top Z {top:.1f}: {height:.1f}mm over the cover lip "
                f"(pinch {PINCH_MIN_H}-{PINCH_MAX_H}), {top - c.shell.z_max:.1f}mm over the shell top")


@check("stowed dark slide fits its holder with clearance and is held (geometry)")
def _(c, b):
    cv = c.cover
    holder, cover, slide = b.local("slide_holder"), b.local("rear_cover"), _stowed_slide(c, b)
    sb = slide.bounding_box()
    y_cover = sh.cover_outer_y(c)
    y_mid = y_cover - cv.holder_gap / 2
    z_rail = cv.holder_top_z - 3
    rail = Vector(cv.holder_x + sh.holder_channel_x(c) - 1, y_mid, z_rail)
    gap = _edge(holder, rail, -Y, 0, 2) + _edge(cover, rail, Y, 0, 2)
    play = gap - cv.slide_t
    centre = Vector(cv.holder_x, y_mid, z_rail)
    sides = (centre.X + _edge(holder, centre, X, 0, 45, step=1) - sb.max.X,
             sb.min.X - (centre.X - _edge(holder, centre, -X, 0, 45, step=1)))
    lip = Vector(cv.holder_x, y_cover - cv.holder_gap - cv.holder_lip_t / 2, z_rail)
    engage = min(sb.max.X - (lip.X + _edge(holder, lip, X, 0, 45, step=1)),
                 lip.X - _edge(holder, lip, -X, 0, 45, step=1) - sb.min.X)
    stop = Vector(cv.holder_x, y_mid, 0)
    bar_top = stop.Z - _edge(holder, stop, -Z, 0, 40, step=1)
    on_cover = abs(sb.max.Y - y_cover) < 0.01
    # Held: each finger's bump reaches past the slide's rear face, and the finger flexes within PETG's range.
    f0, f1 = sh.holder_finger_x(c)
    bump_z = cv.holder_finger_root_z + cv.holder_finger_len - cv.holder_bump_len / 2
    squeeze = []
    for sgn in (-1, 1):
        p = Vector(cv.holder_x + sgn * (f0 + f1) / 2, y_cover - 0.01, bump_z)
        crest = p.Y - _edge(holder, p, -Y, 0, 2, step=0.05)
        squeeze.append(crest - sb.min.Y)
    slot_open = not holder.is_inside(Vector(cv.holder_x + f1 + cv.holder_finger_slot / 2,
                                            y_cover - cv.holder_gap - cv.holder_lip_t / 2, bump_z))
    pressed = (slide & holder).volume
    arm = bump_z - cv.holder_finger_root_z
    strain = 3 * cv.holder_lip_t * max(squeeze) / (2 * arm * arm)
    held = all(0.15 <= s <= 0.45 for s in squeeze) and slot_open and pressed > 0.1 and strain <= 0.01
    ok = (0.2 <= play <= 0.4 and all(0.3 <= s <= 0.7 for s in sides) and engage >= 2.5
          and abs(sb.min.Z - bar_top) < 0.01 and on_cover and held)
    return ok, (f"channel {gap:.2f}mm ({play:.2f} play), sides {sides[0]:.2f}/{sides[1]:.2f}, lips over the edges "
                f"{engage:.2f}mm, slide bottom {sb.min.Z:.2f} on the bar at {bar_top:.2f}, on the cover {on_cover}; "
                f"fingers press {squeeze[0]:.2f}/{squeeze[1]:.2f}mm ({pressed:.2f}mm3), slot open {slot_open}, "
                f"root strain {strain:.2%}")


@check("stowed dark slide and its holder clear everything, cover closed and swung open (geometry)")
def _(c, b):
    s, cv = c.shell, c.cover
    mine = {"dark_slide": _stowed_slide(c, b), "slide_holder": b.placed("slide_holder")}
    problems = []
    rest = [b.placed(n) for n in PARTS if n not in mine]
    for name, shape in mine.items():
        v = _clashes_with(shape, rest)
        if v > 1e-2:
            problems.append(f"closed {name} {v:.2f}mm3")
    group = {"rear_cover", "pressure_pad", *mine}
    fixed = [b.placed(n) for n in PARTS if n not in group | {"turn_button_left", "turn_button_right"}]
    fixed += [_turned_button(c, b, "left", 1), _turned_button(c, b, "right", 1)]
    axis = _cover_axis(c)
    for a in (5, 15, 30, 45, 60, 80, cv.open_deg):
        for name, shape in mine.items():
            v = _clashes_with(shape.rotate(axis, a), fixed)
            if v > 1e-2:
                problems.append(f"{a} deg open {name} {v:.2f}mm3")
    seat = b.placed("body").bounding_box().min.Z
    boxes = [shape.bounding_box() for shape in mine.values()]
    low = min(bx.min.Z for bx in boxes)
    inside = all(bx.min.X >= s.x_min - EPS and bx.max.X <= s.x_max + EPS and bx.min.Z >= s.z_min - EPS
                 and bx.max.Z <= sh.lip_top(c) + EPS for bx in boxes)
    face = [bx for bx in boxes if bx.min.X < FACE_REST_HALF_W and bx.max.X > -FACE_REST_HALF_W and bx.max.Z > FACE_REST_Z0]
    holder = mine["slide_holder"]
    table = next((a for a in range(int(cv.open_deg) + 1) if holder.rotate(axis, a).bounding_box().min.Z < seat), None)
    ok = not problems and low >= seat + SEAT_CLEAR - EPS and inside and not face
    return ok, ((f"{'; '.join(problems[:4])}; " if problems else "")
                + f"clear closed and at 5-{cv.open_deg} deg; lowest Z {low:.1f} over the seat at {seat:.2f}; "
                  f"inside the cover outline {inside}; face rest X +/-{FACE_REST_HALF_W} above Z {FACE_REST_Z0} "
                  f"clear {not face}; on a table the holder meets it at {table} deg open")
