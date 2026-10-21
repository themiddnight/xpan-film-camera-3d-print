"""Seeded errors for the shutter checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA


def _pinhole(**changes):
    return replace(CAMERA, pinhole=replace(CAMERA.pinhole, **changes))


SEEDS: dict = {
    "blade hole too small for the field": (
        _pinhole(blade_hole_d=1.5),
        {"open shutter, lock and pivot clear the field of view (geometry)"},
    ),
    "shutter front opening too small for the field": (
        _pinhole(front_opening=(3.0, 1.5)),
        {"open shutter, lock and pivot clear the field of view (geometry)"},
    ),
    "knob notch 1.2mm wider than the tooth each side (lock lets the blade creep open)": (
        _pinhole(notch_clearance=1.2),
        {"shutter closed: blade covers the pinhole and the lock holds it (geometry)"},
    ),
    "lever turned only 10 deg: the tooth drags on the knob": (
        _pinhole(lock_unlock_deg=10.0),
        {"unlocked lever clears the blade and knob over the whole travel (geometry)"},
    ),
    "lever detent with no depth": (
        _pinhole(detent_depth=0.0),
        {"lock lever clicks into its detent locked and unlocked (geometry)"},
    ),
    "blade detent bump wider than its dimples": (
        _pinhole(detent_d=2.0),
        {"blade slides with zero overlap and its detent bump meets a dimple closed and open (geometry)"},
    ),
    "knob only 4mm long": (
        _pinhole(knob_len=4.0),
        {"shutter knob stands out to push and its travel hits nothing (geometry)"},
    ),
    "knob rubs the body cap face": (
        _pinhole(knob_rear_gap=-0.5),
        {"shutter knob stands out to push and its travel hits nothing (geometry)"},
    ),
    "stop slot 1mm too long": (
        _pinhole(stop_clearance=0.65),
        {"blade stops at closed and at blade_travel (geometry)"},
    ),
    "lever bore pressed onto the pivot": (
        replace(CAMERA, fit=replace(CAMERA.fit, shaft_bore=2.95)),
        {"lock pivot pressed in the housing and cap, free in the lever (geometry)"},
    ),
    "pivot rod cut short of the cap": (
        _pinhole(pivot_len=7.5),
        {"lock pivot pressed in the housing and cap, free in the lever (geometry)"},
    ),
    "detent rail 1.2mm wide": (
        _pinhole(rail_w=1.2),
        {"shutter walls >= min wall (geometry)"},
    ),
}
