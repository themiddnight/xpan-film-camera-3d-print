"""Geometry checks for the pinhole module's shutter: blade, push tabs, lock lever and its pivot."""
import math

from build123d import Part, Pos, Vector

from check_areas.pinhole_body import CONE_MARGIN, _apex_y, _field_cone, _first_run, _hit, _runs
from checklib import EPS, check
from parts import PARTS
from parts import pinhole as ph

TOL = 0.01
"""Shared volume (mm3) below this is a touching face or tessellation noise."""
SWEEP_STEPS = 6
TAB_PROUD_MIN = 10.0
"""How far the tab to push next must stand past its housing edge for a thumb to find and push it (mm)."""
TAB_FLUSH_MAX = 5.0
"""How far the other tab may stand out, so the two ends of the travel read apart by feel (mm)."""
TAB_FACE_MIN = 6.0
"""Least height and depth of a tab's push face (mm)."""
PAD_ABOVE_MIN = 3.0
"""How far the lock's thumb pad must rise above the housing top, so the lock is worked from the top (mm)."""
STOP_OVERRUN = 0.3
"""The stops must hold the blade within this of its nominal closed and open positions (mm)."""
LOCK_PUSH = 1.0
"""Push on the open tab that the engaged lock must stop (mm)."""
DETENT_CLICK_MIN = 0.1
DETENT_CLICK_MAX = 3.0
"""Nose-into-rail volume (mm3) between the notches: enough to click, small enough to be only the nose."""
FINGER_STRAIN_MAX = 0.02
BORE_SPIN_MIN = 0.2
BORE_PRESS = (0.05, 0.2)
"""Diametral interference for a pressed pin, least and most (mm)."""
CAP_GRIP_MIN = 1.5
PLATE_GRIP_MIN = 2.5

MOVING = ph.SLIDING


def _offsets(c) -> list[float]:
    return [c.pinhole.blade_travel * i / (SWEEP_STEPS - 1) for i in range(SWEEP_STEPS)]


def _slid(b, name: str, dx: float) -> Part:
    return Pos(dx, 0, 0) * b.placed(name)


def _lever(c, b, deg: float) -> Part:
    return ph.turn_lock(c, b.placed("shutter_lock"), deg)


def _boxes_meet(a, o) -> bool:
    return all(getattr(a.min, k) <= getattr(o.max, k) and getattr(o.min, k) <= getattr(a.max, k) for k in "XYZ")


@check("shutter closed: blade covers the pinhole and the lock holds it (geometry)")
def _(c, b):
    p, blade = c.pinhole, b.placed("shutter_blade")
    mid = (blade.bounding_box().min.Y + blade.bounding_box().max.Y) / 2
    r = p.rear_opening_d / 2
    covers = all(blade.is_inside(Vector(x, mid, z)) for x, z in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)))
    lever = b.placed("shutter_lock")
    rest = sum(_hit(lever, b.placed(n)) for n in MOVING)
    pushed = _hit(lever, _slid(b, "shutter_blade", LOCK_PUSH))
    ok = covers and rest < TOL and pushed > TOL
    return ok, (f"covers {covers}, lock at rest {rest:.3f} mm3, open tab pushed {LOCK_PUSH}mm: "
                f"the tongue meets the tooth {pushed:.2f} mm3")


@check("shutter lock engages only with the shutter closed (geometry)")
def _(c, b):
    t = c.pinhole.blade_travel
    lever = b.placed("shutter_lock")
    blocked = sum(_hit(lever, _slid(b, n, t)) for n in MOVING)
    return blocked > TOL, f"lever turned back with the shutter open meets the blade and open tab {blocked:.2f} mm3"


@check("lever turns clear of the housing apart from its detent, and unlocked clears the blade and tabs (geometry)")
def _(c, b):
    p = c.pinhole
    housing = b.placed("shutter_housing")
    worst = []
    for i in range(SWEEP_STEPS):
        deg = p.lock_unlock_deg * i / (SWEEP_STEPS - 1)
        lever = _lever(c, b, deg)
        body = lever - ph.turn_lock(c, ph.detent_zone(c), deg)
        worst.append((sum(_hit(lever, b.placed(n)) for n in MOVING) + _hit(body, housing), f"turning {deg:.0f} deg"))
    lever = _lever(c, b, p.lock_unlock_deg)
    for dx in _offsets(c):
        worst.append((sum(_hit(lever, _slid(b, n, dx)) for n in MOVING), f"blade at {dx:.1f}mm"))
    v, where = max(worst)
    return v < TOL, f"worst {v:.3f} mm3 ({where})"


@check("shutter lock sits on top: thumb pad above the housing, nothing below it (geometry)")
def _(c, b):
    lever, housing = b.placed("shutter_lock").bounding_box(), b.placed("shutter_housing").bounding_box()
    above, low = lever.max.Z - housing.max.Z, lever.min.Z - housing.min.Z
    ok = above >= PAD_ABOVE_MIN - EPS and low >= 0
    return ok, f"pad top {above:.1f}mm above the housing top, lever bottom {low:.1f}mm above the housing bottom"


