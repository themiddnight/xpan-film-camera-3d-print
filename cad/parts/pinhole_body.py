"""Simple 50mm pinhole body, its M42 mount stack, tripod nut and two-frame sports finder.

Built in camera coordinates (place = identity), at rest: latched on the film back, finder raised.

Values chosen where docs/design/simple-body.md gave a range or left one open:
- Outer form: flat top and bottom (Z = -29 to +26.5) with sides tapering from X = +/-39 at the rear
  to the M42 pocket wall at the front. FDM infill fills the solid between chamber and skin.
- Latch: the doc's "free end at Y = +10, rear face on the pin's front" cannot hold the body, and
  contradicts its own "ramps over the pin". The hook sits behind the pin instead: rear face on the
  datum plane, front face at Y = datum + body_rear_wall, 0.3mm clear of the pin. The cantilever
  root is at Y = +25 (free length 20.8mm, strain about 1.2%), leaving room for the tripod nut.
- Third baffle: the M42 pocket floor (front face Y = +39.0), not a separate rib at +39.
- Baffles run out at 45 deg on their rear side so they print without support, rear face down.
- M42 stack: the shim ring thickness is whatever puts the pinhole at 50.0 for the measured caps
  (1.0mm nominal). Reprint it after measuring.
- Feet: the film back's rear-cover hinge knuckles hang 7.3mm under its bottom, so the body carries the
  camera's whole footprint. The tripod boss (Y = +32) and two rear pads (|X| = 27 to 35, Y from the
  datum to +14) end in one plane, 0.75mm below the lowest knuckle. Three feet stand level on any table,
  and a tripod plate seats on all three and clears the knuckles. The seat Z comes from the cover's hinge
  params, so it follows them.
- The nut sits in the boss, floor 1.2mm over the seat, so a 5mm screw engages 3.8mm of it. The boss is
  16mm across (nut corners 13.2mm plus two 1.2mm walls). The nut slides in from the +X side.
- The boss runs out at 45 deg on its rear side and the rear pads start on the datum face, so the body
  prints rear face down without support. The latch slot is cut through the boss so the cantilever can flex.
- Viewfinder: a front frame and a small rear sight, both printed leaves. You hold the camera against your
  face, so the eye point is the rear cover's outer face (Y -4.73); the front window then frames the
  65 x 24 field from there on its own. The rear sight is optional: raised, its edges line up with the
  front window's only when the eye is centred; folded, it is out of the way. A printed window holds its
  corners to about 0.2mm, which a hand-bent wire rectangle cannot.
- A round peep cannot do the rear sight's job: 20mm from the eye, a small hole shows only a few degrees.
  So it is a 26.17 x 9.66mm window, sized by the same rule as the front one.
- The front frame stands as far forward as its hinge can while the knuckles stay outside the field's
  lower corners and the hinge base fits the tapering body top (axle Y +28). The finder axis sits just
  over the height at which the field's lower edge grazes the M42 body cap rim.
- They fold toward each other. The rear sight folds forward first and must swing under the raised front
  frame (its tip passes about 2mm short of it) yet lie below the field when folded; its axle sits 1.1mm over the
  lowest a hinge base carries to satisfy both. The front frame folds back over it, its knuckles inboard
  of the rear sight's, so neither hinge stands under the other leaf. Unfold the front frame first.
- Each knuckle has two flats 2.9mm from the axis (0.3mm inside its radius, 1.25mm of wall over the bore):
  one under it raised, one under it folded (the rear sight's plate face lies in it). A printed tongue in the hinge base presses
  a pad on the lower flat; turning the leaf pushes the pad 0.3mm down, so each pose clicks in, and the flat on
  the pad sets the raised frame square. The tongue flexes into a 0.6mm recess in the body top.
- Pin stubs (3mm rod, 6mm long) press into the cheeks and turn in the knuckles' 3.3mm bores; two knuckles
  per leaf, outboard of the window, so nothing crosses the field below it.
"""
from dataclasses import dataclass

from build123d import Align, Box, Cylinder, Face, Part, Pos, RegularPolygon, Rot, Solid, Wire, extrude

from params import Camera
from parts.spec import PartSpec, at_origin

