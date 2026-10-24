"""Pins for the presentation page: named spots on named parts, with anchors computed from params.

An anchor is a point in camera coordinates at the part's rest pose, on the visible surface a reader
would point at. The viewer attaches each pin to its part's node, so pins follow the mechanisms.
cad/check_areas/presentation.py proves every anchor lies on its part's surface.
"""
import math
from dataclasses import dataclass
from typing import Callable

from build123d import Pos

from params import Camera
from parts import PARTS, pinhole as ph, pinhole_body as pb, shell, sprocket, transport

Point = tuple[float, float, float]


@dataclass(frozen=True)
class Feature:
    id: str
    label: str
    part: str
    point: Callable[[Camera], Point]


def _local(c: Camera, part: str, x: float, y: float, z: float) -> Point:
    """A point given in the part's own build frame, carried to camera coordinates by its placement."""
    p = (PARTS[part].place(c) * Pos(x, y, z)).position
    return p.X, p.Y, p.Z


def _front_tooth(c: Camera) -> float:
    """Local angle of the tooth that rests nearest the front (+Y), away from the film wrapped on the rear."""
    rest = sprocket.rest_rotation(c)
    return min(sprocket.tooth_angles(c), key=lambda a: abs((rest + a - 90.0 + 180.0) % 360.0 - 180.0))


def _sprocket_tooth(c: Camera) -> Point:
    s, f = c.sprocket, c.fit
    r, a = s.hub_d / 2 + f.tooth_height, math.radians(_front_tooth(c))
    return _local(c, "sprocket", r * math.cos(a), r * math.sin(a), -c.film.perf_row_z)


def _cam_notch(c: Camera) -> Point:
    s = c.sprocket
    r, a = s.notch_r, math.radians(sprocket.notch_angle(c))
    return _local(c, "sprocket", r * math.cos(a), r * math.sin(a), s.cam_z0 + s.cam_t - s.notch_depth)


def _pawl(c: Camera) -> Point:
    return _local(c, "pawl", -c.pawl.tip_arm / 2, 0.0, transport.lever_z(c)[1])


def _release_button(c: Camera) -> Point:
    """Cap top, off the coin slot that runs through its centre."""
    p = c.pawl
    return _local(c, "release_button", 0.0, p.button_cap_d / 4, transport.button_cap_z0(c) + p.button_cap_h)


def _advance_knob(c: Camera) -> Point:
    return _local(c, "advance_knob", c.takeup.knob_d / 4, 0.0, transport.advance_knob_z(c)[1])


def _rewind_knob(c: Camera) -> Point:
    return _local(c, "rewind_knob", c.rewind.knob_d / 4, 0.0, transport.rewind_knob_z(c)[1])


def _film_gate(c: Camera) -> Point:
    """Gate plate face between the aperture's bevel and the rails."""
    g = c.gate
    return 0.0, g.recess, (c.film.frame_h / 2 + g.bevel + g.rail_z - g.rail_w / 2) / 2


def _cassette(c: Camera) -> Point:
    m = c.measured
    return c.layout.cassette_x + m.cassette_d / 4, c.layout.cassette_y, m.cassette_cap_height / 2


def _rear_cover_latch(c: Camera) -> Point:
    cv = c.cover
    return _local(c, "turn_button_right", cv.button_len / 4, 0.0, cv.button_t)


def _dark_slide(c: Camera) -> Point:
    """Rear face of the pull tab, one corner radius under its top edge."""
    cv = c.cover
    return 0.0, shell.slot_mid_y(c) - cv.slide_t / 2, cv.slide_top_z - cv.handle_r


def _slot_velvet(c: Camera) -> Point:
    g = c.gate
    return 0.0, g.slot_y0 + g.trap_gap - shell.trap_velvet_t(c) / 2, c.shell.z_max


def _pinhole(c: Camera) -> Point:
    """The rim of the hole, on the shim's front face."""
    return c.optics.pinhole_d / 2, ph.cap_front_y(c) + c.pinhole.shim_t, 0.0


