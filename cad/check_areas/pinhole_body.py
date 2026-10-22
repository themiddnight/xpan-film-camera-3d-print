"""Geometry checks for the body and the pinhole module, probed on the placed solids."""
from build123d import Align, Axis, Box, Edge, Part, Pos, Rot, Solid, Vector

from checklib import EPS, SHOOTING, check, posed
from params import Camera
from parts import PARTS
from parts.pinhole_body import LEAVES, cheek_x, fold_axis, knuckle_x, leaf, rect_wire

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
FIELD_TOL = 0.02           # finder field within 2% of the film frame's, across and up
EYE_TOL = 1.0              # the across and up eye points agree this closely, and sit this close to the rear cover's face, mm
AXIS_TOL = 0.05            # window centres on one line parallel to the lens axis
SIGHT_MARGIN = 0.5         # sight lines clear every other part by this much
SIGHT_INSET = 0.2          # ...and pass this far inside the frames' own edges
OVERLAP_TOL = 0.01         # mm3; matches the assembly overlap rule
DETENT_TURN = 10.0         # deg off a pose at which the detent must already be pressing
DETENT_SWEEP_MM3 = 4.0     # two pads pushed 0.3mm by the knuckle round: 2.7mm3 per leaf at 45 deg
FOLD_STEPS = 9
FINDER = tuple(f"viewfinder_{w}_{k}" for w in LEAVES for k in ("frame", "hinge", "pins"))


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
             for n in ("pinhole_body", "m42_shim_ring", "m42_rear_cap_ring", "m42_body_cap")}
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
    face = _first_run(b.placed("pinhole_body"), (0, start, r), (0, 1, 0))
    cap = _first_run(b.placed("m42_body_cap"), (0, start, r), (0, 1, 0))
    gap = cap[0] - face[1]
    return gap >= 0.2 - EPS, f"body front face {gap:.2f}mm behind the cap flange"


@check("baffles clear the image cone by 0.5mm (geometry)")
def _(c, b):
    hit = _hit(_image_cone(c, _apex_y(b), CONE_MARGIN), b.placed("pinhole_body"))
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
    body = b.placed("pinhole_body")
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
    body = b.placed("pinhole_body")
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
    k, body = c.body_link, b.placed("pinhole_body")
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
    seat = b.placed("pinhole_body").bounding_box().min.Z
    z, name = next((z, n) for z, n in _lowest(b) if n != "pinhole_body")
    return z - seat >= PLATE_CLEAR - EPS, f"seat Z {seat:.2f}, next lowest {name} at {z:.2f}: {z - seat:.2f}mm clear (need {PLATE_CLEAR})"


