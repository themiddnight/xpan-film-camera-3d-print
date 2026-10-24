"""Checks on the data the presentation page reads: feature anchors and the spec sheet."""
import math
from collections import Counter

from build123d import Compound, Vertex

import features
import spec_sheet
from checklib import check
from parts import PARTS

ANCHOR_TOL = 0.5
"""An anchor must lie this close to its part's surface (mm)."""
VALUE_TOL = 1e-6
SECTIONS = ("specs", "interface")
STATUSES = ("locked", "draft")
REQUIRED_FEATURES = (
    "sprocket", "cam_notch", "pawl", "release_button", "advance_knob", "rewind_knob", "film_gate",
    "cassette", "rear_cover_latch", "dark_slide", "slot_velvet", "pinhole", "shutter_lock", "shutter_tabs",
    "viewfinder_front", "viewfinder_rear", "body_hook_rail", "body_latch_pin", "m42_mount", "tripod_nut",
)
"""The ids the page's chapters and figures name; the viewer's story validator rejects a manifest without them."""
DERIVED_FORMULAS = {
    "aspect_ratio": lambda v, c: v["frame_width"] / v["frame_height"],
    "f_number": lambda v, c: v["pinhole_distance"] / v["pinhole_diameter"],
    "m42_seat_to_film": lambda v, c: v["pinhole_distance"] - v["m42_seat_to_pinhole"],
    "image_circle": lambda v, c: math.hypot(v["frame_width"], v["frame_height"]),
    "frames_per_roll": lambda v, c: math.floor(c.film.roll_exposures * c.film.standard_frame_pitch / v["advance_per_frame"]),
}
"""Each derived entry, recomputed from the entries it publishes alongside (and the film params it needs)."""


def _repeats(ids: list[str]) -> list[str]:
    return sorted(i for i, n in Counter(ids).items() if n > 1)


@check("feature pins: unique ids, labels, real parts and every id the page names")
def _(c, b):
    fs = features.FEATURES
    ids = [f.id for f in fs]
    problems = [f"repeated id {i}" for i in _repeats(ids)]
    problems += [f"{f.id}: no label" for f in fs if not f.label.strip()]
    problems += [f"{f.id}: unknown part {f.part}" for f in fs if f.part not in PARTS]
    problems += [f"missing {i}" for i in REQUIRED_FEATURES if i not in ids]
    return not problems, f"{len(fs)} features" if not problems else "; ".join(problems)


@check("feature anchors lie on their part's surface (geometry)")
def _(c, b):
    problems = []
    for f in features.FEATURES:
        if f.part not in PARTS:
            continue
        point = f.point(c)
        surface = Compound(b.placed(f.part).faces())
        gap = surface.distance_to(Vertex(*point))
        if gap > ANCHOR_TOL:
            problems.append(f"{f.id} is {gap:.2f}mm off {f.part}")
    return not problems, f"{len(features.FEATURES)} anchors within {ANCHOR_TOL}mm" if not problems else "; ".join(problems)


@check("spec sheet: unique ids, valid section and status, every source resolves")
def _(c, b):
    entries = spec_sheet.SPEC_SHEET
    problems = [f"repeated id {i}" for i in _repeats([e.id for e in entries])]
    for e in entries:
        if not e.label.strip():
            problems.append(f"{e.id}: no label")
        if e.section not in SECTIONS or e.status not in STATUSES:
            problems.append(f"{e.id}: section {e.section!r}, status {e.status!r}")
        try:
            value = spec_sheet.value_of(c, e)
        except (AttributeError, IndexError, ValueError) as err:
            problems.append(f"{e.id}: source {e.source!r} does not resolve ({err})")
            continue
        if not math.isfinite(value):
            problems.append(f"{e.id}: value {value}")
    return not problems, f"{len(entries)} entries" if not problems else "; ".join(problems)


@check("spec sheet: derived values match their formulas")
def _(c, b):
    published = {}
    for e in spec_sheet.SPEC_SHEET:
        try:
            published[e.id] = spec_sheet.value_of(c, e)
        except (AttributeError, IndexError, ValueError):
            pass  # reported by the source check
    problems = []
    for e in spec_sheet.SPEC_SHEET:
        if not e.source.startswith(spec_sheet.DERIVED_PREFIX) or e.id not in published:
            continue
        name = e.source[len(spec_sheet.DERIVED_PREFIX):]
        formula = DERIVED_FORMULAS.get(name)
        if formula is None:
            problems.append(f"{e.id}: no formula named {name!r}")
            continue
        try:
            expected = formula(published, c)
        except KeyError as err:
            problems.append(f"{e.id}: formula needs unpublished {err}")
            continue
        if abs(expected - published[e.id]) > VALUE_TOL * max(1.0, abs(expected)):
            problems.append(f"{e.id}: published {published[e.id]:.4f}, formula gives {expected:.4f}")
    return not problems, "derived entries match" if not problems else "; ".join(problems)
