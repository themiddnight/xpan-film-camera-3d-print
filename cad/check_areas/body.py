"""Geometry checks for the body and the pinhole module, probed on the placed solids."""
from build123d import Box, Edge, Part, Pos, Rot, Solid, Vector

from checklib import EPS, check
from params import Camera
from parts import PARTS
from parts.body import rect_wire

CONE_MARGIN = 0.5
SEAT_TOL = 0.01
PINHOLE_TOL = 0.3
FIELD_DEPTH = 25.0
APEX_HALF = 0.01
PLATE_CLEAR = 0.5          # a tripod plate seated on the feet must clear every other part by this much
SCREW_LEN = 5.0            # typical 1/4"-20 tripod screw protrudes 4.5 to 6.5mm; take a short one
THREAD_PITCH = 25.4 / 20
MIN_THREADS = 2.5          # a 4.5mm screw still gets 2.6 threads on the shipped floor
COM_MARGIN = 3.0           # centre of mass this far inside the support polygon
SLICE_T = 0.05


def _runs(part: Part, start, direction, length: float) -> list[tuple[float, float]]:
    """Solid intervals (distance from start) along a segment."""
    s, d = Vector(*start), Vector(*direction).normalized()
    hits = part.intersect(Edge.make_line(s, s + d * length))
    if not hits:
        return []
    spans = []
    for e in hits.edges():
        a, b = (e.position_at(0) - s).dot(d), (e.position_at(1) - s).dot(d)
        spans.append((min(a, b), max(a, b)))
    return sorted(spans)


def _first_run(part, start, direction, length=40.0):
    runs = _runs(part, start, direction, length)
    return runs[0] if runs else None


def _apex_y(b) -> float:
    return b.placed("pinhole_shim").bounding_box().min.Y


def _loft(y0, hw0, hh0, y1, hw1, hh1) -> Solid:
    return Solid.make_loft([rect_wire(y0, hw0, hh0), rect_wire(y1, hw1, hh1)])


def _image_cone(c: Camera, apex: float, margin: float) -> Solid:
    """Every ray from the 65 x 24 frame to the pinhole, grown by margin."""
    return _loft(0.0, c.film.frame_w / 2 + margin, c.film.frame_h / 2 + margin, apex, APEX_HALF + margin, APEX_HALF + margin)


def _field_cone(c: Camera, apex: float, margin: float) -> Solid:
    """The same rays continued in front of the pinhole: the field of view."""
    k = FIELD_DEPTH / c.optics.pinhole_y
    return _loft(apex, APEX_HALF, APEX_HALF, apex + FIELD_DEPTH,
                 c.film.frame_w / 2 * k + margin, c.film.frame_h / 2 * k + margin)


def _hit(a: Part, b: Part) -> float:
    r = a & b
    return r.volume if r is not None else 0.0


@check("pinhole plane 50.0 from the film plane, M42 stack seated (geometry)")
def _(c, b):
    r = (c.optics.m42_thread_d / 2 + c.measured.m42_rear_cap_od / 2) / 2
    start = c.body.m42_floor_y - 1.0
    spans = {n: _first_run(b.placed(n), (0, start, r), (0, 1, 0), 30.0)
             for n in ("body", "m42_shim_ring", "m42_rear_cap_ring", "m42_body_cap")}
    if None in spans.values():
        return False, f"probe at r={r:.1f} missed {[n for n, s in spans.items() if s is None]}"
    order = list(spans.values())
    seated = all(abs(order[i][1] - order[i + 1][0]) < SEAT_TOL for i in range(len(order) - 1))
    plane = start + order[-1][1]
    apex = _apex_y(b)
    ok = seated and abs(plane - c.optics.pinhole_y) <= PINHOLE_TOL and abs(apex - plane) < SEAT_TOL
    return ok, f"pinhole plane Y {plane:.2f} (shim at {apex:.2f}), stack seated {seated}"


@check("body cap flange seats on the ring, not the body (geometry)")
def _(c, b):
    r = (c.measured.m42_rear_cap_od / 2 + c.measured.m42_body_cap_od / 2) / 2
    start = c.body.m42_floor_y
    face = _first_run(b.placed("body"), (0, start, r), (0, 1, 0))
    cap = _first_run(b.placed("m42_body_cap"), (0, start, r), (0, 1, 0))
    gap = cap[0] - face[1]
    return gap >= 0.2 - EPS, f"body front face {gap:.2f}mm behind the cap flange"


@check("baffles clear the image cone by 0.5mm (geometry)")
def _(c, b):
    hit = _hit(_image_cone(c, _apex_y(b), CONE_MARGIN), b.placed("body"))
    return hit < EPS, f"cone from the frame edges to the pinhole, grown {CONE_MARGIN}mm, cuts {hit:.3f} mm3 of body"


