"""Automated design checks. Run from the repository root: uv run python cad/checks.py

Layout checks recompute derived values from params. Geometry checks probe the
built solids, so they catch a part that disagrees with its parameters.
Exit code 1 if any check fails.
"""
import math
from dataclasses import dataclass
from typing import Callable

from build123d import Part, Rot, Vector

from params import CAMERA, Camera
from parts import PARTS, sprocket

EPS = 1e-9


@dataclass
class Result:
    name: str
    ok: bool
    detail: str


class Built:
    """Builds registered parts on first use, so layout-only runs stay fast."""

    def __init__(self, c: Camera):
        self.c = c
        self._local: dict[str, Part] = {}

    def local(self, name: str) -> Part:
        if name not in self._local:
            self._local[name] = PARTS[name].build(self.c)
        return self._local[name]

    def placed(self, name: str) -> Part:
        return PARTS[name].place(self.c) * self.local(name)

    @property
    def sprocket(self) -> Part:
        return self.local("sprocket")


CHECKS: list[tuple[str, Callable[[Camera, Built], tuple[bool, str]]]] = []


def check(name: str):
    def register(fn):
        CHECKS.append((name, fn))
        return fn
    return register


def radial_extent(part: Part, angle_deg: float, z: float, r_lo: float, r_hi: float) -> float:
    """Outer radius of solid material along a ray, by bisection (assumes inside at r_lo)."""
    a = math.radians(angle_deg)
    for _ in range(40):
        mid = (r_lo + r_hi) / 2
        if part.is_inside(Vector(mid * math.cos(a), mid * math.sin(a), z)):
            r_lo = mid
        else:
            r_hi = mid
    return r_lo


def solid_runs(part: Part, r: float, z: float, step_deg: float = 0.25) -> list[float]:
    """Angular widths (deg) of solid runs around a circle of radius r at height z."""
    n = int(360 / step_deg)
    hits = [part.is_inside(Vector(r * math.cos(math.radians(i * step_deg)),
                                  r * math.sin(math.radians(i * step_deg)), z)) for i in range(n)]
    if all(hits):
        return [360.0]
    start = hits.index(False)
    hits = hits[start:] + hits[:start]
    runs, length = [], 0
    for h in hits + [False]:
        if h:
            length += 1
        elif length:
            runs.append(length * step_deg)
            length = 0
    return runs


# Film and sprocket geometry, measured on the built part.

def _land_z(c: Camera) -> float:
    """Height on the lower film land, between the tooth band and the flange."""
    tooth_bottom = -c.film.perf_row_z - c.fit.tooth_across / 2
    return (tooth_bottom - c.sprocket.flange_gap / 2) / 2


@check("sprocket tooth count (geometry)")
def _(c, b):
    r = c.sprocket.hub_d / 2 + c.fit.tooth_height / 2
    runs = solid_runs(b.sprocket, r, -c.film.perf_row_z)
    return len(runs) == c.film.perfs_per_frame, f"{len(runs)} teeth at r={r:.2f}, perforations per frame {c.film.perfs_per_frame}"


@check("film advance per sprocket turn (geometry)")
def _(c, b):
    hub_r = radial_extent(b.sprocket, sprocket.notch_angle(c), _land_z(c), c.sprocket.relief_d / 2, c.sprocket.flange_d / 2 - 0.2)
    advance = math.pi * (2 * hub_r + c.film.thickness)
    return abs(advance - c.film.advance) < 0.05, f"hub r={hub_r:.3f} at Z={_land_z(c):.2f}, neutral-axis circumference {advance:.3f} vs {c.film.advance:.3f}"


@check("tooth root fits perforation along travel (geometry)")
def _(c, b):
    r = c.sprocket.hub_d / 2 + 0.01
    widths = solid_runs(b.sprocket, r, -c.film.perf_row_z, step_deg=0.05)
    chord = 2 * r * math.sin(math.radians(max(widths)) / 2)
    matches = abs(chord - c.fit.tooth_along_root) < 0.06
    return matches and chord <= c.film.perf_along - 0.4, f"root chord {chord:.2f}mm (param {c.fit.tooth_along_root}) in a {c.film.perf_along}mm perforation"


@check("tooth height (geometry)")
def _(c, b):
    hub_r = c.sprocket.hub_d / 2
    tip = radial_extent(b.sprocket, sprocket.tooth_angles(c)[0], -c.film.perf_row_z, hub_r, hub_r + 3)
    return abs(tip - hub_r - c.fit.tooth_height) < 0.02, f"{tip - hub_r:.3f}mm above the hub"