@check("lock lever clicks into its detent locked and unlocked (geometry)")
def _(c, b):
    p, housing = c.pinhole, b.placed("shutter_housing")
    u, over = p.lock_unlock_deg, p.rail_overrun_deg / 2

    def hit(deg):
        return _hit(_lever(c, b, deg), housing)

    seated = max(hit(0.0), hit(u))
    climbs = [hit(-over), hit(u / 2), hit(u + over)]
    length = p.finger_r * math.radians(p.finger_root_deg - p.finger_tip_deg)
    strain = 1.5 * p.finger_t * p.detent_depth / length ** 2
    ok = seated < TOL and min(climbs) > DETENT_CLICK_MIN and max(climbs) < DETENT_CLICK_MAX and strain <= FINGER_STRAIN_MAX
    return ok, (f"seated {seated:.3f} mm3, nose into rail past lock/mid/past unlock "
                f"{'/'.join(f'{v:.2f}' for v in climbs)} mm3, finger strain {strain:.1%}")


@check("blade slides with zero overlap and its detent bump meets a dimple closed and open (geometry)")
def _(c, b):
    p, housing = c.pinhole, b.placed("shutter_housing")
    worst = max(_hit(_slid(b, "shutter_blade", dx), housing) for dx in _offsets(c))
    y0 = ph.blade_y(c)[0]
    touches = housing.is_inside(Vector(p.detent_x, y0 - 0.02, p.detent_z))
    r = p.detent_d / 2
    rim = [(p.detent_x + dx, p.detent_z + dz) for dx, dz in ((r, 0), (-r, 0), (0, r), (0, -r), (0, 0))]
    mid = y0 + p.blade_t / 2
    seats = all(not _slid(b, "shutter_blade", dx).is_inside(Vector(x, mid, z))
                for dx in (0.0, p.blade_travel) for x, z in rim)
    ok = worst < TOL and touches and seats
    return ok, f"worst blade-housing overlap {worst:.3f} mm3, bump touches blade {touches}, sits in a dimple at both ends {seats}"


@check("open shutter, lock and pivot clear the field of view (geometry)")
def _(c, b):
    p = c.pinhole
    cone = _field_cone(c, _apex_y(b), CONE_MARGIN)
    parts = {n: b.placed(n) for n in ("shutter_housing", "shutter_lock_pivot", "shutter_lock_cap", "shutter_lock")}
    parts["shutter_lock unlocked"] = _lever(c, b, p.lock_unlock_deg)
    parts |= {f"{n} open": _slid(b, n, p.blade_travel) for n in MOVING}
    bad = {n: round(v, 3) for n, part in parts.items() if (v := _hit(cone, part)) > EPS}
    return not bad, f"hits {bad}" if bad else f"clear, rays grown {CONE_MARGIN}mm"


@check("shutter tabs: the one to push next stands proud, the other near flush, travel hits nothing (geometry)")
def _(c, b):
    t = c.pinhole.blade_travel
    h = b.placed("shutter_housing").bounding_box()
    o, k = b.placed("shutter_open_tab").bounding_box(), b.placed("shutter_close_tab").bounding_box()
    # (open tab, close tab) past their own housing edges, and the near-flush tab's gap to its edge.
    closed = (h.min.X - o.min.X, k.max.X - h.max.X)
    opened = (h.min.X - (o.min.X + t), k.max.X + t - h.max.X)
    gaps = (k.min.X - h.max.X, h.min.X - (o.max.X + t))
    face = min(o.size.Y, o.size.Z, k.size.Y, k.size.Z)
    lever = _lever(c, b, c.pinhole.lock_unlock_deg)
    hits = {}
    for dx in _offsets(c):
        for moving in MOVING:
            part = _slid(b, moving, dx)
            box = part.bounding_box()
            for name in PARTS:
                if name in MOVING or (moving, name) == ("shutter_blade", "shutter_housing"):
                    continue
                other = lever if name == "shutter_lock" else b.placed(name)
                if _boxes_meet(box, other.bounding_box()) and (v := _hit(part, other)) > TOL:
                    hits[f"{moving}@{dx:.0f} x {name}"] = round(v, 3)
    ok = (min(closed[0], opened[1]) >= TAB_PROUD_MIN - EPS and max(closed[1], opened[0]) <= TAB_FLUSH_MAX + EPS
          and min(gaps) >= STOP_OVERRUN - EPS and face >= TAB_FACE_MIN - EPS and not hits)
    return ok, (f"closed: open tab {closed[0]:.1f}, close tab {closed[1]:.1f}mm out; open: open tab {opened[0]:.1f}, "
                f"close tab {opened[1]:.1f}mm out; flush tab {min(gaps):.2f}mm off the housing; push face "
                f">= {face:.1f}mm; sweep hits {hits or 'none'}")


@check("blade stops at closed and at blade_travel (geometry)")
def _(c, b):
    t, pin = c.pinhole.blade_travel, b.placed("shutter_lock_pivot")
    free = max(_hit(_slid(b, "shutter_blade", dx), pin) for dx in _offsets(c))
    closed = _hit(_slid(b, "shutter_blade", -STOP_OVERRUN), pin)
    opened = _hit(_slid(b, "shutter_blade", t + STOP_OVERRUN), pin)
    ok = free < TOL and closed > TOL and opened > TOL
    return ok, f"free over {t}mm ({free:.3f} mm3); {STOP_OVERRUN}mm past closed {closed:.2f}, past open {opened:.2f} mm3"