@check("M42 mount clears the corner rays (geometry)")
def _(c, b):
    apex = _apex_y(b)
    rear = _image_cone(c, apex, CONE_MARGIN)
    front = _field_cone(c, apex, CONE_MARGIN)
    hits = {n: _hit(rear, b.placed(n)) for n in ("m42_shim_ring", "m42_rear_cap_ring", "m42_body_cap")}
    hits["m42_body_cap"] += _hit(front, b.placed("m42_body_cap"))
    hits["pinhole_shim"] = _hit(_field_cone(c, apex, 0.0), b.placed("pinhole_shim"))
    bad = {n: round(v, 3) for n, v in hits.items() if v > EPS}
    return not bad, f"hits {bad}" if bad else f"clear, rays grown {CONE_MARGIN}mm"


@check("body rear face on the datum, inside the bridge span (geometry)")
def _(c, b):
    body = b.placed("body")
    bb = body.bounding_box()
    y = c.gate.datum_y
    on_datum = abs(bb.min.Y - y) < SEAT_TOL
    corners = [(c.body.rear_half_w - 1, 0), (0, c.body.z_max - 1), (c.body.rear_half_w - 1, c.body.z_min + 1),
               (-c.body.rear_half_w + 1, c.body.z_min + 1)]
    contact = all(body.is_inside(Vector(x, y + 0.05, z)) for x, z in corners)
    span = c.shell.bridge_half_span - max(abs(bb.min.X), abs(bb.max.X))
    ok = on_datum and contact and span >= 0.5 - EPS
    return ok, f"rear face Y {bb.min.Y:.2f}, contact {contact}, {span:.2f}mm inside the bridge span"


@check("body tongue fits the hook slot with clearance (geometry)")
def _(c, b):
    k, clr = c.body_link, c.fit.fdm_clearance
    body = b.placed("body")
    z = (k.hook_slot_top_z + c.body.z_max) / 2 + 0.5
    y_run = _first_run(body, (0, k.hook_slot_y[0] - 1, z), (0, 1, 0), 5.0)
    if y_run is None:
        return False, "no tongue in the hook slot"
    y0, y1 = k.hook_slot_y[0] - 1 + y_run[0], k.hook_slot_y[0] - 1 + y_run[1]
    top = c.body.z_max + _first_run(body, (0, (y0 + y1) / 2, c.body.z_max), (0, 0, 1), 10.0)[1]
    gaps = (y0 - k.hook_slot_y[0], k.hook_slot_y[1] - y1, k.hook_slot_top_z - top)
    return min(gaps) >= clr - EPS, "Y {:.2f}/{:.2f}, top {:.2f}mm".format(*gaps)


@check("latch hook sits behind the pin and rises past its centre (geometry)")
def _(c, b):
    k, body = c.body_link, b.placed("body")
    pin_rear = k.latch_pin_y - c.measured.rod_d / 2
    z = k.latch_cantilever_top_z + 0.5
    run = _first_run(body, (0, c.gate.datum_y - 1, z), (0, 1, 0), 10.0)
    front = c.gate.datum_y - 1 + run[1]
    up = _first_run(body, (0, front - 0.2, c.body.z_min - 1), (0, 0, 1), 10.0)
    top = c.body.z_min - 1 + up[1]
    free = not body.is_inside(Vector(0, (c.body.notch_y1 + c.body.latch_root_y) / 2,
                                     k.latch_cantilever_top_z + c.body.latch_gap / 2))
    ok = 0 <= pin_rear - front <= 0.5 and top >= k.latch_pin_z + 0.2 and free
    return ok, f"hook front {pin_rear - front:.2f}mm behind the pin, top {top - k.latch_pin_z:+.2f}mm over its centre, beam free {free}"


def _lowest(b) -> list[tuple[float, str]]:
    return sorted((b.placed(n).bounding_box().min.Z, n) for n in PARTS)