@check("lock notch is a closed pocket of the right depth (geometry)")
def _(c, b):
    s = c.sprocket
    a, top = sprocket.notch_angle(c), s.cam_z0 + s.cam_t
    open_mid = not b.sprocket.is_inside(_polar(s.notch_r, a, top - s.notch_depth + 0.1))
    floor = b.sprocket.is_inside(_polar(s.notch_r, a, top - s.notch_depth - 0.1))
    rim = b.sprocket.is_inside(_polar(s.cam_d / 2 - 0.3, a, top - 0.2))
    rim_wall = s.cam_d / 2 - (s.notch_r + s.notch_len / 2)
    ok = open_mid and floor and rim and rim_wall >= c.print.min_wall - EPS
    return ok, f"open {open_mid}, floor {floor}, rim solid {rim}, rim wall {rim_wall:.2f}mm"


@check("notch under the pawl tip in the assembled pose (geometry)")
def _(c, b):
    s = c.sprocket
    z = s.cam_z0 + s.cam_t - s.notch_depth / 2
    x, y = c.pawl_tip
    placed = b.placed("sprocket")
    under_tip = not placed.is_inside(Vector(x, y, z))
    side_a = math.degrees(math.asin(s.notch_w / 2 / s.notch_r)) + 3
    axis = Vector(c.layout.sprocket_x, c.sprocket_y, z)
    beside = placed.is_inside(axis + _polar(s.notch_r, c.pawl.angle_deg + side_a, 0))
    return under_tip and beside, f"pocket under tip {under_tip}, cam solid {side_a:.0f} deg beside it {beside}"


@check("sprocket part clears the divider wall (geometry)")
def _(c, b):
    radius = b.sprocket.bounding_box().max.X
    gap = c.layout.sprocket_x - radius - (c.shell.bridge_half_span + c.shell.divider_wall)
    return gap >= 1.0 - EPS, f"largest radius {radius:.2f}mm, gap {gap:.2f}mm"


@check("sprocket fits the print bed (geometry)")
def _(c, b):
    size = (Rot(*PARTS["sprocket"].print_rotation) * b.sprocket).bounding_box().size
    return max(size.X, size.Y) <= c.print.bed, f"{size.X:.1f} x {size.Y:.1f}mm footprint"


def _polar(r: float, angle_deg: float, z: float) -> Vector:
    a = math.radians(angle_deg)
    return Vector(r * math.cos(a), r * math.sin(a), z)


# Layout checks from parameters.

@check("hub = pitch diameter - film thickness")
def _(c, b):
    return abs(c.sprocket.hub_d + c.film.thickness - c.pitch_d) < 0.01, f"pitch {c.pitch_d:.3f}, hub {c.sprocket.hub_d}"


@check("tooth fits perforation across")
def _(c, b):
    return c.fit.tooth_across < c.film.perf_across - 0.5, f"{c.film.perf_across - c.fit.tooth_across:.2f}mm total clearance"


@check("rails clear perforations with film float")
def _(c, b):
    g = c.gate
    float_ = (g.fence_gap - c.film.width) / 2
    inner = g.rail_z - g.rail_w / 2
    perf_edge = c.film.width / 2 - c.film.perf_edge
    return inner - (perf_edge + float_) >= 0.3 - EPS, f"rail inner edge {inner:.2f}, perforation edge {perf_edge:.2f} + float {float_:.2f}"


@check("rails stay on the film")
def _(c, b):
    g = c.gate
    float_ = (g.fence_gap - c.film.width) / 2
    return g.rail_z + g.rail_w / 2 < c.film.width / 2 - float_, f"rail outer edge {g.rail_z + g.rail_w / 2:.2f}"


@check("front wall over dark slide slot")
def _(c, b):
    g = c.gate
    wall = g.front_wall - g.velvet_groove_depth
    return wall >= c.print.min_wall - EPS, f"{wall:.2f}mm"


@check("cover groove walls")
def _(c, b):
    s = c.shell
    wall = (s.rear_rim - s.cover_groove_w) / 2
    return wall >= c.print.min_wall - EPS, f"{wall:.2f}mm each side"


