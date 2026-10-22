"""Moving systems and the scripted frame-advance cycle for the viewer.

Each mechanism runs from value 0 (at rest) to 1 and drives parts by rotation about an axis or a slide
along one, in camera mm (docs/superpowers/specs/2026-10-22-phase3-4-parts.md, section 4). A cyclic
mechanism keeps counting past 1: the frame advance turns on, frame after frame.
"""
import math
from dataclasses import dataclass, field
from typing import Literal

from params import Camera
from parts import body, pinhole, shell, transport

Vec = tuple[float, float, float]


@dataclass(frozen=True)
class Drive:
    part: str
    kind: Literal["rotate", "slide", "stretch"]
    axis: Vec
    amount: float
    """Degrees for rotate, millimetres for slide, at mechanism value 1. For stretch, the change of
    length factor along the axis: the part scales by 1 + amount x value about the origin."""
    origin: Vec = (0.0, 0.0, 0.0)
    """A point on the rotation axis, or the fixed end of a stretch; unused for slide."""


@dataclass(frozen=True)
class Readout:
    per_unit: float
    unit: str


@dataclass(frozen=True)
class Mechanism:
    id: str
    label: str
    drives: tuple[Drive, ...]
    readout: Readout | None = None
    cyclic: bool = False
    internal: bool = False
    """Driven only by cycles; the viewer gives it no slider."""
    requires: tuple[tuple[str, float], ...] = ()
    """Mechanisms that must be at (at least) these values before this one moves, e.g. the cover
    latches turned before the cover opens. The viewer applies them; the sweep check sets them."""


@dataclass(frozen=True)
class Key:
    t: float
    values: dict[str, float]
    phase: str


@dataclass(frozen=True)
class Cycle:
    id: str
    label: str
    keys: tuple[Key, ...]
    counter_mechanism: str
    count_per_unit: float
    count_label: str
    per_unit: float
    unit: str
    focus_ghost: tuple[str, ...] = field(default_factory=tuple)
    focus_hide: tuple[str, ...] = field(default_factory=tuple)


UP: Vec = (0.0, 0.0, 1.0)
DOWN: Vec = (0.0, 0.0, -1.0)


def pawl_axis(c: Camera) -> tuple[Vec, Vec]:
    """Pivot pin axis (horizontal, across the lever in plan) and a point on it.

    The direction is chosen so a positive turn lifts the tip: with the lever running along u toward the
    button, axis x (-u) points up.
    """
    a = math.radians(c.pawl.angle_deg)
    x, y = c.pawl_pivot
    return (-math.sin(a), math.cos(a), 0.0), (x, y, c.pawl.pivot_z)


def pawl_ride_deg(c: Camera) -> float:
    """Lever turn that lifts the whole nose onto the cam top face, where it rides between clicks.

    The nose corner nearest the pivot rises least, so it sets the angle. Solved by bisection on the
    rotated corner height, since the corner sits below the pivot axis as well as along the lever.
    """
    p, s = c.pawl, c.sprocket
    cam_top = s.cam_z0 + s.cam_t
    nose_bottom = cam_top - s.notch_depth + p.nose_floor_gap
    du = p.tip_arm - p.nose_len / 2   # pivot to the nose's inner face, along the lever
    dz = nose_bottom - p.pivot_z      # negative: the nose bottom is below the pivot axis

    def height(deg: float) -> float:
        t = math.radians(deg)
        return p.pivot_z + dz * math.cos(t) + du * math.sin(t)

    lo, hi = 0.0, 45.0
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if height(mid) < cam_top else (lo, mid)
    return hi


def dark_slide_pull(c: Camera) -> float:
    """Lift that brings the slide's bottom edge 3mm above the slot mouth in the shell top."""
    bottom = shell.PARTS["dark_slide"].build(c).bounding_box().min.Z
    return c.shell.z_max - bottom + 3.0


def pawl_spring_squeeze(c: Camera, lever_deg: float) -> float:
    """Length-factor change of the pawl spring when the lever turns by lever_deg (button end goes down)."""
    length = transport.lever_z(c)[0] - c.pawl.spring_shelf_z
    return -c.pawl.button_arm * math.sin(math.radians(lever_deg)) / length


def advance_fraction_to_clear_pocket(c: Camera) -> float:
    """Sprocket turn (fraction of one frame) after which the pocket has left the nose.

    The pocket's tangential edge must pass the far side of the nose at every radius the two share;
    the innermost radius needs the largest turn.
    """
    s, p = c.sprocket, c.pawl
    r = s.notch_r - s.notch_len / 2
    turn = math.asin(min(1.0, s.notch_w / 2 / r)) + math.asin(min(1.0, p.tip_w / 2 / r))
    return turn / (2 * math.pi)


