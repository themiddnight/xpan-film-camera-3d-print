"""Geometry checks for the film parts: the strip against the rails, hub, teeth and flanges, and the cassette in its chamber."""
import math

from build123d import Box, Pos, Vector

from checklib import check, radial_extent
from parts.film import FilmPath
from parts.sprocket import notch_angle, rest_rotation, tooth_angles

FACE_TOL = 0.01
SLAB_H = 10.0       # Z slab clear of both perforation rows
HOLE_SEARCH = 1.6   # mm each side of a tooth, beyond the half perforation
BISECT_STEPS = 20


def _bisect_edge(film, point_at, inside_at: float, outside_at: float) -> float:
    """Boundary between film material (inside_at) and a hole (outside_at), as a distance along the strip."""
    for _ in range(BISECT_STEPS):
        mid = (inside_at + outside_at) / 2
        if film.is_inside(point_at(mid)):
            inside_at = mid
        else:
            outside_at = mid
    return (inside_at + outside_at) / 2


def _polar(centre: Vector, r: float, angle_deg: float, z: float) -> Vector:
    a = math.radians(angle_deg)
    return Vector(centre.X + r * math.cos(a), centre.Y + r * math.sin(a), z)


def _sprocket_axis(c) -> Vector:
    return Vector(c.layout.sprocket_x, c.sprocket_y, 0)


@check("film lies on the rails across the gate (geometry)")
def _(c, b):
    film, t = b.local("film"), c.film.thickness
    off = []
    for x in (-c.film.frame_w / 2, 0.0, c.film.frame_w / 2):
        for z in (0.0, -c.gate.rail_z, c.gate.rail_z):
            on = film.is_inside(Vector(x, -FACE_TOL, z)) and film.is_inside(Vector(x, -t + FACE_TOL, z))
            clear = not film.is_inside(Vector(x, FACE_TOL, z)) and not film.is_inside(Vector(x, -t - FACE_TOL, z))
            if not (on and clear):
                off.append((x, z))
    return not off, f"film spans Y = -{t} to 0 at all 9 probes" if not off else f"film off Y = -{t}..0 at (X, Z) {off}"


@check("film run from gate centre to sprocket tangent (geometry)")
def _(c, b):
    sx = c.layout.sprocket_x
    clip = Pos(sx / 2, 0, 0) * Box(sx, 4.0, SLAB_H)
    length = (b.local("film") & clip).volume / (SLAB_H * c.film.thickness)
    return abs(length - sx) < 0.1, f"{length:.2f}mm of strip between X = 0 and the tangent at X = {sx}"


@check("film sits on the sprocket hub (geometry)")
def _(c, b):
    film, t = b.local("film"), c.film.thickness
    s = c.sprocket
    z = c.gate.rail_z  # edge band: over the hub land, clear of the perforation row and the tooth band
    hub_r = radial_extent(b.sprocket, notch_angle(c), z, s.relief_d / 2, s.flange_d / 2 - 0.2)
    axis, wrap = _sprocket_axis(c), FilmPath.of(c).wrap_deg
    bad = []
    for angle in (-90 + 0.25 * wrap, -90 + 0.75 * wrap):
        in_film = [film.is_inside(_polar(axis, hub_r + d, angle, z)) for d in (FACE_TOL, t - FACE_TOL)]
        out_film = [film.is_inside(_polar(axis, hub_r + d, angle, z)) for d in (-FACE_TOL, t + FACE_TOL)]
        if not all(in_film) or any(out_film):
            bad.append(round(angle, 1))
    return not bad, f"film fills r = {hub_r:.2f} to {hub_r + t:.2f} on the hub" if not bad else f"film not on the hub (r {hub_r:.2f}) at {bad} deg"


@check("perforation centred on every tooth in the wrap (geometry)")
def _(c, b):
    film, sprocket = b.local("film"), b.placed("sprocket")
    axis, path = _sprocket_axis(c), FilmPath.of(c)
    r, z0 = path.sprocket_r, -c.film.perf_row_z
    root = c.fit.tooth_along_root
    probes = [(da, dz) for da in (-root / 3, 0.0, root / 3) for dz in (-c.fit.tooth_across / 3, c.fit.tooth_across / 3)]
    report, ok = [], True
    for a0 in tooth_angles(c):
        angle = (rest_rotation(c) + a0 + 180) % 360 - 180
        if not -90 <= angle <= path.leave_deg:
            continue

        def at(d, dz=0.0):
            return _polar(axis, r, angle + math.degrees(d / r), z0 + dz)

        if film.is_inside(at(0)):
            ok = False
            report.append(f"{angle:.1f} deg: tooth centre inside film material FAIL")
            continue
        lo = _bisect_edge(film, at, -HOLE_SEARCH, 0.0)
        hi = _bisect_edge(film, at, HOLE_SEARCH, 0.0)
        centre, width = (hi + lo) / 2, hi - lo
        tooth_clear = all(sprocket.is_inside(at(da, dz)) and not film.is_inside(at(da, dz)) for da, dz in probes)
        good = tooth_clear and abs(centre) <= 0.12 and abs(width - c.film.perf_along) <= 0.08
        ok &= good
        report.append(f"{angle:.1f} deg: hole {width:.2f} wide, {centre:+.2f} off tooth" + ("" if good else " FAIL"))
    if not report:
        return False, "no tooth in the wrap"
    return ok, "; ".join(report)


@check("film clears the sprocket flanges (geometry)")
def _(c, b):
    s = c.sprocket
    r = (s.hub_d + s.flange_d) / 4
    angle = notch_angle(c)
    faces = []
    for sign in (-1, 1):
        lo, hi = 0.0, sign * (s.flange_gap / 2 + s.flange_t / 2)
        for _ in range(BISECT_STEPS):
            mid = (lo + hi) / 2
            if b.sprocket.is_inside(Vector(r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle)), mid)):
                hi = mid
            else:
                lo = mid
        faces.append(lo)
    bb = b.local("film").bounding_box()
    clearance = min(bb.min.Z - faces[0], faces[1] - bb.max.Z)
    gap = faces[1] - faces[0]
    return clearance >= 0.1, f"film {bb.max.Z - bb.min.Z:.2f}mm wide in a {gap:.2f}mm flange gap, {clearance:.2f}mm to the nearer flange"


@check("cassette fits its chamber (geometry)")
def _(c, b):
    bb, s = b.local("cassette").bounding_box(), c.shell
    x0, x1 = s.x_min + s.outer_wall, -(s.bridge_half_span + s.divider_wall)
    y0, y1 = c.bought.chamber_y_min, s.y_front - s.outer_wall
    margins = {
        "X-": bb.min.X - x0, "X+": x1 - bb.max.X, "Y-": bb.min.Y - y0, "Y+": y1 - bb.max.Y, "ceiling": s.ceiling_z - bb.max.Z,
    }
    tight = {k: round(v, 2) for k, v in margins.items() if v < 0}
    return not tight, f"X {bb.min.X:.2f} to {bb.max.X:.2f}, Y {bb.min.Y:.2f} to {bb.max.Y:.2f}, top Z {bb.max.Z:.2f}" + (f"; over by {tight}" if tight else "")