@check("centre relief keeps the image area off the hub")
def _(c, b):
    s = c.sprocket
    covers = s.relief_half_h >= c.film.frame_h / 2 + 0.2
    clear_of_teeth = s.relief_half_h <= c.film.perf_row_z - c.fit.tooth_across / 2 - 0.5
    return covers and clear_of_teeth and s.relief_d < s.hub_d - 1.0, f"relief Z +/-{s.relief_half_h}, image +/-{c.film.frame_h / 2}, diameter {s.relief_d}"


@check("sprocket flanges pass the film")
def _(c, b):
    gap = c.sprocket.flange_gap - c.film.width
    return 0.2 <= gap <= 0.8, f"{gap:.2f}mm total side clearance"


@check("shaft bore clearance")
def _(c, b):
    gap = c.fit.shaft_bore - c.measured.rod_d
    return 0.15 <= gap <= 0.5, f"{gap:.2f}mm on a {c.measured.rod_d}mm pin"


def _spool_distance(c):
    return math.hypot(c.layout.spool_x - c.layout.sprocket_x, c.layout.spool_y - c.sprocket_y)


@check("wound roll clears sprocket flange")
def _(c, b):
    gap = _spool_distance(c) - c.sprocket.flange_d / 2 - c.takeup.roll_d_max / 2
    return gap >= 2.0, f"{gap:.2f}mm"


@check("take-up flange clears sprocket flange")
def _(c, b):
    gap = _spool_distance(c) - c.sprocket.flange_d / 2 - c.takeup.flange_d / 2
    return gap >= 1.0, f"{gap:.2f}mm"


def wrap_deg(c: Camera, spool_r: float) -> float:
    """Film arrives along +X at the hub bottom and leaves on the internal tangent to the spool."""
    d = _spool_distance(c)
    centre = math.degrees(math.atan2(c.layout.spool_y - c.sprocket_y, c.layout.spool_x - c.layout.sprocket_x))
    return centre + math.degrees(math.asin((c.pitch_d / 2 + spool_r) / d))


@check("sprocket wrap engages >= 1.8 teeth")
def _(c, b):
    w0, w1 = wrap_deg(c, c.takeup.core_d / 2), wrap_deg(c, c.takeup.roll_d_max / 2)
    t = c.sprocket.teeth / 360
    return w0 * t >= 1.8, f"{w0:.1f}-{w1:.1f} deg, {w0 * t:.1f}-{w1 * t:.1f} teeth"


@check("cover shoe stays inside the contact arc")
def _(c, b):
    leave = -90 + wrap_deg(c, c.takeup.core_d / 2)
    return leave >= c.shell.shoe_end_deg, f"film leaves at {leave:.1f} deg, shoe ends at {c.shell.shoe_end_deg} deg"


@check("shell fits the print bed")
def _(c, b):
    w = c.shell.x_max - c.shell.x_min
    return w <= c.print.bed, f"{w:.1f}mm"


def _spool_tip(c):
    return c.measured.cassette_cap_height / 2 + c.measured.spool_top_protrusion


@check("cassette spool tip clears the ceiling")
def _(c, b):
    gap = c.shell.ceiling_z - _spool_tip(c)
    return gap >= 1.0, f"{gap:.1f}mm"


@check("rewind fork lifts inside the tower")
def _(c, b):
    r = c.rewind
    left = r.tower_top_inside - (r.fork_top_engaged + r.lift)
    return left >= 0.5, f"{left:.1f}mm left at full lift"


@check("lifted fork clears the spool tip")
def _(c, b):
    r = c.rewind
    return r.fork_bottom + r.lift - _spool_tip(c) >= 1.0, f"fork bottom {r.fork_bottom + r.lift:.1f} over tip {_spool_tip(c)}"


@check("rear opening passes the cassette spool tip")
def _(c, b):
    return c.rewind.rear_opening_top - _spool_tip(c) >= 1.0, f"opening top {c.rewind.rear_opening_top}, tip {_spool_tip(c)}"


@check("lifted pawl clears the ceiling")
def _(c, b):
    gap = c.shell.ceiling_z - c.pawl_lifted_top_z
    return gap >= 0.5, f"lever top {c.pawl_lifted_top_z:.1f} lifted, {gap:.1f}mm under the ceiling"


@check("release button clears the advance knob")
def _(c, b):
    bx, by = c.pawl_button
    gap = math.hypot(bx - c.layout.spool_x, by - c.layout.spool_y) - c.pawl.button_d / 2 - c.takeup.knob_d / 2
    return gap >= 1.0, f"{gap:.1f}mm edge to edge"


