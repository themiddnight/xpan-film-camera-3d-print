"""M42 pinhole module: a drilled body cap, the brass pinhole shim and a sliding-blade shutter.

Built in camera coordinates (place = identity), screwed into the body, shutter closed and locked.
The cap sits wherever the body's M42 stack puts its seat face, so the pinhole plane is measured,
not assumed.

To open: push the lock lever's thumb pad toward the lens axis (-X) until it clicks, then slide the
knob +X until it stops. To close: slide the knob back until it stops and push the pad back (+X).

Values chosen where docs/design/lens.md left them open:
- Body cap: male thread shown as a 42mm boss 5mm long with 1.5mm walls, drilled 6mm through.
- Shim: 12mm disc, glued on the cap front over the drilled hole; its rear face is the pinhole plane.
- Shutter housing: 28 x 28mm, glued to the cap front. 1.5mm rear plate, 0.8mm blade channel open
  at both X ends, 1.5mm front plate. Openings 4mm round (rear) and 7 x 4mm (front) clear the field.
- Blade: 23mm tall from X = -16 to the housing's +X edge, then an 11mm tongue glued into the knob.
  It slides 10mm toward +X to open, where its 4mm hole moves onto the pinhole. A stadium slot rides
  on the lock pivot pin: its ends are the open and closed stops and keep the blade captive.
- Blade detent: a bump on the channel's rear face as high as the blade's side play, so it touches
  the centred blade, and a dimple hole for each end of the travel. It clicks only when the blade is
  pressed rearward; the lock is what holds the shutter closed.
- Knob: 10 x 14mm, 0.5mm off the housing edge when closed (5.5mm proud of it in X), 4mm ahead of
  the housing front face, ridged. It slides over the body cap's flat front face, 0.3mm clear.
- Lock lever: pivots on the pin 9mm right of and 5.75mm below the pinhole. A 3mm tooth rises 2.5mm
  into a notch in the knob's bottom face; the pivot sits level with the middle of that engagement,
  so pushing the knob loads the tooth straight through the pivot. Turning the lever 25 deg about +Y
  drops the tooth clear. A thumb pad hangs below the housing.
- Lever detent: an arc spring finger on the lever (1.2mm, about 7mm long) whose nose clicks into two
  notches of a printed rail on the housing face, 0.4mm deep. Strain at full flex is about 1.5%.
- Pivot: 9mm of 3mm rod pressed into both housing plates, its rear end on the body cap face; a
  printed cap pressed on its tip keeps the lever on.
"""
import math

from build123d import Face, Part, Pos, Rot, Sphere, Wire, extrude

from params import Camera
from parts.body import box, ring_seat_y, ycyl
from parts.spec import PartSpec, at_origin

ARC_STEPS = 24


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


def housing_front_y(c: Camera) -> float:
    return slot_y(c)[1] + c.pinhole.front_plate


def knob_x0(c: Camera) -> float:
    return c.pinhole.housing_half + c.pinhole.knob_gap


def knob_y(c: Camera) -> tuple[float, float]:
    p = c.pinhole
    return cap_front_y(c) + p.knob_rear_gap, housing_front_y(c) + p.knob_proud


def lever_y(c: Camera) -> tuple[float, float]:
    y0 = housing_front_y(c) + c.pinhole.lock_gap
    return y0, y0 + c.pinhole.lock_t


def pivot_xz(c: Camera) -> tuple[float, float]:
    """Lock pivot: level with the middle of the tooth's engagement in the knob's bottom face."""
    p = c.pinhole
    return p.lock_pivot_x, -p.knob_h / 2 + p.tooth_engage / 2


def lock_axis(c: Camera) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Direction and a point of the lock lever's axis. A positive turn about it unlocks."""
    x, z = pivot_xz(c)
    return (0.0, 1.0, 0.0), (x, lever_y(c)[0], z)


def turn_lock(c: Camera, part: Part, deg: float) -> Part:
    """A part turned about the lock axis, as the unlock mechanism turns the lever."""
    x, z = pivot_xz(c)
    return Pos(x, 0, z) * Rot(0, deg, 0) * Pos(-x, 0, -z) * part


def _polar(c: Camera, r: float, deg: float) -> tuple[float, float]:
    x, z = pivot_xz(c)
    a = math.radians(deg)
    return x + r * math.cos(a), z + r * math.sin(a)


def _xz_prism(points, y0: float, y1: float) -> Part:
    return extrude(Face(Wire.make_polygon([(x, y0, z) for x, z in points], close=True)), y1 - y0, dir=(0, 1, 0))