MIN = (Align.MIN, Align.MIN, Align.MIN)
BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def ycyl(r, y0, y1, x=0.0, z=0.0) -> Part:
    """Cylinder along +Y from y0 to y1."""
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=BASE)


def zcyl(r, z0, z1, x=0.0, y=0.0) -> Part:
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=BASE)


def rect_wire(y, half_w, half_h) -> Wire:
    return Wire.make_polygon(
        [(-half_w, y, -half_h), (half_w, y, -half_h), (half_w, y, half_h), (-half_w, y, half_h)], close=True
    )


def loft_rects(y0, hw0, hh0, y1, hw1, hh1) -> Solid:
    return Solid.make_loft([rect_wire(y0, hw0, hh0), rect_wire(y1, hw1, hh1)])


def yz_prism(points, x0, x1) -> Part:
    """Extrude a closed (y, z) profile along X."""
    return extrude(Face(Wire.make_polygon([(x0, y, z) for y, z in points], close=True)), x1 - x0, dir=(1, 0, 0))


def cone_half(c: Camera, y: float) -> tuple[float, float]:
    """Half-size of the image cone (65 x 24 frame at Y = 0 to the pinhole) at height y."""
    k = (c.optics.pinhole_y - y) / c.optics.pinhole_y
    return c.film.frame_w / 2 * k, c.film.frame_h / 2 * k


# M42 mount stack along Y: pocket floor, shim ring, rear cap ring, body cap seat, pinhole.

def seat_y(c: Camera) -> float:
    """Design position of the ring's female seat face, where the body cap flange bears."""
    return c.optics.pinhole_y - c.measured.m42_seat_to_pinhole


def shim_t(c: Camera) -> float:
    return max(seat_y(c) - c.measured.m42_rear_cap_h - c.body.m42_floor_y, c.body.m42_shim_min)


def ring_y0(c: Camera) -> float:
    """Rear face of the rear cap ring, resting on the shim ring."""
    return c.body.m42_floor_y + shim_t(c)


def ring_seat_y(c: Camera) -> float:
    """Where the ring's seat face lands once stacked; the body cap flange sits here."""
    return ring_y0(c) + c.measured.m42_rear_cap_h


def pocket_r(c: Camera) -> float:
    return c.measured.m42_rear_cap_od / 2 + c.body.m42_pocket_gap


def seat_z(c: Camera) -> float:
    """Plane of the tripod boss face and the rear pads, below everything else in the camera."""
    return c.cover.hinge_axis_z - c.cover.knuckle_od / 2 - c.body.seat_clear


def nut_z0(c: Camera) -> float:
    return seat_z(c) + c.body.tripod_floor


# Body.

def _baffle(c: Camera, y_front: float, interior: Part) -> tuple[Part, Part]:
    """A rib baffle_t thick at its opening edge, running out at 45 deg toward the rear, and its opening."""
    b = c.body
    y_edge = y_front - b.baffle_t
    hw, hh = cone_half(c, y_edge)
    hw, hh = hw + b.baffle_clearance, hh + b.baffle_clearance
    run = b.chamber_rear_w
    slab = interior & box(-b.rear_half_w, b.rear_half_w, c.gate.datum_y, y_front, b.z_min, b.z_max)
    opening = box(-hw, hw, y_edge - 0.01, y_front + 0.01, -hh, hh)
    return slab - loft_rects(y_edge - run, hw + run, hh + run, y_edge, hw, hh) - opening, opening