@check("release button inside the chamber front wall")
def _(c, b):
    edge = c.pawl_button[1] + c.pawl.button_d / 2
    inner_front = c.shell.y_front - c.shell.outer_wall
    return edge <= inner_front, f"button edge Y {edge:.1f}, wall at {inner_front}"


@check("button lifts pawl clear of the notch")
def _(c, b):
    margin = c.pawl_tip_lift - c.sprocket.notch_depth
    ratio = c.pawl.tip_arm / c.pawl.button_arm
    return margin >= 0.5, f"tip lifts {c.pawl_tip_lift:.2f}mm (lever ratio {ratio:.2f}), {margin:.2f}mm over the notch"


@check("clutch spring slides over the shaft")
def _(c, b):
    t = c.takeup
    inside = t.clutch_spring_od - 2 * t.clutch_spring_wire
    return inside > c.measured.rod_d + 0.2, f"spring inside {inside:.1f}mm on a {c.measured.rod_d}mm shaft"


@check("body tongue clearance in hook slot")
def _(c, b):
    k = c.body_link
    gaps = (k.tongue_y[0] - k.hook_slot_y[0], k.hook_slot_y[1] - k.tongue_y[1], k.hook_slot_top_z - k.tongue_top_z)
    return min(gaps) >= c.fit.fdm_clearance - EPS, "Y {:.1f}/{:.1f}, Z {:.1f}mm".format(*gaps)


@check("hook slot starts at the body datum")
def _(c, b):
    return abs(c.body_link.hook_slot_y[0] - c.gate.datum_y) < 1e-6, f"slot Y {c.body_link.hook_slot_y[0]}, datum {c.gate.datum_y:.2f}"


@check("latch pin sits in front of the body rear wall")
def _(c, b):
    k = c.body_link
    gap = k.latch_pin_y - c.measured.rod_d / 2 - (c.gate.datum_y + k.body_rear_wall)
    return gap >= 0.3 - EPS, f"{gap:.1f}mm"


@check("latch hook rises past the pin centre")
def _(c, b):
    k = c.body_link
    top = k.latch_cantilever_top_z + k.latch_hook_h
    return top >= k.latch_pin_z + 0.2, f"hook top {top:.1f}, pin centre {k.latch_pin_z:.1f}"


@check("front aperture clears image cone at datum")
def _(c, b):
    o, g, f = c.optics, c.gate, c.film
    k = (o.pinhole_y - g.datum_y) / o.pinhole_y
    return g.aperture_w > f.frame_w * k and g.aperture_h > f.frame_h * k, f"cone {f.frame_w * k:.1f} x {f.frame_h * k:.1f} in {g.aperture_w} x {g.aperture_h}"


def corner_angle(c: Camera) -> float:
    return math.degrees(math.atan(math.hypot(c.film.frame_w, c.film.frame_h) / 2 / c.optics.pinhole_y))


@check("M42 bore clears corner rays")
def _(c, b):
    o = c.optics
    r = o.m42_depth_behind_pinhole * math.tan(math.radians(corner_angle(c)))
    return r < o.m42_bore / 2, f"cone radius {r:.1f}mm, bore radius {o.m42_bore / 2}"


@check("pinhole near the Rayleigh optimum")
def _(c, b):
    o = c.optics
    best = 1.9 * math.sqrt(o.pinhole_y * o.wavelength)
    return abs(o.pinhole_d - best) / best < 0.1, f"optimum {best:.3f}mm, f/{o.pinhole_y / o.pinhole_d:.0f}"


def run_checks(c: Camera = CAMERA) -> list[Result]:
    built = Built(c)
    return [Result(name, *fn(c, built)) for name, fn in CHECKS]


def main() -> int:
    results = run_checks()
    for r in results:
        print(f"{'PASS' if r.ok else 'FAIL'}  {r.name}: {r.detail}")
    failed = [r.name for r in results if not r.ok]
    print(f"INFO  corner ray angle: {corner_angle(CAMERA):.1f} deg, "
          f"cos^4 falloff {math.log2(math.cos(math.radians(corner_angle(CAMERA))) ** -4):.2f} stops")
    print(f"INFO  frames per 36-exp roll: {36 * 38.0 / CAMERA.film.advance:.1f} before loading waste")
    print()
    print("ALL PASS" if not failed else f"{len(failed)} FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