def _hull(points):
    """Convex hull, counter-clockwise (monotone chain)."""
    pts = sorted(set(points))

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (p[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]
    return half(pts) + half(pts[::-1])


def _inside_margin(hull, p) -> float:
    """Smallest distance from p to a hull edge; negative when p is outside."""
    worst = float("inf")
    for (ax, ay), (bx, by) in zip(hull, hull[1:] + hull[:1]):
        ex, ey = bx - ax, by - ay
        worst = min(worst, (ex * (p[1] - ay) - ey * (p[0] - ax)) / (ex * ex + ey * ey) ** 0.5)
    return worst


def _seat_patches(body: Part, seat: float) -> list[list[tuple[float, float]]]:
    """Outline points of each separate piece of the body that touches the seat plane."""
    slab = body & (Pos(0, 0, seat + SLICE_T / 2) * Box(400, 400, SLICE_T))
    patches = []
    for island in slab.solids():
        bottom = min(island.faces(), key=lambda f: f.center().Z)
        patches.append([(p.X, p.Y) for e in bottom.edges() for p in (e @ (i / 8) for i in range(9))])
    return patches


@check("tripod seat is the lowest plane, plate-clear of the hinge knuckles (geometry)")
def _(c, b):
    seat = b.placed("body").bounding_box().min.Z
    z, name = next((z, n) for z, n in _lowest(b) if n != "body")
    return z - seat >= PLATE_CLEAR - EPS, f"seat Z {seat:.2f}, next lowest {name} at {z:.2f}: {z - seat:.2f}mm clear (need {PLATE_CLEAR})"


@check("camera stands level on its three feet, centre of mass inside them (geometry)")
def _(c, b):
    body = b.placed("body")
    seat = body.bounding_box().min.Z
    patches = _seat_patches(body, seat)
    parts = [(b.placed(n).volume, b.placed(n).center()) for n in PARTS]
    total = sum(v for v, _ in parts)
    com = (sum(v * p.X for v, p in parts) / total, sum(v * p.Y for v, p in parts) / total)
    margin = _inside_margin(_hull([pt for patch in patches for pt in patch]), com) if len(patches) >= 3 else float("-inf")
    ok = len(patches) == 3 and margin >= COM_MARGIN - EPS
    return ok, f"{len(patches)} patches within {SLICE_T}mm of the seat, centre of mass X {com[0]:.1f} Y {com[1]:.1f} is {margin:.1f}mm inside them (need {COM_MARGIN})"


@check("a 5mm tripod screw reaches the nut through a clear hole (geometry)")
def _(c, b):
    bd, body, nut = c.body, b.placed("body"), b.placed("tripod_nut")
    seat = body.bounding_box().min.Z
    ring = (bd.nut_bore + bd.nut_af) / 4
    run = _first_run(nut, (ring, bd.tripod_y, seat - 1), (0, 0, 1), 40.0)
    if run is None:
        return False, "no nut above the seat"
    bottom, top = seat - 1 + run[0], seat - 1 + run[1]
    r = bd.nut_bore / 2
    blocked = [off for off in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r))
               if _runs(body, (off[0], bd.tripod_y + off[1], seat - 1), (0, 0, 1), top - seat + 1)]
    engaged = min(SCREW_LEN - (bottom - seat), top - bottom)
    threads = engaged / THREAD_PITCH
    return not blocked and threads >= MIN_THREADS - EPS, f"nut bottom {bottom - seat:.2f}mm over the seat, {SCREW_LEN}mm screw engages {max(engaged, 0):.2f}mm = {max(threads, 0):.1f} threads (need {MIN_THREADS}), hole blocked at {blocked}"


def _wall_rays(c: Camera, b) -> list[tuple[str, str, tuple, tuple]]:
    bd, v = c.body, c.viewfinder
    from parts.body import nut_z0
    nut_top = nut_z0(c) + bd.nut_t + bd.nut_clearance
    pocket = (bd.m42_floor_y + bd.front_face_y) / 2
    rays = [("body", f"side wall Y{y:.0f}", (0, y, 0), (1, 0, 0)) for y in (c.gate.datum_y + 1, 30.0)]
    rays += [("body", f"{n} wall", (0, c.gate.datum_y + 3, 0), (0, 0, s)) for n, s in (("top", 1), ("bottom", -1))]
    rays += [("body", f"M42 pocket wall {n}", (0, pocket, 0), d) for n, d in (("X", (1, 0, 0)), ("top", (0, 0, 1)), ("bottom", (0, 0, -1)))]
    rays += [("body", "M42 pocket wall at the front face", (0, bd.front_face_y - 0.1, 0), (1, 0, 0))]
    rays += [
        ("body", "nut pocket to boss front", (0, bd.tripod_y, nut_top - 0.05), (0, 1, 0)),
        ("body", "nut pocket corner to boss side", (0, bd.tripod_y, nut_z0(c) + bd.nut_t / 2), (-1, 0, 0)),
        ("body", "nut pocket to latch slot at the nut", (0, bd.tripod_y, nut_z0(c) + bd.nut_t / 2), (0, -1, 0)),
        ("body", "nut pocket floor", (0, bd.tripod_y + (bd.tripod_screw_hole + bd.nut_af) / 4, nut_z0(c) + 0.1), (0, 0, -1)),
        ("body", "screw hole to latch slot", (0, bd.tripod_y, c.body_link.latch_cantilever_top_z + bd.latch_gap / 2), (0, -1, 0)),
        ("body", "screw hole to chamber", (0, bd.tripod_y, nut_top + bd.tripod_screw_depth - 0.05), (0, 0, 1)),
        ("viewfinder_hinge_right", "hinge over the wire", (v.hinge_x, v.axle_y, v.axle_z), (0, 0, 1)),
    ]
    return rays


@check("body walls >= min wall (geometry)")
def _(c, b):
    thin = []
    for part, label, start, d in _wall_rays(c, b):
        run = _first_run(b.placed(part), start, d)
        t = run[1] - run[0] if run else 0.0
        if t < c.print.min_wall - EPS:
            thin.append(f"{label} {t:.2f}")
    return not thin, f"thin: {thin}" if thin else f"all {len(_wall_rays(c, b))} probed walls >= {c.print.min_wall}mm"


@check("body and pinhole printed parts fit the print bed (geometry)")
def _(c, b):
    over = []
    for name, spec in PARTS.items():
        if spec.group in ("body", "pinhole") and spec.print_rotation is not None:
            size = (Rot(*spec.print_rotation) * b.local(name)).bounding_box().size
            if max(size.X, size.Y) > c.print.bed:
                over.append(f"{name} {size.X:.0f} x {size.Y:.0f}")
    return not over, f"over: {over}" if over else "all fit"