def build_pinhole_body(c: Camera) -> Part:
    b, k = c.body, c.body_link
    y0, y1 = c.gate.datum_y, b.front_face_y
    fw = pocket_r(c) + b.wall
    outline = Wire.make_polygon([(-b.rear_half_w, y0, b.z_min), (b.rear_half_w, y0, b.z_min),
                                 (fw, y1, b.z_min), (-fw, y1, b.z_min)], close=True)
    body = extrude(Face(outline), b.z_max - b.z_min, dir=(0, 0, 1))

    body += box(-b.tongue_half_w, b.tongue_half_w, k.tongue_y[0], k.tongue_y[1], b.z_max, k.tongue_top_z)
    seat = seat_z(c)
    r, ty = b.tripod_boss_d / 2, b.tripod_y
    k45 = r / 2 ** 0.5
    body += zcyl(r, seat, b.z_min + 1, y=ty)
    body += extrude(Face(Wire.make_polygon([(0, ty - 2 * k45, seat), (k45, ty - k45, seat), (k45, ty, seat),
                                            (-k45, ty, seat), (-k45, ty - k45, seat)], close=True)),
                    b.z_min + 1 - seat, dir=(0, 0, 1))
    for sign in (-1, 1):
        xa, xb = sorted(sign * x for x in b.foot_x)
        body += box(xa, xb, y0, b.foot_y1, seat, b.z_min + 1)

    floor_edge_y = b.m42_floor_y - b.baffle_t
    interior = loft_rects(y0 - 0.1, b.chamber_rear_w / 2, b.chamber_h / 2,
                          floor_edge_y, b.chamber_front_w / 2, b.chamber_h / 2)
    body -= interior
    for y in (*(yb + b.baffle_t / 2 for yb in b.baffle_y), b.m42_floor_y):
        rib, opening = _baffle(c, y, interior)
        body = body + rib - opening
    body -= ycyl(pocket_r(c), b.m42_floor_y, y1 + 1)

    body -= box(-b.notch_half_w, b.notch_half_w, y0 - 0.1, b.notch_y1, b.z_min - 1, b.notch_top_z)
    beam_top = k.latch_cantilever_top_z
    slot = b.latch_half_w + b.latch_gap
    body -= box(-slot, slot, y0 - 0.1, b.latch_root_y, seat - 1, beam_top + b.latch_gap)
    body += box(-b.latch_half_w, b.latch_half_w, y0, b.latch_root_y + b.latch_gap, b.z_min, beam_top)
    hook_front, hook_top = y0 + k.body_rear_wall, beam_top + k.latch_hook_h
    body += yz_prism([(y0, b.z_min), (hook_front, b.z_min), (hook_front, hook_top),
                      (y0 + b.latch_ramp, hook_top), (y0, beam_top)], -b.latch_half_w, b.latch_half_w)

    z0 = nut_z0(c)
    z1 = z0 + b.nut_t + b.nut_clearance
    af = b.nut_af + b.nut_clearance
    body -= Pos(0, b.tripod_y, z0) * extrude(RegularPolygon(af / 2, 6, major_radius=False), z1 - z0)
    body -= box(0, b.rear_half_w + 1, b.tripod_y - af / 2, b.tripod_y + af / 2, z0, z1)
    body -= zcyl(b.tripod_screw_hole / 2, seat - 1, z1 + b.tripod_screw_depth, y=b.tripod_y)

    return body_finder_mounts(c, body)


def build_shim_ring(c: Camera) -> Part:
    b, y = c.body, c.body.m42_floor_y
    return ycyl(c.measured.m42_rear_cap_od / 2, y, y + shim_t(c)) - ycyl(b.m42_shim_id / 2, y - 1, y + shim_t(c) + 1)


def build_rear_cap_ring(c: Camera) -> Part:
    m, y = c.measured, ring_y0(c)
    lip = y + c.body.m42_ring_lip
    ring = ycyl(m.m42_rear_cap_od / 2, y, y + m.m42_rear_cap_h)
    ring -= ycyl(c.optics.m42_thread_d / 2, lip, y + m.m42_rear_cap_h + 1)
    return ring - ycyl(c.optics.m42_bore / 2, y - 1, lip + 1)


def build_tripod_nut(c: Camera) -> Part:
    b, z0 = c.body, nut_z0(c)
    nut = Pos(0, b.tripod_y, z0) * extrude(RegularPolygon(b.nut_af / 2, 6, major_radius=False), b.nut_t)
    return nut - zcyl(b.nut_bore / 2, z0 - 1, z0 + b.nut_t + 1, y=b.tripod_y)


# Viewfinder: two printed leaves, each on two 3mm pin stubs pressed into a hinge base on the body top.
# They fold toward each other: the rear sight forward first, low; then the front frame back over it.

FOLD_DEG = 90.0
LEAVES = ("rear", "front")  # fold order


@dataclass(frozen=True)
class Leaf:
    which: str
    axle_y: float
    axle_z: float
    w: float
    h: float
    fold: float  # deg about +X that lays the leaf flat: negative folds it forward, positive back


