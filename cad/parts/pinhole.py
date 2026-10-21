"""M42 pinhole module: a drilled body cap, the brass pinhole shim and a sliding-blade shutter.

Built in camera coordinates (place = identity), screwed into the body, shutter closed and locked.
The cap sits wherever the body's M42 stack puts its seat face, so the pinhole plane is measured,
not assumed.

Values chosen where docs/design/lens.md left them open:
- Body cap: male thread shown as a 42mm boss 5mm long with 1.5mm walls, drilled 6mm through.
- Shim: 12mm disc, glued on the cap front over the drilled hole; its rear face is the pinhole plane.
- Shutter housing: 28 x 28mm, glued to the cap front. 1.5mm rear plate, 0.8mm blade channel open
  at both X ends, 1.5mm front plate. Openings 4mm round (rear) and 7 x 4mm (front) clear the field.
- Blade: 32 x 23mm, slides 10mm toward +X to open, where a 4mm hole moves onto the pinhole.
  A 0.25mm printed bump drops into a 1.5mm hole in the blade when closed.
- Lock pin: 3mm x 20mm along Y, 8mm below the pinhole (outside the 27 deg vertical field),
  through a 7mm boss, the blade and the rear plate to the cap face. It only enters when closed.
"""
from build123d import Part, Pos, Sphere

from params import Camera
from parts.body import box, ring_seat_y, ycyl
from parts.spec import PartSpec, at_origin


def cap_front_y(c: Camera) -> float:
    """The pinhole plane: body cap front face, where the shim is glued."""
    return ring_seat_y(c) + c.measured.m42_seat_to_pinhole


def slot_y(c: Camera) -> tuple[float, float]:
    y = cap_front_y(c) + c.pinhole.rear_plate
    return y, y + c.pinhole.slot


def blade_y(c: Camera) -> tuple[float, float]:
    y0, y1 = slot_y(c)
    mid = (y0 + y1) / 2
    return mid - c.pinhole.blade_t / 2, mid + c.pinhole.blade_t / 2


def build_body_cap(c: Camera) -> Part:
    p, seat, front = c.pinhole, ring_seat_y(c), cap_front_y(c)
    thread_r = c.optics.m42_thread_d / 2
    cap = ycyl(c.measured.m42_body_cap_od / 2, seat, front)
    cap += ycyl(thread_r, seat - p.cap_boss_len, seat)
    cap -= ycyl(thread_r - p.cap_boss_wall, seat - p.cap_boss_len - 1, seat)
    return cap - ycyl(p.cap_drill_d / 2, seat - 1, front + 1)


def build_shim(c: Camera) -> Part:
    p, y = c.pinhole, cap_front_y(c)
    return ycyl(p.shim_d / 2, y, y + p.shim_t) - ycyl(c.optics.pinhole_d / 2, y - 1, y + 1)


def build_housing(c: Camera) -> Part:
    p, f = c.pinhole, cap_front_y(c)
    s0, s1 = slot_y(c)
    y1 = s1 + p.front_plate
    h = p.housing_half
    housing = box(-h, h, f, y1, -h, h)
    housing += ycyl(p.pin_boss_d / 2, f, f + p.pin_boss_len, z=p.pin_z)
    channel = p.blade_h / 2 + p.blade_side_gap
    housing -= box(-h - 1, h + 1, s0, s1, -channel, channel)
    housing -= ycyl(p.shim_d / 2 + c.fit.fdm_clearance, f - 1, f + p.shim_recess)
    housing -= ycyl(p.rear_opening_d / 2, f - 1, s0 + 0.01)
    ow, oh = p.front_opening
    housing -= box(-ow / 2, ow / 2, s1 - 0.01, y1 + 1, -oh / 2, oh / 2)
    housing -= ycyl(c.fit.shaft_bore / 2, f - 1, f + p.pin_boss_len + 1, z=p.pin_z)

    r_s = ((p.detent_d / 2) ** 2 + p.detent_h ** 2) / (2 * p.detent_h)
    bump = Pos(p.detent_x, s0 + p.detent_h - r_s, p.detent_z) * Sphere(r_s)
    bump &= box(p.detent_x - r_s, p.detent_x + r_s, s0 - 0.01, s0 + p.detent_h, p.detent_z - r_s, p.detent_z + r_s)
    return housing + bump


def build_blade(c: Camera) -> Part:
    p = c.pinhole
    y0, y1 = blade_y(c)
    blade = box(-p.blade_len / 2, p.blade_len / 2, y0, y1, -p.blade_h / 2, p.blade_h / 2)
    for d, x, z in ((p.blade_hole_d, -p.blade_travel, 0.0), (p.blade_pin_hole, 0.0, p.pin_z),
                    (p.dimple_d, p.detent_x, p.detent_z)):
        blade -= ycyl(d / 2, y0 - 1, y1 + 1, x=x, z=z)
    return blade


def build_lock_pin(c: Camera) -> Part:
    p, f = c.pinhole, cap_front_y(c)
    return ycyl(c.measured.rod_d / 2, f, f + p.pin_len, z=p.pin_z)


PARTS = {
    "shutter_housing": PartSpec(build=build_housing, place=at_origin, group="pinhole", kind="printed",
                                color="#303036", print_rotation=(90, 0, 0)),
    "m42_body_cap": PartSpec(build=build_body_cap, place=at_origin, group="pinhole", kind="bought",
                             color="#151515"),
    "pinhole_shim": PartSpec(build=build_shim, place=at_origin, group="pinhole", kind="bought",
                             color="#c8a050"),
    "shutter_blade": PartSpec(build=build_blade, place=at_origin, group="pinhole", kind="bought",
                              color="#9ea3a8"),
    "shutter_lock_pin": PartSpec(build=build_lock_pin, place=at_origin, group="pinhole", kind="bought",
                                 color="#d0d4d8"),
}