def mechanisms(c: Camera) -> tuple[Mechanism, ...]:
    sprocket_axis = (c.layout.sprocket_x, c.sprocket_y, 0.0)
    spool_axis = (c.layout.spool_x, c.layout.spool_y, 0.0)
    # The take-up winds one frame of film onto the mid-size roll; clockwise from above (film arrives
    # on its -X side heading +Y).
    spool_deg = -c.film.advance / (math.pi * c.bought.roll_d) * 360
    axis, pivot = pawl_axis(c)
    spring_base = (*c.pawl_button, c.pawl.spring_shelf_z)
    return (
        Mechanism(
            "advance", "Advance knob",
            (
                # Film runs +X past the rear (-Y) side of the sprocket, which turns it counter-clockwise from above.
                Drive("sprocket", "rotate", UP, 360.0, sprocket_axis),
                Drive("takeup_spool", "rotate", UP, spool_deg, spool_axis),
                Drive("drive_collar", "rotate", UP, spool_deg, spool_axis),
                Drive("advance_knob", "rotate", UP, spool_deg, spool_axis),
                Drive("takeup_shaft", "rotate", UP, spool_deg, spool_axis),
            ),
            Readout(c.film.advance, "mm of film"),
            cyclic=True,
            # Turned by hand from the slider, the sprocket would run into the locked pawl; lift it onto the cam.
            requires=(("pawl_ride", 1.0),),
        ),
        Mechanism(
            "release", "Release button",
            (
                Drive("release_button", "slide", DOWN, c.pawl.button_travel),
                Drive("pawl", "rotate", axis, transport.pawl_lift_deg(c), pivot),
                Drive("pawl_spring", "stretch", UP, pawl_spring_squeeze(c, transport.pawl_lift_deg(c)), spring_base),
            ),
            Readout(c.pawl.button_travel, "mm pressed"),
        ),
        Mechanism(
            "pawl_ride", "Pawl rides on the cam",
            (
                Drive("pawl", "rotate", axis, pawl_ride_deg(c), pivot),
                Drive("pawl_spring", "stretch", UP, pawl_spring_squeeze(c, pawl_ride_deg(c)), spring_base),
            ),
            internal=True,
        ),
        Mechanism(
            "turn_buttons", "Turn the cover latches",
            tuple(Drive(f"turn_button_{side}", "rotate", UP, 90.0, (sign * c.cover.button_x, c.cover.button_y, 0.0))
                  for side, sign in (("left", -1), ("right", 1))),
        ),
        Mechanism(
            "cover", "Open rear cover",
            # About +X, a positive turn swings the cover's top backward (-Y), away from the shell.
            tuple(Drive(p, "rotate", (1.0, 0.0, 0.0), c.cover.open_deg, (0.0, c.cover.hinge_axis_y, c.cover.hinge_axis_z))
                  for p in ("rear_cover", "pressure_pad")),
            Readout(c.cover.open_deg, "deg open"),
            requires=(("turn_buttons", 1.0),),
        ),
        Mechanism(
            "dark_slide", "Pull dark slide",
            (Drive("dark_slide", "slide", UP, dark_slide_pull(c)),),
            Readout(dark_slide_pull(c), "mm pulled"),
        ),
        Mechanism(
            "rewind", "Lift rewind knob",
            tuple(Drive(p, "slide", UP, c.rewind.lift) for p in ("rewind_knob", "rewind_fork", "rewind_shaft")),
            Readout(c.rewind.lift, "mm lifted"),
        ),
        Mechanism(
            "shutter_lock", "Unlock shutter",
            (Drive("shutter_lock", "rotate", pinhole.lock_axis(c)[0], c.pinhole.lock_unlock_deg, pinhole.lock_axis(c)[1]),),
        ),
        Mechanism(
            "shutter", "Open shutter",
            tuple(Drive(p, "slide", (1.0, 0.0, 0.0), c.pinhole.blade_travel) for p in ("shutter_blade", "shutter_knob")),
            Readout(c.pinhole.blade_travel, "mm open"),
            requires=(("shutter_lock", 1.0),),
        ),
        Mechanism(
            "finder_front", "Fold front finder frame",
            (Drive("viewfinder_front_frame", "rotate", *_fold(c, "front")),),
            Readout(-body.FOLD_DEG, "deg folded"),
        ),
        Mechanism(
            "finder_rear", "Fold rear finder frame",
            (Drive("viewfinder_rear_frame", "rotate", *_fold(c, "rear")),),
            Readout(-body.FOLD_DEG, "deg folded"),
            # The rear frame lies on the folded front frame; raised, the front frame stands in its way.
            requires=(("finder_front", 1.0),),
        ),
    )


