"""Proves the checks catch known mistakes. Run from the repository root:
uv run python cad/tests/test_checks.py

Each seed is a past or plausible design error; the named checks must fail on it,
and the shipped parameters must pass everything.
"""
import importlib
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # cad/ holds params, parts and checks
sys.path.insert(0, str(HERE))

from checklib import CHECKS
from checks import run_checks
from params import CAMERA

SEEDS = {
    "v01 sprocket hub 20.2mm (film floated off the hub)": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, hub_d=20.2)),
        {"film advance per sprocket turn (geometry)", "hub = pitch diameter - film thickness"},
    ),
    "13-tooth sprocket": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, teeth=13)),
        {"sprocket tooth count (geometry)"},
    ),
    "tooth wider than the perforation allows": (
        replace(CAMERA, fit=replace(CAMERA.fit, tooth_along_root=2.0, tooth_along_tip=1.8)),
        {"tooth root fits perforation along travel (geometry)"},
    ),
    "straight film path past the sprocket": (
        replace(CAMERA, layout=replace(CAMERA.layout, spool_y=-8.0)),
        {"sprocket wrap engages >= 1.8 teeth"},
    ),
    "v02 draft rails over the perforations": (
        replace(CAMERA, gate=replace(CAMERA.gate, rail_w=1.6, rail_z=16.5, fence_gap=35.4)),
        {"rails clear perforations with film float"},
    ),
    "notch cut through the cam rim": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, notch_r=7.5)),
        {"lock notch is a closed pocket of the right depth (geometry)"},
    ),
    "no centre relief": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, relief_half_h=11.0)),
        {"centre relief keeps the image area off the hub"},
    ),
    "flanges pinch the film": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, flange_gap=34.0)),
        {"sprocket flanges pass the film"},
    ),
    "bore smaller than the pin": (
        replace(CAMERA, fit=replace(CAMERA.fit, shaft_bore=2.9)),
        {"shaft bore clearance"},
    ),
    "oversized cam hits the divider": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, cam_d=26.0)),
        {"sprocket part clears the divider wall (geometry)"},
    ),
    "take-up flange too big": (
        replace(CAMERA, takeup=replace(CAMERA.takeup, flange_d=34.0)),
        {"take-up flange clears sprocket flange"},
    ),
    "button travel lifts the pawl into the ceiling": (
        replace(CAMERA, pawl=replace(CAMERA.pawl, button_travel=4.0)),
        {"lifted pawl clears the ceiling"},
    ),
    "short lever arm lifts the tip too little": (
        replace(CAMERA, pawl=replace(CAMERA.pawl, tip_arm=3.0, button_arm=9.0)),
        {"button lifts pawl clear of the notch"},
    ),
    "v02 draft latch hook 1.2mm": (
        replace(CAMERA, body_link=replace(CAMERA.body_link, latch_hook_h=1.2)),
        {"latch hook rises past the pin centre"},
    ),
    "pocket much wider than the pawl nose (loose lock)": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, notch_w=3.4)),
        {"locked pawl stops the sprocket within the backlash limit (geometry)"},
    ),
    "printer bed smaller than the shell": (
        replace(CAMERA, print=replace(CAMERA.print, bed=150.0)),
        {"every printed part fits the print bed (geometry)"},
    ),
    "pins in clearance holes instead of a press fit": (
        replace(CAMERA, fit=replace(CAMERA.fit, pin_press_hole=3.05)),
        {"no parts overlap beyond the intended fits (geometry)"},
    ),
    "take-up spool moved into the sprocket": (
        replace(CAMERA, layout=replace(CAMERA.layout, spool_x=77.0)),
        {"no parts overlap beyond the intended fits (geometry)"},
    ),
    "rewind fork with no tower": (
        replace(CAMERA, rewind=replace(CAMERA.rewind, tower_top_inside=28.5)),
        {"rewind fork lifts inside the tower"},
    ),
}


# Each area adds its own seeds in tests/test_<area>.py as a SEEDS dict of the same shape.
for _path in sorted(HERE.glob("test_*.py")):
    if _path.stem != "test_checks":
        _area = importlib.import_module(_path.stem).SEEDS
        if _area.keys() & SEEDS.keys():
            raise ValueError(f"{_path.name} repeats a seed label")
        SEEDS.update(_area)


def shipped_failures(name: str) -> set[str]:
    return {r.name for r in run_checks(CAMERA, {name}) if not r.ok}


def seed_misses(label: str) -> set[str]:
    """The checks a seed should trip but does not. Only those checks run: a seed is caught or
    missed on them alone, and skipping the rest is what keeps the suite minutes, not hours."""
    camera, expected, *patch = SEEDS[label]
    with patch[0]() if patch else nullcontext():
        failed = {r.name for r in run_checks(camera, expected) if not r.ok}
    return expected - failed


def main() -> int:
    start = time.perf_counter()
    # Each shipped check and each seed is its own task; the slowest checks take over a minute,
    # so one process per core keeps the wall time near the slowest single task.
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        shipped = {name: pool.submit(shipped_failures, name) for name, _ in CHECKS}
        seeds = {label: pool.submit(seed_misses, label) for label in SEEDS}
        problems = []
        baseline = set().union(*(f.result() for f in shipped.values()))
        if baseline:
            problems.append(f"shipped parameters fail: {sorted(baseline)}")
        for label, future in seeds.items():
            missing = future.result()
            print(f"{label}: {'caught' if not missing else f'MISSED {sorted(missing)}'}")
            if missing:
                problems.append(label)
    print()
    print(f"{len(CHECKS)} shipped checks and {len(SEEDS)} seeds in {time.perf_counter() - start:.0f}s")
    print("ALL SEEDS CAUGHT" if not problems else f"PROBLEMS: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
