"""Simple 50mm pinhole body, its M42 mount stack, tripod nut and wire-frame viewfinder.

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
- Viewfinder: two fold-flat wire elements share one axle in the two hinge blocks (Y = +42,
  Z = +33). The frame stands over the axle and folds forward. The peep U runs back 80mm, outside
  the dark slide, and folds down onto the film-back top.
"""
from build123d import (
    Align, Box, Cylinder, Face, Part, Plane, Pos, RegularPolygon, Rot, Solid, Sphere, Wire, extrude,
)

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


def rod(points, d: float) -> Part:
    """A bent wire through the given points: cylinders with spherical joints."""
    part = None
    for a, b in zip(points, points[1:]):
        direction = tuple(q - p for p, q in zip(a, b))
        length = sum(x * x for x in direction) ** 0.5
        seg = Solid.make_cylinder(d / 2, length, Plane(origin=a, z_dir=direction))
        part = seg if part is None else part + seg
    for p in points[1:-1]:
        part += Pos(*p) * Sphere(d / 2)
    return part


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


def build_body(c: Camera) -> Part:
    b, k, v, f = c.body, c.body_link, c.viewfinder, c.fit
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

    tw, td = v.tenon_w + f.fdm_clearance, v.tenon_d + f.fdm_clearance
    for sign in (-1, 1):
        body -= box(sign * v.hinge_x - tw / 2, sign * v.hinge_x + tw / 2, v.axle_y - td / 2, v.axle_y + td / 2,
                    b.z_max - b.hinge_pocket_depth, b.z_max + 1)
    return body


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


# Viewfinder.

def peep_centre(c: Camera) -> tuple[float, float, float]:
    v = c.viewfinder
    return 0.0, v.axle_y - v.peep_to_frame, v.axle_z + v.frame_h / 2


def build_hinge(c: Camera, sign: int) -> Part:
    b, v = c.body, c.viewfinder
    x = sign * v.hinge_x
    block = box(x - v.block_w / 2, x + v.block_w / 2, v.axle_y - v.block_d / 2, v.axle_y + v.block_d / 2,
                b.z_max, v.axle_z + v.block_above_axle)
    tenon_h = b.hinge_pocket_depth - c.fit.fdm_clearance
    block += box(x - v.tenon_w / 2, x + v.tenon_w / 2, v.axle_y - v.tenon_d / 2, v.axle_y + v.tenon_d / 2,
                 b.z_max - tenon_h, b.z_max)
    hole = Pos(x - v.block_w, v.axle_y, v.axle_z) * Rot(0, 90, 0) * Cylinder(v.wire_hole / 2, 2 * v.block_w, align=BASE)
    return block - hole


def build_viewfinder_wire(c: Camera) -> Part:
    v = c.viewfinder
    hw, z0, y = v.frame_w / 2, v.axle_z, v.axle_y
    frame = rod([(-hw, y, z0), (hw, y, z0), (hw, y, z0 + v.frame_h), (-hw, y, z0 + v.frame_h), (-hw, y, z0)], v.wire_d)

    ring_r = (v.peep_d + v.wire_d) / 2
    px, py, pz = peep_centre(c)
    bar_z = pz - ring_r + v.wire_d / 4
    slope = (bar_z - z0) / v.peep_to_frame
    xs = v.hinge_x + v.block_w / 2 + v.wire_d
    zb = z0 + (y - v.arm_bend_y) * slope
    peep_u = rod([(-xs, y, z0), (-v.arm_x, v.arm_bend_y, zb), (-v.arm_x, py, bar_z),
                  (v.arm_x, py, bar_z), (v.arm_x, v.arm_bend_y, zb), (xs, y, z0)], v.wire_d)
    ring = Solid.make_torus(ring_r, v.wire_d / 2, Plane(origin=(px, py, pz), z_dir=(0, 1, 0)))
    return frame + peep_u + ring


PARTS = {
    "body": PartSpec(build=build_body, place=at_origin, group="body", kind="printed",
                     color="#2b2b2e", print_rotation=(90, 0, 0)),
    "m42_shim_ring": PartSpec(build=build_shim_ring, place=at_origin, group="body", kind="printed",
                              color="#5a5a60", print_rotation=(90, 0, 0)),
    "viewfinder_hinge_left": PartSpec(build=lambda c: build_hinge(c, -1), place=at_origin, group="body",
                                      kind="printed", color="#44444a", print_rotation=(0, 90, 0)),
    "viewfinder_hinge_right": PartSpec(build=lambda c: build_hinge(c, 1), place=at_origin, group="body",
                                       kind="printed", color="#44444a", print_rotation=(0, 90, 0)),
    "m42_rear_cap_ring": PartSpec(build=build_rear_cap_ring, place=at_origin, group="body", kind="bought",
                                  color="#1a1a1a"),
    "tripod_nut": PartSpec(build=build_tripod_nut, place=at_origin, group="body", kind="bought",
                           color="#b8bcc2"),
    "viewfinder_wire": PartSpec(build=build_viewfinder_wire, place=at_origin, group="body", kind="bought",
                                color="#c0c4c8"),
}
