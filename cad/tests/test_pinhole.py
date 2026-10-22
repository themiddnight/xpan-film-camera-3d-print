"""Seeded errors for the shutter checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA


def _pinhole(**changes):
    return replace(CAMERA, pinhole=replace(CAMERA.pinhole, **changes))


LEVER_SWING = "lever turns clear of the housing apart from its detent, and unlocked clears the blade and tabs (geometry)"
TABS = "shutter tabs: the one to push next stands proud, the other near flush, travel hits nothing (geometry)"

SEEDS: dict = {
    "blade hole too small for the field": (
        _pinhole(blade_hole_d=1.5),
        {"open shutter, lock and pivot clear the field of view (geometry)"},
    ),
    "shutter front opening too small for the field": (
        _pinhole(front_opening=(3.0, 1.5)),
        {"open shutter, lock and pivot clear the field of view (geometry)"},
    ),
    "tongue notch 1.2mm wider than the tooth each side (lock lets the blade creep open)": (
        _pinhole(notch_clearance=1.2),
        {"shutter closed: blade covers the pinhole and the lock holds it (geometry)"},
    ),
    "tabs behind the lever and the tooth 3.5mm further out: the lever locks with the shutter open": (
        _pinhole(tooth_x=-21.5, tab_proud=-1.5),
        {"shutter lock engages only with the shutter closed (geometry)"},
    ),
    "lever turned only 10 deg: the tooth drags on the open tab": (
        _pinhole(lock_unlock_deg=10.0),
        {LEVER_SWING},
    ),
    "tooth 0.5mm off the housing edge: it swings up into the housing corner": (
        _pinhole(tooth_x=-16.5),
        {LEVER_SWING},
    ),
    "lock pad on a 4mm flag, level with the housing top": (
        _pinhole(flag_len=4.0),
        {"shutter lock sits on top: thumb pad above the housing, nothing below it (geometry)"},
    ),
    "lock pad raised into the finder's view": (
        _pinhole(flag_len=17.0),
        {"finder sight lines clear in the shooting pose (geometry)"},
    ),
    "lever detent with no depth": (
        _pinhole(detent_depth=0.0),
        {"lock lever clicks into its detent locked and unlocked (geometry)"},
    ),
    "blade detent bump wider than its dimples": (
        _pinhole(detent_d=2.0),
        {"blade slides with zero overlap and its detent bump meets a dimple closed and open (geometry)"},
    ),
    "tabs 8mm long: the near-flush tab stands 8.5mm out": (
        _pinhole(tab_len=8.0),
        {TABS},
    ),
    "tabs 0.1mm off the housing: the tab bottoms before the stop": (
        _pinhole(tab_gap=0.1),
        {TABS},
    ),
    "tab rubs the body cap face": (
        _pinhole(tab_rear_gap=-0.5),
        {TABS},
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
    "tab walls 0.8mm beside the tongue slit": (
        _pinhole(tab_wall=0.8),
        {"shutter walls >= min wall (geometry)"},
    ),
}
