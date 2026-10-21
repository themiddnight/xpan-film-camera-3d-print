"""Moving systems for the viewer. Each runs from value 0 (at rest) to 1 and drives parts.

See docs/superpowers/specs/2026-10-22-phase3-4-parts.md, section 4. Coordinates are camera mm.
"""
from dataclasses import dataclass
from typing import Literal

from params import Camera

Vec = tuple[float, float, float]


@dataclass(frozen=True)
class Drive:
    part: str
    kind: Literal["rotate", "slide"]
    axis: Vec
    amount: float
    """Degrees for rotate, millimetres for slide, at mechanism value 1."""
    origin: Vec = (0.0, 0.0, 0.0)
    """A point on the rotation axis; unused for slide."""


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


UP: Vec = (0.0, 0.0, 1.0)


def mechanisms(c: Camera) -> tuple[Mechanism, ...]:
    sprocket_axis = (c.layout.sprocket_x, c.sprocket_y, 0.0)
    return (
        Mechanism(
            "advance", "Advance one frame",
            # Film runs +X past the rear (-Y) side of the sprocket, which turns it counter-clockwise from above.
            (Drive("sprocket", "rotate", UP, 360.0, sprocket_axis),),
            Readout(c.film.advance, "mm of film"),
        ),
    )


def manifest_entries(c: Camera, registered: set[str]) -> list[dict]:
    out = []
    for m in mechanisms(c):
        unknown = [d.part for d in m.drives if d.part not in registered]
        if unknown:
            raise ValueError(f"mechanism {m.id} drives unregistered parts: {unknown}")
        out.append({
            "id": m.id,
            "label": m.label,
            "readout": None if m.readout is None else {"per_unit": m.readout.per_unit, "unit": m.readout.unit},
            "drives": [{"part": d.part, "kind": d.kind, "axis": list(d.axis), "origin": list(d.origin),
                        "amount": d.amount} for d in m.drives],
        })
    return out