def _shutter_lock(c: Camera) -> Point:
    p = c.pinhole
    px, pz = ph.pivot_xz(c)
    y1 = ph.lever_y(c)[1]
    return px, y1 - p.pad_depth / 2, pz + p.flag_len + p.pad_h / 2


def _shutter_tab(c: Camera) -> Point:
    y0, y1 = ph.tab_y(c)
    return ph.tab_x(c, "open")[1], (y0 + y1) / 2, 0.0


def _finder(which: str) -> Callable[[Camera], Point]:
    def point(c: Camera) -> Point:
        v, lf = c.viewfinder, pb.leaf(c, which)
        return 0.0, lf.axle_y + pb._flat(c), v.axis_z + lf.h / 2 + v.bar / 2
    return point


def _hook_rail(c: Camera) -> Point:
    return 0.0, c.body_link.hook_front_y, (c.body_link.hook_bottom_z + c.shell.z_max) / 2


def _latch_pin(c: Camera) -> Point:
    k = c.body_link
    return 0.0, k.latch_pin_y, k.latch_pin_z + c.measured.rod_d / 2


def _m42_mount(c: Camera) -> Point:
    """Front face of the body's rear cap ring, midway across its wall."""
    return 0.0, pb.ring_seat_y(c), (c.optics.m42_thread_d + c.measured.m42_rear_cap_od) / 4


def _tripod_nut(c: Camera) -> Point:
    """The face the tripod screw enters, midway across the hex wall."""
    b = c.body
    return 0.0, b.tripod_y + (b.nut_bore + b.nut_af) / 4, pb.nut_z0(c)


FEATURES: tuple[Feature, ...] = (
    Feature("sprocket", "Sprocket", "sprocket", _sprocket_tooth),
    Feature("cam_notch", "Cam notch", "sprocket", _cam_notch),
    Feature("pawl", "Pawl", "pawl", _pawl),
    Feature("release_button", "Release button", "release_button", _release_button),
    Feature("advance_knob", "Advance knob", "advance_knob", _advance_knob),
    Feature("rewind_knob", "Rewind knob", "rewind_knob", _rewind_knob),
    Feature("film_gate", "Film gate", "shell", _film_gate),
    Feature("cassette", "Film cassette", "cassette", _cassette),
    Feature("rear_cover_latch", "Cover latch", "turn_button_right", _rear_cover_latch),
    Feature("dark_slide", "Dark slide", "dark_slide", _dark_slide),
    Feature("slot_velvet", "Velvet light trap", "slot_velvet", _slot_velvet),
    Feature("pinhole", "Pinhole", "pinhole_shim", _pinhole),
    Feature("shutter_lock", "Shutter lock", "shutter_lock", _shutter_lock),
    Feature("shutter_tabs", "Shutter tab", "shutter_open_tab", _shutter_tab),
    Feature("viewfinder_front", "Front finder frame", "viewfinder_front_frame", _finder("front")),
    Feature("viewfinder_rear", "Rear sight", "viewfinder_rear_frame", _finder("rear")),
    Feature("body_hook_rail", "Hook rail", "shell", _hook_rail),
    Feature("body_latch_pin", "Latch pin", "latch_pin", _latch_pin),
    Feature("m42_mount", "M42 lens mount", "m42_rear_cap_ring", _m42_mount),
    Feature("tripod_nut", "Tripod nut", "tripod_nut", _tripod_nut),
)


def feature_entries(c: Camera) -> list[dict]:
    unknown = [f"{f.id} -> {f.part}" for f in FEATURES if f.part not in PARTS]
    if unknown:
        raise ValueError(f"features on unregistered parts: {unknown}")
    return [
        {"id": f.id, "label": f.label, "part": f.part, "point": [round(v, 3) for v in f.point(c)]}
        for f in FEATURES
    ]
