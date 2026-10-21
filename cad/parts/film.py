"""Bought film parts: the 135 cassette in its chamber and the loaded film strip.

Both are reference solids at their true size and position, built in camera coordinates
(docs/design/film-back.md 17.1, 17.4, 17.5). Values come from `Measured` and `Bought`.

Values chosen where a doc gave a range or left a value open:
- Lip envelope 29.5mm is read as the cassette's extent along X, centred on the axis, because the
  chamber is only 32mm wide. The lip block reaches X = cassette_x + 14.75 on the gate side.
- Spool top end is a 6.0mm cylinder, key slot 2.6mm wide and 4.5mm deep cut along X from the tip.
  The BOM gives the slot, not the end diameter. The rewind fork also has a 2.6mm slot, so the
  fork and this spool end do not mate as modeled; the fork stream decides which side holds the blade.
- Bottom stub is 5.0mm in diameter and 2.5mm long (doc gives the length only).
- Felt lips are one block with a 0.33mm slit around the film (0.10mm clearance each side),
  starting 3.0mm behind the cassette axis, 37mm long between the end caps.
- Strip starts 3.0mm inside the lip tip. Perforations are cut along the whole strip.
- Take-up roll: a solid annulus from the 16mm core to the mid-roll surface, plus the last 300 degrees
  of the strip wound over it as a sheet. Roll diameter 20mm is the outer film surface.
- The film path is derived from the sprocket: the flat run is tangent to the bottom of the pitch circle,
  so a wrong hub or tooth count moves the film off the rails instead of being hidden.
"""
import math
from dataclasses import dataclass

from build123d import Box, Compound, Cylinder, Edge, Face, Location, Part, Pos, Vector, Wire, chamfer, extrude

from params import Camera
from parts.sprocket import rest_rotation
from parts.spec import PartSpec, at_origin

OVERSHOOT = 1.0  # boolean cut slack past a face, not a dimension


@dataclass(frozen=True)
class FilmPath:
    """Neutral axis of the strip in the XY plane, parametrised by arc length s.

    s = 0 at the sprocket tangent point (hub bottom). Flat run for s < 0 along +X, then a
    counter-clockwise arc round the sprocket, a straight run on the internal tangent, and a
    clockwise arc round the take-up roll. The emulsion is on the left of travel.
    """
    t: float
    start_x: float
    sprocket: tuple[float, float]
    sprocket_r: float
    spool: tuple[float, float]
    spool_r: float
    roll_wrap_deg: float

    @classmethod
    def of(cls, c: Camera) -> "FilmPath":
        b = c.bought
        lip_tip = c.layout.cassette_x + c.measured.cassette_lip_envelope / 2
        return cls(
            t=c.film.thickness,
            start_x=lip_tip - b.film_in_lip,
            sprocket=(c.layout.sprocket_x, c.sprocket_y),
            sprocket_r=c.pitch_d / 2,
            spool=(c.layout.spool_x, c.layout.spool_y),
            spool_r=(b.roll_d - c.film.thickness) / 2,
            roll_wrap_deg=b.roll_wrap_deg,
        )

    @property
    def flat_y(self) -> float:
        return self.sprocket[1] - self.sprocket_r

    @property
    def _centre_line(self) -> tuple[float, float]:
        return self.spool[0] - self.sprocket[0], self.spool[1] - self.sprocket[1]

    @property
    def leave_deg(self) -> float:
        """Sprocket angle where the film leaves on the internal tangent to the roll."""
        dx, dy = self._centre_line
        return math.degrees(math.atan2(dy, dx) - math.acos(min(1.0, (self.sprocket_r + self.spool_r) / math.hypot(dx, dy))))

    @property
    def wrap_deg(self) -> float:
        return self.leave_deg + 90.0

    @property
    def s_min(self) -> float:
        return self.start_x - self.sprocket[0]

    @property
    def arc_len(self) -> float:
        return self.sprocket_r * math.radians(self.wrap_deg)

    @property
    def straight_len(self) -> float:
        dx, dy = self._centre_line
        return math.sqrt(max(0.0, dx * dx + dy * dy - (self.sprocket_r + self.spool_r) ** 2))

    @property
    def roll_len(self) -> float:
        return self.spool_r * math.radians(self.roll_wrap_deg)

    @property
    def s_max(self) -> float:
        return self.arc_len + self.straight_len + self.roll_len

    @property
    def leave_point(self) -> tuple[float, float]:
        a = math.radians(self.leave_deg)
        return self.sprocket[0] + self.sprocket_r * math.cos(a), self.sprocket[1] + self.sprocket_r * math.sin(a)

    @property
    def straight_dir(self) -> tuple[float, float]:
        a = math.radians(self.leave_deg)
        return -math.sin(a), math.cos(a)

    @property
    def roll_start_deg(self) -> float:
        return self.leave_deg + 180.0

    def at(self, s: float) -> tuple[float, float, float]:
        """Neutral-axis point (x, y) and heading in degrees at arc length s."""
        if s <= 0:
            return self.sprocket[0] + s, self.flat_y, 0.0
        if s <= self.arc_len:
            a = -90.0 + math.degrees(s / self.sprocket_r)
            return (self.sprocket[0] + self.sprocket_r * math.cos(math.radians(a)),
                    self.sprocket[1] + self.sprocket_r * math.sin(math.radians(a)), a + 90.0)
        s -= self.arc_len
        if s <= self.straight_len:
            (px, py), (ux, uy) = self.leave_point, self.straight_dir
            return px + ux * s, py + uy * s, self.wrap_deg
        psi = self.roll_start_deg - math.degrees((s - self.straight_len) / self.spool_r)
        return (self.spool[0] + self.spool_r * math.cos(math.radians(psi)),
                self.spool[1] + self.spool_r * math.sin(math.radians(psi)), psi - 90.0)

    def side_edges(self, offset: float) -> list[Edge]:
        """One face of the strip. offset +1 is the emulsion face (left of travel), -1 the base face."""
        h = offset * self.t / 2
        sx, sy = self.sprocket
        cx, cy = self.spool

        def pt(x, y):
            return Vector(x, y, 0)

        def arc(centre, r, a0, a1):
            a, b, c = (math.radians(x) for x in (a0, (a0 + a1) / 2, a1))
            return Edge.make_three_point_arc(*(pt(centre[0] + r * math.cos(x), centre[1] + r * math.sin(x)) for x in (a, b, c)))

        leave = self.leave_deg
        la = math.radians(leave)
        nl = (-math.cos(la), -math.sin(la))
        px, py = self.leave_point
        ux, uy = self.straight_dir
        n = self.straight_len
        return [
            Edge.make_line(pt(self.start_x, self.flat_y + h), pt(sx, self.flat_y + h)),
            arc((sx, sy), self.sprocket_r - h, -90.0, leave),
            Edge.make_line(pt(px + nl[0] * h, py + nl[1] * h), pt(px + ux * n + nl[0] * h, py + uy * n + nl[1] * h)),
            arc((cx, cy), self.spool_r + h, self.roll_start_deg, self.roll_start_deg - self.roll_wrap_deg),
        ]


