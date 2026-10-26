"""The shape of a registry entry. Every part module exports PARTS: dict[str, PartSpec]."""
from dataclasses import dataclass
from typing import Callable, Literal

from build123d import Location, Part

from params import Camera

Group = Literal["film-back", "body", "pinhole"]
Kind = Literal["printed", "stock", "bought"]


def at_origin(c: Camera) -> Location:
    """Placement for parts built directly in camera coordinates."""
    return Location()


@dataclass(frozen=True)
class PartSpec:
    build: Callable[[Camera], Part]
    place: Callable[[Camera], Location]
    """Assembled, at-rest pose in camera coordinates."""
    group: Group
    kind: Kind
    color: str
    print_rotation: tuple[float, float, float] | None = None
    """Rotation into print orientation. Required for printed parts, None for the others."""
    bom: str | None = None
    """The `#` of the docs/bom.md Parts row a stock or bought part comes from, such as "1" or "7b"."""
    inventory: bool = True
    """False for what loads into the camera rather than being part of it (cassette, film)."""

    def __post_init__(self):
        if (self.kind == "printed") != (self.print_rotation is not None):
            raise ValueError("printed parts need a print_rotation; stock and bought parts must not have one")
        if self.inventory and (self.kind == "printed") == (self.bom is not None):
            raise ValueError("an inventory part that is not printed needs a bom row; a printed part must not have one")
