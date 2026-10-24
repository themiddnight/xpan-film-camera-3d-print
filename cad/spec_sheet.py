"""The numbers the presentation page publishes, picked from params with a label, unit, section and status.

`source` names where a value comes from: a params path such as `optics.pinhole_d` (an index selects
from a tuple, as in `body_link.hook_slot_y[1]`), or `derived:<name>` for a value worked out from
others. cad/check_areas/presentation.py recomputes each derived value from the published entries.
"""
import math
import re
from dataclasses import dataclass
from typing import Callable, Literal

from params import Camera
from parts import pinhole_body

Section = Literal["specs", "interface"]
Status = Literal["locked", "draft"]

DERIVED_PREFIX = "derived:"
_STEP = re.compile(r"([A-Za-z_]\w*)((?:\[\d+\])*)")


@dataclass(frozen=True)
class SpecEntry:
    id: str
    label: str
    unit: str
    section: Section
    status: Status
    source: str
    compute: Callable[[Camera], float] | None = None
    """Set for derived entries only."""


def resolve(c: Camera, path: str) -> float:
    """Follow a params path such as `body_link.hook_slot_y[1]`; any missing step raises."""
    value = c
    for step in path.split("."):
        m = _STEP.fullmatch(step)
        if m is None:
            raise ValueError(f"bad params path step {step!r} in {path!r}")
        value = getattr(value, m.group(1))
        for index in re.findall(r"\d+", m.group(2)):
            value = value[int(index)]
    return float(value)


def value_of(c: Camera, entry: SpecEntry) -> float:
    if entry.source.startswith(DERIVED_PREFIX):
        if entry.compute is None:
            raise ValueError(f"{entry.id}: derived entry has no formula")
        return entry.compute(c)
    return resolve(c, entry.source)


def _p(id, label, unit, section, status, path) -> SpecEntry:
    return SpecEntry(id, label, unit, section, status, path)


def _d(id, label, unit, section, status, name, compute) -> SpecEntry:
    return SpecEntry(id, label, unit, section, status, DERIVED_PREFIX + name, compute)


SPEC_SHEET: tuple[SpecEntry, ...] = (
    _p("frame_width", "Frame width", "mm", "specs", "locked", "film.frame_w"),
    _p("frame_height", "Frame height", "mm", "specs", "locked", "film.frame_h"),
    _d("aspect_ratio", "Aspect ratio (width to height)", "", "specs", "locked", "aspect_ratio",
       lambda c: c.film.frame_w / c.film.frame_h),
    _p("standard_frame_width", "Standard 135 frame width, for comparison", "mm", "specs", "locked",
       "film.standard_frame_w"),
    _p("perf_pitch", "Perforation pitch", "mm", "specs", "locked", "film.perf_pitch"),
    _p("perfs_per_frame", "Perforations per frame", "perfs", "specs", "locked", "film.perfs_per_frame"),
    _p("advance_per_frame", "Film advance per frame", "mm", "specs", "locked", "film.advance"),
    _p("sprocket_teeth", "Sprocket teeth", "teeth", "specs", "locked", "sprocket.teeth"),
    # A count of whole frames, not a measurement: the head and tail leader of a real roll are not
    # known until a test print loads one, so the status stays draft.
    _d("frames_per_roll", "Frames per 36-exposure roll, before loading waste", "frames", "specs", "draft",
       "frames_per_roll", lambda c: math.floor(c.film.frames_per_roll)),
    _p("sprocket_pitch_d", "Sprocket pitch diameter", "mm", "specs", "locked", "pitch_d"),
    _p("pinhole_diameter", "Pinhole diameter", "mm", "specs", "locked", "optics.pinhole_d"),
    _p("pinhole_distance", "Pinhole to film distance", "mm", "specs", "locked", "optics.pinhole_y"),
    _d("f_number", "Aperture (f-number)", "", "specs", "locked", "f_number",
       lambda c: c.optics.pinhole_y / c.optics.pinhole_d),

    _p("hook_rail_half_length", "Hook rail half length, either side of centre", "mm", "interface", "draft",
       "body_link.hook_half_x"),
    _p("hook_slot_rear", "Hook slot rear face, from the film plane", "mm", "interface", "draft",
       "body_link.hook_slot_y[0]"),
    _p("hook_slot_front", "Hook slot front face, from the film plane", "mm", "interface", "draft",
       "body_link.hook_slot_y[1]"),
    _p("hook_slot_roof", "Hook slot roof height, from gate centre", "mm", "interface", "draft",
       "body_link.hook_slot_top_z"),
    _p("tongue_rear", "Body tongue rear face, from the film plane", "mm", "interface", "draft",
       "body_link.tongue_y[0]"),
    _p("tongue_front", "Body tongue front face, from the film plane", "mm", "interface", "draft",
       "body_link.tongue_y[1]"),
    _p("tongue_top", "Body tongue top height, from gate centre", "mm", "interface", "draft",
       "body_link.tongue_top_z"),
    _p("detach_angle", "Tilt the tongue allows when the body swings off", "deg", "interface", "draft",
       "body_link.detach_deg"),
    _p("latch_pin_diameter", "Bottom latch pin diameter", "mm", "interface", "draft", "measured.rod_d"),
    _p("latch_pin_distance", "Latch pin distance from the film plane", "mm", "interface", "draft",
       "body_link.latch_pin_y"),
    _p("latch_pin_height", "Latch pin height, from gate centre", "mm", "interface", "draft",
       "body_link.latch_pin_z"),
    _p("latch_lug_gap", "Latch gap between the lugs, half width", "mm", "interface", "draft",
       "body_link.lug_x[0]"),
    _p("datum_distance", "Body datum face distance from the film plane", "mm", "interface", "draft",
       "gate.datum_y"),
    _p("gate_aperture_width", "Front aperture width", "mm", "interface", "draft", "gate.aperture_w"),
    _p("gate_aperture_height", "Front aperture height", "mm", "interface", "draft", "gate.aperture_h"),

    _p("m42_thread", "Lens mount thread diameter", "mm", "interface", "draft", "optics.m42_thread_d"),
    _p("m42_pitch", "Lens mount thread pitch", "mm", "interface", "draft", "optics.m42_pitch"),
    _p("m42_bore", "Lens mount clear bore", "mm", "interface", "draft", "optics.m42_bore"),
    _p("m42_seat_to_pinhole", "Mount seat to pinhole plane", "mm", "interface", "draft",
       "measured.m42_seat_to_pinhole"),
    _d("m42_seat_to_film", "Mount seat distance from the film plane", "mm", "interface", "draft",
       "m42_seat_to_film", pinhole_body.seat_y),
    _d("image_circle", "Minimum image circle", "mm", "interface", "draft", "image_circle",
       lambda c: math.hypot(c.film.frame_w, c.film.frame_h)),
)


def spec_entries(c: Camera) -> list[dict]:
    return [
        {"id": e.id, "label": e.label, "value": round(value_of(c, e), 4), "unit": e.unit,
         "section": e.section, "status": e.status, "source": e.source}
        for e in SPEC_SHEET
    ]