def perforation_positions(c: Camera, path: FilmPath) -> list[float]:
    """Arc lengths of perforation centres: one on every sprocket tooth at rest, spaced by the KS pitch."""
    pitch = c.film.perf_pitch
    tooth = path.sprocket_r * math.radians(rest_rotation(c) + 90.0)
    first = tooth + c.bought.film_phase
    margin = c.film.perf_along / 2 + c.bought.perf_end_margin
    k0 = math.ceil((path.s_min + margin - first) / pitch)
    k1 = math.floor((path.s_max - margin - first) / pitch)
    return [first + k * pitch for k in range(k0, k1 + 1)]


def _strip(c: Camera, path: FilmPath) -> Part:
    f = c.film
    left, right = path.side_edges(+1), path.side_edges(-1)
    start_cap = Edge.make_line(left[0].start_point(), right[0].start_point())
    end_cap = Edge.make_line(left[-1].end_point(), right[-1].end_point())
    face = Face(Wire(left + [end_cap] + right + [start_cap]))
    sheet = extrude(face, amount=f.width / 2, both=True)

    cutter = Box(f.perf_along, c.bought.perf_cut_depth, f.perf_across)
    cutters = []
    for s in perforation_positions(c, path):
        x, y, heading = path.at(s)
        for sign in (-1, 1):
            cutters.append(Location((x, y, sign * f.perf_row_z), (0, 0, heading)) * cutter)
    return sheet - Compound(cutters)


def build_film(c: Camera) -> Part:
    path = FilmPath.of(c)
    f = c.film
    roll_r = c.bought.roll_d / 2
    core_r = c.takeup.core_d / 2
    annulus = Pos(path.spool[0], path.spool[1], 0) * (
        Cylinder(roll_r - f.thickness, f.width) - Cylinder(core_r, f.width)
    )
    return _strip(c, path) + annulus


def build_cassette(c: Camera) -> Part:
    m, b = c.measured, c.bought
    cx, cy = c.layout.cassette_x, c.layout.cassette_y
    half_h = m.cassette_cap_height / 2
    r = m.cassette_d / 2
    body_h = m.cassette_cap_height - 2 * b.cassette_cap_t

    part = Pos(cx, cy, 0) * Cylinder(r, body_h)
    cap = chamfer(Cylinder(r, b.cassette_cap_t).edges(), b.cassette_cap_chamfer)
    for sign in (-1, 1):
        part += Pos(cx, cy, sign * (half_h - b.cassette_cap_t / 2)) * cap

    top_len = m.spool_top_protrusion
    spool_end = Pos(cx, cy, half_h + top_len / 2) * Cylinder(b.spool_end_d / 2, top_len)
    spool_end -= Pos(cx, cy, half_h + top_len - m.spool_key_depth / 2) * Box(
        b.spool_end_d + OVERSHOOT, m.spool_key_slot, m.spool_key_depth
    )
    part += spool_end
    part += Pos(cx, cy, -half_h - b.spool_stub_len / 2) * Cylinder(b.spool_stub_d / 2, b.spool_stub_len)

    t = c.film.thickness
    tip = cx + m.cassette_lip_envelope / 2
    block_y0 = -(t + b.lip_clearance + b.lip_t)
    block_y1 = b.lip_clearance + b.lip_t
    block_x0 = cx - b.lip_back
    lips = Pos((block_x0 + tip) / 2, (block_y0 + block_y1) / 2, 0) * Box(tip - block_x0, block_y1 - block_y0, body_h)
    slit_y0, slit_y1 = -(t + b.lip_clearance), b.lip_clearance
    lips -= Pos((cx + tip + OVERSHOOT) / 2, (slit_y0 + slit_y1) / 2, 0) * Box(
        tip + OVERSHOOT - cx, slit_y1 - slit_y0, body_h + OVERSHOOT
    )
    return part + lips


PARTS = {
    "cassette": PartSpec(build=build_cassette, place=at_origin, group="film-back", kind="bought", color="#5b7a99"),
    "film": PartSpec(build=build_film, place=at_origin, group="film-back", kind="bought", color="#8a5a2b"),
}