@check("camera stands level on its three feet, centre of mass inside them (geometry)")
def _(c, b):
    body = b.placed("pinhole_body")
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
    bd, body, nut = c.body, b.placed("pinhole_body"), b.placed("tripod_nut")
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
    from parts.pinhole_body import nut_z0
    nut_top = nut_z0(c) + bd.nut_t + bd.nut_clearance
    pocket = (bd.m42_floor_y + bd.front_face_y) / 2
    rays = [("pinhole_body", f"side wall Y{y:.0f}", (0, y, 0), (1, 0, 0)) for y in (c.gate.datum_y + 1, 30.0)]
    rays += [("pinhole_body", f"{n} wall", (0, c.gate.datum_y + 3, 0), (0, 0, s)) for n, s in (("top", 1), ("bottom", -1))]
    rays += [("pinhole_body", f"M42 pocket wall {n}", (0, pocket, 0), d) for n, d in (("X", (1, 0, 0)), ("top", (0, 0, 1)), ("bottom", (0, 0, -1)))]
    rays += [("pinhole_body", "M42 pocket wall at the front face", (0, bd.front_face_y - 0.1, 0), (1, 0, 0))]
    rays += [
        ("pinhole_body", "nut pocket to boss front", (0, bd.tripod_y, nut_top - 0.05), (0, 1, 0)),
        ("pinhole_body", "nut pocket corner to boss side", (0, bd.tripod_y, nut_z0(c) + bd.nut_t / 2), (-1, 0, 0)),
        ("pinhole_body", "nut pocket to latch slot at the nut", (0, bd.tripod_y, nut_z0(c) + bd.nut_t / 2), (0, -1, 0)),
        ("pinhole_body", "nut pocket floor", (0, bd.tripod_y + (bd.tripod_screw_hole + bd.nut_af) / 4, nut_z0(c) + 0.1), (0, 0, -1)),
        ("pinhole_body", "screw hole to latch slot", (0, bd.tripod_y, c.body_link.latch_cantilever_top_z + bd.latch_gap / 2), (0, -1, 0)),
        ("pinhole_body", "screw hole to chamber", (0, bd.tripod_y, nut_top + bd.tripod_screw_depth - 0.05), (0, 0, 1)),
    ]
    for which in LEAVES:
        lf = leaf(c, which)
        k0, k1 = knuckle_x(c, which)
        cheek = sum(cheek_x(c, which)) / 2
        rays += [
            (f"viewfinder_{which}_hinge", f"{which} hinge cheek over the pin", (cheek, lf.axle_y, lf.axle_z), (0, 0, 1)),
            (f"viewfinder_{which}_hinge", f"{which} hinge strip beside the tongue",
             (k0 - v.tongue_len / 2, lf.axle_y - v.base_d / 2 - 0.5, c.body.z_max + v.base_t / 2), (0, 1, 0)),
            # Toward the flat on the fold side, where the knuckle is thinnest.
            (f"viewfinder_{which}_frame", f"{which} knuckle flat over the bore", ((k0 + k1) / 2, lf.axle_y, lf.axle_z),
             (0, 1 if lf.fold < 0 else -1, 0)),
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


# Viewfinder: measured on the built leaves, posed the way the hinges turn them.

def _meet(a, b) -> bool:
    """Bounding boxes share space (BoundBox.overlaps misses one box inside the other)."""
    return all(getattr(a.min, k) <= getattr(b.max, k) and getattr(b.min, k) <= getattr(a.max, k) for k in "XYZ")


def _turned_leaf(c: Camera, b, which: str, deg: float) -> Part:
    axis, origin = fold_axis(c, which)
    part = b.placed(f"viewfinder_{which}_frame")
    return part if deg == 0 else part.rotate(Axis(origin, axis), deg)


def _window(c: Camera, b, which: str) -> dict:
    """The window's edges in the leaf's front face (its sighting edges, since the leaf is thickest there)."""
    v, lf = c.viewfinder, leaf(c, which)
    part = b.placed(f"viewfinder_{which}_frame")
    start = lf.axle_y - 10.0
    bar = _first_run(part, (0, start, v.axis_z + lf.h / 2 + v.bar / 2), (0, 1, 0), 20.0)
    face = start + bar[1]
    probe = (0, face - 0.02, v.axis_z)
    right, left = (_first_run(part, probe, (s, 0, 0), 60.0)[0] for s in (1, -1))
    up, down = (_first_run(part, probe, (0, 0, s), 40.0)[0] for s in (1, -1))
    return {"y": face, "hw": (right + left) / 2, "hh": (up + down) / 2,
            "xc": (right - left) / 2, "zc": v.axis_z + (up - down) / 2}


def _finder(c: Camera, b) -> dict:
    r, f = _window(c, b, "rear"), _window(c, b, "front")
    d = f["y"] - r["y"]
    kx, kz = (f["hw"] - r["hw"]) / d, (f["hh"] - r["hh"]) / d
    return {"rear": r, "front": f, "kx": kx, "kz": kz,
            "eye_x": r["y"] - r["hw"] / kx, "eye_z": r["y"] - r["hh"] / kz}


@check("finder frames give the 65 x 24 field from one eye point (geometry)")
def _(c, b):
    fd = _finder(c, b)
    want = (c.film.frame_w / 2 / c.optics.pinhole_y, c.film.frame_h / 2 / c.optics.pinhole_y)
    err = (fd["kx"] / want[0] - 1, fd["kz"] / want[1] - 1)
    r, f = fd["rear"], fd["front"]
    axis = max(abs(r["zc"] - f["zc"]), abs(r["xc"]), abs(f["xc"]))
    ok = max(map(abs, err)) <= FIELD_TOL and abs(fd["eye_x"] - fd["eye_z"]) <= EYE_TOL and axis <= AXIS_TOL
    return ok, (f"rear {2 * r['hw']:.2f} x {2 * r['hh']:.2f} at Y {r['y']:.2f}, front {2 * f['hw']:.2f} x "
                f"{2 * f['hh']:.2f} at Y {f['y']:.2f}: field {err[0]:+.1%} across, {err[1]:+.1%} up; eye at Y "
                f"{fd['eye_x']:.2f} / {fd['eye_z']:.2f}, centres off the axis line {axis:.3f}mm")


@check("finder stays ahead of the body rear face, eye point on the rear cover (geometry)")
def _(c, b):
    rear_face = b.placed("pinhole_body").bounding_box().min.Y
    back = min(b.placed(n).bounding_box().min.Y for n in FINDER)
    fd = _finder(c, b)
    eye = (fd["eye_x"] + fd["eye_z"]) / 2
    cover = b.placed("rear_cover").bounding_box().min.Y
    ok = back >= rear_face - EPS and abs(cover - eye) <= EYE_TOL
    return ok, (f"finder from Y {back:.2f}, body rear face {rear_face:.2f}; eye at Y {eye:.2f}, "
                f"{cover - eye:+.2f}mm from the rear cover's face (camera against the face)")


def _sight_cone(eye: float, w: dict, grow: float, to_y: float) -> Solid:
    """Every line of sight from the eye through the front window, out to to_y, grown by grow."""
    k = (to_y - eye) / (w["y"] - eye)
    return Pos(0, 0, w["zc"]) * Solid.make_loft([rect_wire(eye, APEX_HALF + grow, APEX_HALF + grow),
                                                 rect_wire(to_y, w["hw"] * k + grow, w["hh"] * k + grow)])


@check("finder sight lines clear in the shooting pose (geometry)")
def _(c, b):
    fd = _finder(c, b)
    eye = (fd["eye_x"] + fd["eye_z"]) / 2
    front = fd["front"]
    beyond = max(b.placed(n).bounding_box().max.Y for n in PARTS) + 1.0
    clear = _sight_cone(eye, front, SIGHT_MARGIN, beyond)
    inside = _sight_cone(eye, front, -SIGHT_INSET, front["y"])
    beyond = clear & Pos(0, front["y"] + EPS, 0) * Box(1000, 1000, 1000, align=(Align.CENTER, Align.MIN, Align.CENTER))
    frames = {f"viewfinder_{w}_frame" for w in LEAVES}
    rear_folded = _turned_leaf(c, b, "rear", leaf(c, "rear").fold)
    shooting = posed(c, b, SHOOTING)
    hits = {}
    for name in [*PARTS, "rear sight folded"]:
        part = rear_folded if name == "rear sight folded" else shooting.get(name, b.placed(name))
        # A frame sights with its window edges, so only the field beyond its window must be clear of it.
        for cone in (inside, beyond) if name in frames else (clear,):
            if _meet(part.bounding_box(), cone.bounding_box()):
                vol = _hit(cone, part)
                if vol > EPS:
                    hits[name] = round(hits.get(name, 0.0) + vol, 3)
    return not hits, f"blocked by {hits}" if hits else (
        f"eye through the front window and on past the lens clear of every part by {SIGHT_MARGIN}mm, "
        f"of the frames' edges by {SIGHT_INSET}mm, rear sight raised or folded")


def _folded(c: Camera, b, rear: float = 1.0, front: float = 1.0) -> dict[str, Part]:
    """Both leaves turned the given fraction of their fold."""
    return {f"viewfinder_{w}_frame": _turned_leaf(c, b, w, leaf(c, w).fold * t) for w, t in (("rear", rear), ("front", front))}


def _clashes(b, shapes: dict[str, Part], allowed: dict[frozenset, float]) -> list[str]:
    out = []
    for name, shape in shapes.items():
        box = shape.bounding_box()
        for other in PARTS:
            if other == name or (other in shapes and other < name):
                continue
            other_shape = shapes.get(other, b.placed(other))
            if not _meet(box, other_shape.bounding_box()):
                continue
            vol = _hit(shape, other_shape)
            if vol > allowed.get(frozenset((name, other)), OVERLAP_TOL):
                out.append(f"{name} x {other} {vol:.2f}mm3")
    return out


@check("folded finder lies inside the body top outline and under the height limit (geometry)")
def _(c, b):
    body = b.placed("pinhole_body")
    top = c.body.z_max
    bb = body.bounding_box()
    shapes = {n: b.placed(n) for n in FINDER} | _folded(c, b)
    worst, where = float("inf"), ""
    for name, shape in shapes.items():
        for p in shape.vertices():
            if not bb.min.Y <= p.Y <= bb.max.Y:
                worst, where = -1.0, f"{name} at Y {p.Y:.2f}"
                break
            run = _first_run(body, (0, p.Y, top - 2.0), (1 if p.X >= 0 else -1, 0, 0), 100.0)
            margin = run[1] - abs(p.X)
            if margin < worst:
                worst, where = margin, f"{name} at X {p.X:.2f} Y {p.Y:.2f}"
    height = max(s.bounding_box().max.Z for s in shapes.values()) - top
    ok = worst >= -EPS and height <= c.viewfinder.fold_height + EPS
    return ok, (f"closest to the outline {worst:.2f}mm ({where}); folded top {height:.2f}mm over the body top "
                f"(limit {c.viewfinder.fold_height})")


@check("finder folds and unfolds without a clash (geometry)")
def _(c, b):
    detent = {frozenset((f"viewfinder_{w}_frame", f"viewfinder_{w}_hinge")): DETENT_SWEEP_MM3 for w in LEAVES}
    problems = []
    for i in range(1, FOLD_STEPS + 1):
        t = i / FOLD_STEPS
        for label, shapes in (("rear", _folded(c, b, rear=t, front=0.0)), ("front", _folded(c, b, front=t))):
            problems += [f"{label} at {t:.0%}: {p}" for p in _clashes(b, shapes, detent)]
    folded = _clashes(b, _folded(c, b), {})
    problems += [f"folded: {p}" for p in folded]
    return not problems, "; ".join(problems[:6]) if problems else (
        f"rear sight then front frame folded in {FOLD_STEPS} steps; only the detent pads give, folded pose clear")


@check("finder detents hold each frame raised and folded (geometry)")
def _(c, b):
    out, ok = [], True
    for which in LEAVES:
        hinge = b.placed(f"viewfinder_{which}_hinge")
        for pose in (0.0, leaf(c, which).fold):
            at = _hit(_turned_leaf(c, b, which, pose), hinge)
            off = min(_hit(_turned_leaf(c, b, which, pose + s * DETENT_TURN), hinge) for s in (1, -1))
            ok &= at <= OVERLAP_TOL and off > OVERLAP_TOL
            out.append(f"{which} {pose:.0f}: {at:.3f} / {off:.2f}mm3")
    return ok, f"pad overlap in pose / {DETENT_TURN:.0f} deg off it: " + ", ".join(out)