def _sector(c: Camera, r0: float, r1: float, a0: float, a1: float, y0: float, y1: float) -> Part:
    """Annular sector about the lock pivot, angles in degrees in the X-Z plane."""
    steps = [a0 + (a1 - a0) * i / ARC_STEPS for i in range(ARC_STEPS + 1)]
    outer = [_polar(c, r1, a) for a in steps]
    inner = [_polar(c, r0, a) for a in reversed(steps)]
    return _xz_prism(outer + inner, y0, y1)


def nose_centre(c: Camera) -> tuple[float, float]:
    """Radius and angle of the detent nose centre with the lever locked."""
    p = c.pinhole
    r = p.finger_r + p.finger_t / 2
    return r, p.finger_tip_deg + math.degrees(p.nose_r / r)


def rail_r0(c: Camera) -> float:
    p = c.pinhole
    return nose_centre(c)[0] + p.nose_r - p.detent_depth


def detent_bump_h(c: Camera) -> float:
    """The blade's side play in its channel: the bump touches the centred blade."""
    return (c.pinhole.slot - c.pinhole.blade_t) / 2


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
    y1 = housing_front_y(c)
    h = p.housing_half
    px, pz = pivot_xz(c)
    housing = box(-h, h, f, y1, -h, h)
    channel = p.blade_h / 2 + p.blade_side_gap
    housing -= box(-h - 1, h + 1, s0, s1, -channel, channel)
    housing -= ycyl(p.shim_d / 2 + c.fit.fdm_clearance, f - 1, f + p.shim_recess)
    housing -= ycyl(p.rear_opening_d / 2, f - 1, s0 + 0.01)
    ow, oh = p.front_opening
    housing -= box(-ow / 2, ow / 2, s1 - 0.01, y1 + 1, -oh / 2, oh / 2)
    housing -= ycyl(c.fit.pin_press_hole / 2, f - 1, y1 + 1, x=px, z=pz)

    r_n, a_n = nose_centre(c)
    r0 = rail_r0(c)
    rail = _sector(c, r0, r0 + p.rail_w, a_n - p.lock_unlock_deg - p.rail_overrun_deg, a_n + p.rail_overrun_deg,
                   y1 - 0.01, lever_y(c)[1])
    for a in (a_n, a_n - p.lock_unlock_deg):
        nx, nz = _polar(c, r_n, a)
        rail -= ycyl(p.nose_r + p.notch_play, y1 - 1, y1 + p.lock_t + 2, x=nx, z=nz)
    housing += rail

    bump_h = detent_bump_h(c)
    r_s = ((p.detent_d / 2) ** 2 + bump_h ** 2) / (2 * bump_h)
    bump = Pos(p.detent_x, s0 + bump_h - r_s, p.detent_z) * Sphere(r_s)
    bump &= box(p.detent_x - r_s, p.detent_x + r_s, s0 - 0.01, s0 + bump_h, p.detent_z - r_s, p.detent_z + r_s)
    return housing + bump


def _stadium(r: float, x0: float, x1: float, z: float, y0: float, y1: float) -> Part:
    return box(x0, x1, y0, y1, z - r, z + r) + ycyl(r, y0, y1, x=x0, z=z) + ycyl(r, y0, y1, x=x1, z=z)


def build_blade(c: Camera) -> Part:
    p = c.pinhole
    y0, y1 = blade_y(c)
    x1 = knob_x0(c)
    px, pz = pivot_xz(c)
    blade = box(p.blade_x0, x1, y0, y1, -p.blade_h / 2, p.blade_h / 2)
    blade += box(x1 - 0.01, x1 + p.tongue_len, y0, y1, -p.tongue_h / 2, p.tongue_h / 2)
    blade -= ycyl(p.blade_hole_d / 2, y0 - 1, y1 + 1, x=-p.blade_travel)
    for x in (p.detent_x, p.detent_x - p.blade_travel):
        blade -= ycyl(p.dimple_d / 2, y0 - 1, y1 + 1, x=x, z=p.detent_z)
    r = c.measured.rod_d / 2 + p.stop_clearance
    return blade - _stadium(r, px - p.blade_travel, px, pz, y0 - 1, y1 + 1)


