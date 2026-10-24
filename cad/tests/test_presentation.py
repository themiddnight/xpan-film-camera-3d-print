"""Seeded errors for the feature pins and the spec sheet; collected by test_checks.py.

The pins and the sheet are fixed lists, so a seed here is a camera plus a patch of the list
(a third element: a function returning a context manager that applies it).
"""
from dataclasses import replace
from unittest.mock import patch

import features
import spec_sheet
from params import CAMERA


def _pins(change):
    """Patch FEATURES with `change` applied to the list."""
    return lambda: patch.object(features, "FEATURES", tuple(change(list(features.FEATURES))))


def _sheet(change):
    return lambda: patch.object(spec_sheet, "SPEC_SHEET", tuple(change(list(spec_sheet.SPEC_SHEET))))


def _swap(items, id_, **changes):
    return [replace(i, **changes) if i.id == id_ else i for i in items]


OFF_SURFACE = 3.0

PINS = "feature pins: unique ids, labels, real parts and every id the page names"
SURFACE = "feature anchors lie on their part's surface (geometry)"
SOURCES = "spec sheet: unique ids, valid section and status, every source resolves"
DERIVED = "spec sheet: derived values match their formulas"


def _lifted(c):
    x, y, z = features.FEATURES[[f.id for f in features.FEATURES].index("cassette")].point(c)
    return x, y, z + OFF_SURFACE


SEEDS: dict = {
    "cassette pin 3mm above the cassette": (
        CAMERA, {SURFACE},
        _pins(lambda fs: _swap(fs, "cassette", point=_lifted)),
    ),
    "pin on a part that is not registered": (
        CAMERA, {PINS},
        _pins(lambda fs: _swap(fs, "pinhole", part="pinhole_plate")),
    ),
    "two pins with one id": (
        CAMERA, {PINS},
        _pins(lambda fs: _swap(fs, "pawl", id="sprocket")),
    ),
    "a pin the page names is gone": (
        CAMERA, {PINS},
        _pins(lambda fs: [f for f in fs if f.id != "tripod_nut"]),
    ),
    "spec entry sourced from a missing param": (
        CAMERA, {SOURCES},
        _sheet(lambda es: _swap(es, "pinhole_diameter", source="optics.pinhole_diam")),
    ),
    "spec tuple index past the end": (
        CAMERA, {SOURCES},
        _sheet(lambda es: _swap(es, "hook_slot_front", source="body_link.hook_slot_y[2]")),
    ),
    "spec status typo": (
        CAMERA, {SOURCES},
        _sheet(lambda es: _swap(es, "frame_width", status="final")),
    ),
    "f-number no longer distance / diameter": (
        CAMERA, {DERIVED},
        _sheet(lambda es: _swap(es, "f_number", compute=lambda c: c.optics.pinhole_y / c.optics.pinhole_d / 2)),
    ),
    "image circle published as the frame width": (
        CAMERA, {DERIVED},
        _sheet(lambda es: _swap(es, "image_circle", compute=lambda c: c.film.frame_w)),
    ),
}
