"""Shared check machinery: the registry, lazy part building and geometry probes.

Area check modules (cad/check_areas/) and cad/checks.py register checks here with `@check`.
"""
import math
from dataclasses import dataclass
from typing import Callable

from build123d import Axis, Part, Pos, Vector

import mechanisms
from params import Camera
from parts import PARTS

EPS = 1e-9


@dataclass
class Result:
    name: str
    ok: bool
    detail: str


class Built:
    """Builds registered parts on first use, so layout-only runs stay fast."""

    def __init__(self, c: Camera):
        self.c = c
        self._local: dict[str, Part] = {}

    def local(self, name: str) -> Part:
        if name not in self._local:
            self._local[name] = PARTS[name].build(self.c)
        return self._local[name]

    def placed(self, name: str) -> Part:
        return PARTS[name].place(self.c) * self.local(name)

    @property
    def sprocket(self) -> Part:
        return self.local("sprocket")


CHECKS: list[tuple[str, Callable[[Camera, Built], tuple[bool, str]]]] = []


def check(name: str):
    def register(fn):
        CHECKS.append((name, fn))
        return fn
    return register


def radial_extent(part: Part, angle_deg: float, z: float, r_lo: float, r_hi: float) -> float:
    """Outer radius of solid material along a ray, by bisection (assumes inside at r_lo)."""
    a = math.radians(angle_deg)
    for _ in range(40):
        mid = (r_lo + r_hi) / 2
        if part.is_inside(Vector(mid * math.cos(a), mid * math.sin(a), z)):
            r_lo = mid
        else:
            r_hi = mid
    return r_lo


def solid_runs(part: Part, r: float, z: float, step_deg: float = 0.25) -> list[float]:
    """Angular widths (deg) of solid runs around a circle of radius r at height z."""
    n = int(360 / step_deg)
    hits = [part.is_inside(Vector(r * math.cos(math.radians(i * step_deg)),
                                  r * math.sin(math.radians(i * step_deg)), z)) for i in range(n)]
    if all(hits):
        return [360.0]
    start = hits.index(False)
    hits = hits[start:] + hits[:start]
    runs, length = [], 0
    for h in hits + [False]:
        if h:
            length += 1
        elif length:
            runs.append(length * step_deg)
            length = 0
    return runs


# Mechanism poses, applied the way the viewer applies them.

SHOOTING = {"dark_slide": 1.0, "slide_carry": 1.0, "slide_stow": 1.0}
"""Mechanism values for taking pictures: the slide pulled and stowed on the cover."""

def _stretch(shape, origin, axis, factor):
    """Scale along one coordinate axis about origin, as a spring compresses."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
    from OCP.gp import gp_GTrsf, gp_XYZ
    i = [abs(a) for a in axis].index(1.0)
    g = gp_GTrsf()
    g.SetValue(i + 1, i + 1, factor)
    shift = [0.0, 0.0, 0.0]
    shift[i] = origin[i] * (1 - factor)
    g.SetTranslationPart(gp_XYZ(*shift))
    return type(shape)(BRepBuilderAPI_GTransform(shape.wrapped, g, True).Shape())


def drive_shape(shape, d, value: float):
    if d.kind == "rotate":
        return shape.rotate(Axis(d.origin, d.axis), d.amount * value)
    if d.kind == "stretch":
        return _stretch(shape, d.origin, d.axis, 1 + d.amount * value)
    return Pos(*(a * d.amount * value for a in d.axis)) * shape


def posed(c: Camera, b: Built, values: dict[str, float]) -> dict:
    """Every driven part placed with the given mechanism values, drives applied in mechanism order."""
    shapes = {}
    for m in mechanisms.mechanisms(c):
        v = values.get(m.id, 0.0)
        if v == 0.0:
            continue
        for d in m.drives:
            shapes[d.part] = drive_shape(shapes.get(d.part, b.placed(d.part)), d, v)
    return shapes