def _hole_d(part: Part, x: float, y: float, z: float, span: float = 10.0) -> float:
    """Width of the gap in the part along X that contains x."""
    runs = _runs(part, (x - span, y, z), (1, 0, 0), 2 * span)
    left = max((r[1] for r in runs if r[1] <= span), default=0.0)
    right = min((r[0] for r in runs if r[0] >= span), default=2 * span)
    return right - left


@check("lock pivot pressed in the housing and cap, free in the lever (geometry)")
def _(c, b):
    rod = c.measured.rod_d
    x, z = ph.pivot_xz(c)
    f = ph.cap_front_y(c)
    lever_mid = sum(ph.lever_y(c)) / 2
    cap_y = ph.lock_cap_y(c)
    rear = _hole_d(b.placed("shutter_housing"), x, f + c.pinhole.rear_plate / 2, z)
    lever = _hole_d(b.placed("shutter_lock"), x, lever_mid, z)
    cap = _hole_d(b.placed("shutter_lock_cap"), x, cap_y[0] + 0.3, z)
    pin = b.placed("shutter_lock_pivot").bounding_box()
    plate_grip = c.pinhole.rear_plate + c.pinhole.front_plate
    cap_grip = pin.max.Y - cap_y[0]
    pressed = all(BORE_PRESS[0] - EPS <= rod - d <= BORE_PRESS[1] + EPS for d in (rear, cap))
    ok = (pressed and lever - rod >= BORE_SPIN_MIN - EPS and cap_grip >= CAP_GRIP_MIN - EPS
          and plate_grip >= PLATE_GRIP_MIN - EPS and abs(pin.min.Y - f) < TOL)
    return ok, (f"housing bore {rear:.2f}, cap bore {cap:.2f}, lever bore {lever:.2f} on a {rod}mm pin; "
                f"grip {plate_grip:.1f}mm in the plates, {cap_grip:.1f}mm in the cap")


def _tab_rays(c, tab: ph.Tab) -> list[tuple[str, str, tuple, tuple]]:
    x_in, x_out = ph.tab_x(c, tab)
    out = 1.0 if x_out > x_in else -1.0
    b0, b1 = ph.blade_y(c)
    mid = (b0 + b1) / 2
    inside = (x_in + out * 0.5, mid, 0)
    name = f"shutter_{tab}_tab"
    return [
        (name, "behind the blade slit", inside, (0, -1, 0)),
        (name, "over the blade slit", inside, (0, 0, 1)),
        (name, "slit bottom to the push face", inside, (out, 0, 0)),
    ]


def _wall_rays(c) -> list[tuple[str, str, tuple, tuple]]:
    p = c.pinhole
    s0, s1 = ph.slot_y(c)
    b0, b1 = ph.blade_y(c)
    x, z = ph.pivot_xz(c)
    lever_mid = sum(ph.lever_y(c)) / 2
    r_n, a_n = ph.nose_centre(c)
    a = math.radians(a_n)
    notch = (x + (r_n - 0.1) * math.cos(a), lever_mid, z + (r_n - 0.1) * math.sin(a))
    tooth_mid = ph.tongue_top(c) - p.tooth_engage + p.tooth_h / 2
    return [
        ("shutter_housing", "blade rail", (0, (s0 + s1) / 2, 0), (0, 0, 1)),
        ("shutter_housing", "rear plate", (p.housing_half - 2, (s0 + s1) / 2, 0), (0, -1, 0)),
        ("shutter_housing", "front plate", (p.housing_half - 2, (s0 + s1) / 2, 0), (0, 1, 0)),
        ("shutter_housing", "pivot bore to the top edge", (x, (s1 + ph.housing_front_y(c)) / 2, z), (0, 0, 1)),
        ("shutter_housing", "detent rail under the locked notch", notch, (math.cos(a), 0, math.sin(a))),
        *_tab_rays(c, "open"),
        *_tab_rays(c, "close"),
        ("shutter_lock", "hub", (x, lever_mid, z), (0, 0, 1)),
        ("shutter_lock", "tooth", (p.tooth_x - p.tooth_w, (b0 + b1) / 2, tooth_mid), (1, 0, 0)),
        ("shutter_lock_cap", "cap", (x, ph.lock_cap_y(c)[0] + 0.3, z), (0, 0, 1)),
    ]


@check("shutter walls >= min wall (geometry)")
def _(c, b):
    thin = []
    rays = _wall_rays(c)
    for part, label, start, d in rays:
        run = _first_run(b.placed(part), start, d)
        t = run[1] - run[0] if run else 0.0
        if t < c.print.min_wall - EPS:
            thin.append(f"{label} {t:.2f}")
    return not thin, f"thin: {thin}" if thin else f"all {len(rays)} probed walls >= {c.print.min_wall}mm"