def leaf(c: Camera, which: str) -> Leaf:
    v = c.viewfinder
    if which == "rear":
        return Leaf("rear", v.rear_axle_y, v.rear_axle_z, v.rear_w, v.rear_h, -FOLD_DEG)
    return Leaf("front", v.front_axle_y, v.front_axle_z, v.front_w, v.front_h, FOLD_DEG)


def min_axle_z(c: Camera) -> float:
    """Lowest axle a hinge base can carry: the knuckle over the base plate."""
    v = c.viewfinder
    return c.body.z_max + v.base_t + c.fit.fdm_clearance + v.knuckle_d / 2


def fold_axis(c: Camera, which: str) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Hinge axis direction and a point on it; the leaf's fold about it lays the leaf flat."""
    lf = leaf(c, which)
    return (1.0, 0.0, 0.0), (0.0, lf.axle_y, lf.axle_z)


def _flat(c: Camera) -> float:
    """Axis to each knuckle flat; the leaf's plate face lies in one, so folded it lands on the pad."""
    v = c.viewfinder
    return v.knuckle_d / 2 - v.detent_depth


def knuckle_x(c: Camera, which: str) -> tuple[float, float]:
    v, lf = c.viewfinder, leaf(c, which)
    x_in = lf.w / 2 + (v.rear_knuckle_inset if which == "rear" else v.front_knuckle_inset)
    return x_in, x_in + v.knuckle_len


def cheek_x(c: Camera, which: str) -> tuple[float, float]:
    x0 = knuckle_x(c, which)[1] + c.fit.fdm_clearance
    return x0, x0 + c.viewfinder.cheek_w


def xcyl(r, x0, x1, y=0.0, z=0.0) -> Part:
    """Cylinder along +X from x0 to x1."""
    return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=BASE)


def build_leaf(c: Camera, which: str) -> Part:
    """The window plate stands just in front of the axle, its front face the sighting plane. The knuckle
    keeps two flats: the bottom one, and the one on the side the leaf folds toward, which turns to the
    bottom when folded."""
    v, lf = c.viewfinder, leaf(c, which)
    r, a = v.knuckle_d / 2, _flat(c)
    y, z = lf.axle_y, lf.axle_z
    side = 1 if lf.fold < 0 else -1
    x_in, x_out = knuckle_x(c, which)
    outer = lf.w / 2 + v.bar
    part = box(-outer, outer, y + a - v.leaf_t, y + a, z - a, v.axis_z + lf.h / 2 + v.bar)
    for s in (-1, 1):
        part += box(*sorted((s * lf.w / 2, s * x_out)), y + a - v.leaf_t, y + a, z - a, z + r)
        part += xcyl(r, *sorted((s * x_in, s * x_out)), y=y, z=z)
    span = x_out + 1
    part -= box(-span, span, *sorted((y + side * a, y + side * (r + 1))), z - r - 1, z + r + 1)
    part -= box(-span, span, y - r - 1, y + r + 1, z - r - 1, z - a)
    # The corner between the two flats swings lowest as the leaf folds; keep it inside the knuckle radius.
    part -= box(-span, span, *sorted((y, y + side * r)), z - r, z) - xcyl(r, -span, span, y=y, z=z)
    part -= box(-lf.w / 2, lf.w / 2, y - r - 1, y + r + 1, v.axis_z - lf.h / 2, v.axis_z + lf.h / 2)
    for s in (-1, 1):
        part -= xcyl(c.fit.shaft_bore / 2, *sorted((s * (x_in - 1), s * span)), y=y, z=z)
    return part


def _tongue(c: Camera, lf: Leaf, s: int) -> tuple[float, float]:
    """X span of the detent tongue on one side, root to tip."""
    v = c.viewfinder
    x_in = knuckle_x(c, lf.which)[0]
    tip = cheek_x(c, lf.which)[0] - v.tongue_slot
    return s * (x_in - v.tongue_len), s * tip


def _peg_x(c: Camera, lf: Leaf, s: int) -> float:
    return _tongue(c, lf, s)[0] - s * c.viewfinder.peg_inset


