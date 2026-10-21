"""Sprocket and cam, printed as one part that spins on a fixed 3mm pin.

Built around its own axis (local origin on the axis, Z shared with the camera),
with the first tooth on local +X and the lock notch half a pitch later.
"""
import math

from build123d import Axis, Cylinder, Location, Polygon, Pos, Rot, extrude, fillet, Part

from params import Camera
from parts.spec import PartSpec


def tooth_angles(c: Camera) -> list[float]:
    return [i * 360 / c.sprocket.teeth for i in range(c.sprocket.teeth)]


def notch_angle(c: Camera) -> float:
    """Centred on a tooth gap, so the lock stops the film between perforations."""
    return 180 / c.sprocket.teeth


def rest_rotation(c: Camera) -> float:
    """Rotation that puts the notch under the pawl tip when the sprocket is locked."""
    return c.pawl.angle_deg - notch_angle(c)


def _tooth(c: Camera) -> Part:
    f, hub_r = c.fit, c.sprocket.hub_d / 2
    r_sunk, r_tip = hub_r - c.sprocket.tooth_root_overlap, hub_r + f.tooth_height
    half_root, half_tip = f.tooth_along_root / 2, f.tooth_along_tip / 2
    profile = Polygon(
        (r_sunk, -half_root), (hub_r, -half_root), (r_tip, -half_tip),
        (r_tip, half_tip), (hub_r, half_root), (r_sunk, half_root),
        align=None,
    )
    z0 = -c.film.perf_row_z - f.tooth_across / 2
    tooth = extrude(Pos(0, 0, z0) * profile, amount=f.tooth_across)
    tip_edges = tooth.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
    return fillet(tip_edges, f.tooth_tip_fillet)


def build(c: Camera) -> Part:
    s, f = c.sprocket, c.fit
    hub_r = s.hub_d / 2
    land_half = s.flange_gap / 2
    flange_top = land_half + s.flange_t

    part = Cylinder(hub_r, 2 * land_half)
    part -= Cylinder(hub_r, 2 * s.relief_half_h) - Cylinder(s.relief_d / 2, 2 * s.relief_half_h)
    for sign in (-1, 1):
        part += Pos(0, 0, sign * (land_half + s.flange_t / 2)) * Cylinder(s.flange_d / 2, s.flange_t)

    hub_len = s.top_hub_z1 - flange_top
    part += Pos(0, 0, flange_top + hub_len / 2) * Cylinder(s.top_hub_d / 2, hub_len)
    part += Pos(0, 0, s.cam_z0 + s.cam_t / 2) * Cylinder(s.cam_d / 2, s.cam_t)

    tooth = _tooth(c)
    for a in tooth_angles(c):
        part += Rot(0, 0, a) * tooth

    cam_top = s.cam_z0 + s.cam_t
    pocket = Pos(s.notch_r, 0, cam_top - s.notch_depth / 2) * extrude(
        Polygon((-s.notch_len / 2, -s.notch_w / 2), (s.notch_len / 2, -s.notch_w / 2),
                (s.notch_len / 2, s.notch_w / 2), (-s.notch_len / 2, s.notch_w / 2), align=None),
        amount=s.notch_depth / 2, both=True,
    )
    part -= Rot(0, 0, notch_angle(c)) * pocket

    bore_bottom = -flange_top
    bore_top = s.top_hub_z1 - s.bore_top_wall
    part -= Pos(0, 0, (bore_bottom + bore_top) / 2) * Cylinder(f.shaft_bore / 2, bore_top - bore_bottom)

    a = math.radians(notch_angle(c))
    dot_r = s.top_hub_d / 2 - s.index_dot_inset
    part -= Pos(dot_r * math.cos(a), dot_r * math.sin(a), s.top_hub_z1 - s.index_dot_depth / 2) * Cylinder(
        s.index_dot_d / 2, s.index_dot_depth
    )
    return part


PARTS = {
    "sprocket": PartSpec(
        build=build,
        place=lambda c: Location((c.layout.sprocket_x, c.sprocket_y, 0), (0, 0, rest_rotation(c))),
        group="film-back",
        kind="printed",
        color="#c9a227",
        print_rotation=(0, 0, 0),
    ),
}