def build_knob(c: Camera) -> Part:
    p = c.pinhole
    x0, (y0, y1) = knob_x0(c), knob_y(c)
    b0, b1 = blade_y(c)
    half = p.knob_h / 2
    knob = box(x0, x0 + p.knob_len, y0, y1, -half, half)
    n = int((p.knob_len - p.ridge_w) // p.ridge_pitch)
    margin = (p.knob_len - p.ridge_w - n * p.ridge_pitch) / 2
    for i in range(n + 1):
        x = x0 + margin + i * p.ridge_pitch
        knob += box(x, x + p.ridge_w, y1 - 0.01, y1 + p.ridge_h, -half, half)
    g = p.glue_gap
    knob -= box(x0 - 1, x0 + p.tongue_len + g, b0 - g, b1 + g, -p.tongue_h / 2 - g, p.tongue_h / 2 + g)
    k, ly0 = p.notch_clearance, lever_y(c)[0]
    return knob - box(p.tooth_x - p.tooth_w / 2 - k, p.tooth_x + p.tooth_w / 2 + k, ly0 - k, y1 + p.ridge_h + 1,
                      -half - 1, -half + p.tooth_engage + k)


def build_lock(c: Camera) -> Part:
    p = c.pinhole
    y0, y1 = lever_y(c)
    px, pz = pivot_xz(c)
    arm_top = -p.knob_h / 2 - p.notch_clearance
    lever = ycyl(p.lock_hub_r, y0, y1, x=px, z=pz)
    lever += box(px, p.tooth_x + p.tooth_w / 2, y0, y1, arm_top - p.lock_arm_w, arm_top)
    lever += box(p.tooth_x - p.tooth_w / 2, p.tooth_x + p.tooth_w / 2, y0, y1,
                 arm_top - 0.01, -p.knob_h / 2 + p.tooth_engage)
    lever += box(px - p.flag_w / 2, px + p.flag_w / 2, y0, y1, pz - p.flag_len, pz)
    pad_z = pz - p.flag_len
    lever += box(px - p.pad_w / 2, px + p.pad_w / 2, y0, y0 + p.pad_depth, pad_z - p.pad_h / 2, pad_z + p.pad_h / 2)
    lever += _sector(c, p.finger_r - p.finger_t / 2, p.finger_r + p.finger_t / 2,
                     p.finger_tip_deg, p.finger_root_deg, y0, y1)
    r_n, a_n = nose_centre(c)
    nx, nz = _polar(c, r_n, a_n)
    lever += ycyl(p.nose_r, y0, y1, x=nx, z=nz)
    return lever - ycyl(c.fit.shaft_bore / 2, y0 - 1, y1 + 1, x=px, z=pz)


def pivot_y(c: Camera) -> tuple[float, float]:
    """The pivot rod's rear end bears on the body cap face."""
    y = cap_front_y(c)
    return y, y + c.pinhole.pivot_len


def lock_cap_y(c: Camera) -> tuple[float, float]:
    y0 = lever_y(c)[1] + c.pinhole.cap_gap
    return y0, y0 + c.pinhole.cap_t


def build_lock_pivot(c: Camera) -> Part:
    px, pz = pivot_xz(c)
    return ycyl(c.measured.rod_d / 2, *pivot_y(c), x=px, z=pz)


def build_lock_cap(c: Camera) -> Part:
    p = c.pinhole
    px, pz = pivot_xz(c)
    y0, y1 = lock_cap_y(c)
    cap = ycyl(p.cap_d / 2, y0, y1, x=px, z=pz)
    return cap - ycyl(c.fit.pin_press_hole / 2, y0 - 1, pivot_y(c)[1] + 0.2, x=px, z=pz)


PARTS = {
    "shutter_housing": PartSpec(build=build_housing, place=at_origin, group="pinhole", kind="printed",
                                color="#303036", print_rotation=(90, 0, 0)),
    "shutter_knob": PartSpec(build=build_knob, place=at_origin, group="pinhole", kind="printed",
                             color="#b04a3a", print_rotation=(0, 0, 0)),
    "shutter_lock": PartSpec(build=build_lock, place=at_origin, group="pinhole", kind="printed",
                             color="#c08a30", print_rotation=(90, 0, 0)),
    "shutter_lock_cap": PartSpec(build=build_lock_cap, place=at_origin, group="pinhole", kind="printed",
                                 color="#44444a", print_rotation=(90, 0, 0)),
    "m42_body_cap": PartSpec(build=build_body_cap, place=at_origin, group="pinhole", kind="bought",
                             color="#151515"),
    "pinhole_shim": PartSpec(build=build_shim, place=at_origin, group="pinhole", kind="bought",
                             color="#c8a050"),
    "shutter_blade": PartSpec(build=build_blade, place=at_origin, group="pinhole", kind="bought",
                              color="#9ea3a8"),
    "shutter_lock_pivot": PartSpec(build=build_lock_pivot, place=at_origin, group="pinhole", kind="bought",
                                   color="#d0d4d8"),
}