def build_hinge(c: Camera, which: str) -> Part:
    """Base plate with two cheeks holding the pin stubs and a sprung detent tongue under each knuckle."""
    v, lf, f = c.viewfinder, leaf(c, which), c.fit
    y, z0 = lf.axle_y, c.body.z_max
    x0, x1 = cheek_x(c, lf.which)
    y0, y1 = y - v.base_d / 2, y + v.base_d / 2
    part = box(-x1, x1, y0, y1, z0, z0 + v.base_t)
    for s in (-1, 1):
        xa, xb = sorted((s * x0, s * x1))
        part += box(xa, xb, y0, y1, z0, lf.axle_z + f.pin_press_hole / 2 + c.print.min_wall)
        part -= zcyl((v.peg_d + f.fdm_clearance) / 2, z0 - 1, z0 + v.base_t + 1, x=_peg_x(c, lf, s), y=y)
        root, tip = _tongue(c, lf, s)
        half, slot = v.tongue_w / 2, v.tongue_slot
        for side in (-1, 1):
            edge = y + side * half
            part -= box(*sorted((root, tip + s * slot)), *sorted((edge, edge + side * slot)), z0 - 1, z0 + v.base_t + 1)
        part -= box(*sorted((tip, tip + s * slot)), y - half - slot, y + half + slot, z0 - 1, z0 + v.base_t + 1)
        x_in = knuckle_x(c, lf.which)[0]
        part += box(*sorted((s * x_in, tip)), y - half, y + half, z0 + v.base_t, lf.axle_z - _flat(c))
    return part - xcyl(f.pin_press_hole / 2, -x1 - 1, x1 + 1, y=y, z=lf.axle_z)


def build_pin(c: Camera, which: str, side: int) -> Part:
    """One 3mm rod stub (side -1 left, +1 right), pressed into its cheek, the leaf's knuckle turning on it."""
    lf = leaf(c, which)
    x_in, x1 = knuckle_x(c, lf.which)[0] + c.fit.fdm_clearance, cheek_x(c, lf.which)[1]
    xa, xb = sorted((side * x_in, side * x1))
    return xcyl(c.measured.rod_d / 2, xa, xb, y=lf.axle_y, z=lf.axle_z)


def body_finder_mounts(c: Camera, body: Part) -> Part:
    """Locating pegs for both hinge bases, and a relief recess under each detent tongue."""
    v, top = c.viewfinder, c.body.z_max
    for which in LEAVES:
        lf = leaf(c, which)
        for s in (-1, 1):
            body += zcyl(v.peg_d / 2, top - 1, top + v.peg_h, x=_peg_x(c, lf, s), y=lf.axle_y)
            body -= box(*sorted(_tongue(c, lf, s)), lf.axle_y - v.tongue_w / 2, lf.axle_y + v.tongue_w / 2,
                        top - v.tongue_relief, top + 1)
    return body


PARTS = {
    "pinhole_body": PartSpec(build=build_pinhole_body, place=at_origin, group="body", kind="printed",
                     color="#2b2b2e", print_rotation=(90, 0, 0)),
    "m42_shim_ring": PartSpec(build=build_shim_ring, place=at_origin, group="body", kind="printed",
                              color="#5a5a60", print_rotation=(90, 0, 0)),
    "m42_rear_cap_ring": PartSpec(build=build_rear_cap_ring, place=at_origin, group="body", kind="bought",
                                  color="#1a1a1a", bom="2"),
    "tripod_nut": PartSpec(build=build_tripod_nut, place=at_origin, group="body", kind="bought",
                           color="#b8bcc2", bom="8"),
}
for _which in LEAVES:
    PARTS[f"viewfinder_{_which}_frame"] = PartSpec(
        build=lambda c, w=_which: build_leaf(c, w), place=at_origin, group="body", kind="printed",
        color="#3a3a40", print_rotation=(-90, 0, 0))
    PARTS[f"viewfinder_{_which}_hinge"] = PartSpec(
        build=lambda c, w=_which: build_hinge(c, w), place=at_origin, group="body", kind="printed",
        color="#44444a", print_rotation=(0, 0, 0))
    for _side, _side_name in ((-1, "left"), (1, "right")):
        PARTS[f"viewfinder_{_which}_pin_{_side_name}"] = PartSpec(
            build=lambda c, w=_which, s=_side: build_pin(c, w, s), place=at_origin, group="body", kind="stock",
            color="#b8bcc2", bom="1")