def _fold(c: Camera, which: str) -> tuple[Vec, float, Vec]:
    axis, origin = body.fold_axis(c, which)
    return axis, body.FOLD_DEG, origin


def frame_cycle(c: Camera) -> Cycle:
    """One frame advance as film-back.md section 8.2 describes it, timed for viewing.

    Press the button (tip lifts out of the pocket), turn the knob until the pocket has left the tip,
    let the button go (the tip rides on the cam), keep turning; one full turn brings the pocket back
    and the tip drops in with a click.
    """
    clear = advance_fraction_to_clear_pocket(c)
    s, p = c.sprocket, c.pawl
    # The nose can fall once the returning pocket lies under all of it: within the pocket's spare width.
    drop = 1.0 - (s.notch_w - p.tip_w) / 2 / (2 * math.pi * s.notch_r)

    def key(t, advance, release, ride, phase):
        return Key(t, {"advance": advance, "release": release, "pawl_ride": ride}, phase)

    keys = (
        key(0.0, 0.0, 0.0, 0.0, "press the release button"),
        key(0.6, 0.0, 1.0, 0.0, "turn the advance knob"),
        key(1.3, 2 * clear, 1.0, 0.0, "let go: the pawl rides on the cam"),
        key(1.8, 3 * clear, 0.0, 1.0, "riding: the film turns the sprocket"),
        key(5.4, drop, 0.0, 1.0, "pocket returns: click"),
        key(5.55, 1.0, 0.0, 0.0, "locked: one frame advanced"),
        key(6.3, 1.0, 0.0, 0.0, "locked: one frame advanced"),
    )
    return Cycle(
        "frame", "Advance one frame", keys,
        counter_mechanism="advance",
        count_per_unit=c.film.perfs_per_frame,
        count_label="perf",
        per_unit=c.film.advance,
        unit="mm",
        focus_ghost=("shell", "rear_cover", "pressure_pad", "dark_slide", "turn_button_left", "turn_button_right"),
        focus_hide=("viewfinder_rear_frame", "viewfinder_front_frame"),
    )


def cycles(c: Camera) -> tuple[Cycle, ...]:
    return (frame_cycle(c),)


def check_requires(ms: tuple[Mechanism, ...]) -> None:
    ids = {m.id for m in ms}
    for m in ms:
        for r, _ in m.requires:
            if r not in ids or r == m.id:
                raise ValueError(f"mechanism {m.id} requires unknown mechanism {r}")


def manifest_entries(c: Camera, registered: set[str]) -> tuple[list[dict], list[dict]]:
    """Mechanisms and cycles for the manifest. Every named part and mechanism must exist."""
    ms = mechanisms(c)
    check_requires(ms)
    out_m = []
    for m in ms:
        unknown = [d.part for d in m.drives if d.part not in registered]
        if unknown:
            raise ValueError(f"mechanism {m.id} drives unregistered parts: {unknown}")
        out_m.append({
            "id": m.id,
            "label": m.label,
            "cyclic": m.cyclic,
            "internal": m.internal,
            "requires": [{"mechanism": r, "value": v} for r, v in m.requires],
            "readout": None if m.readout is None else {"per_unit": m.readout.per_unit, "unit": m.readout.unit},
            "drives": [{"part": d.part, "kind": d.kind, "axis": list(d.axis), "origin": list(d.origin),
                        "amount": d.amount} for d in m.drives],
        })
    ids = {m.id for m in ms}
    out_c = []
    for cy in cycles(c):
        named = {k for key in cy.keys for k in key.values} | {cy.counter_mechanism}
        if named - ids:
            raise ValueError(f"cycle {cy.id} names unknown mechanisms: {sorted(named - ids)}")
        missing = [p for p in cy.focus_ghost + cy.focus_hide if p not in registered]
        if missing:
            raise ValueError(f"cycle {cy.id} focus names unregistered parts: {missing}")
        out_c.append({
            "id": cy.id,
            "label": cy.label,
            "keys": [{"t": k.t, "values": k.values, "phase": k.phase} for k in cy.keys],
            "counter": {"mechanism": cy.counter_mechanism, "count_per_unit": cy.count_per_unit,
                        "count_label": cy.count_label, "per_unit": cy.per_unit, "unit": cy.unit},
            "focus": {"ghost": list(cy.focus_ghost), "hide": list(cy.focus_hide)},
        })
    return out_m, out_c
