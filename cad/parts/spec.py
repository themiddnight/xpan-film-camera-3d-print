"""The shape of a registry entry. Every part module exports PARTS: dict[str, PartSpec]."""
from dataclasses import dataclass
from typing import Callable, Literal

from build123d import Location, Part

from params import Camera

Group = Literal["film-back", "body", "pinhole"]
Kind = Literal["printed", "bought"]


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
    """Rotation into print orientation. Required for printed parts, None for bought ones."""

    def __post_init__(self):
        if (self.kind == "printed") != (self.print_rotation is not None):
            raise ValueError("printed parts need a print_rotation; bought parts must not have one")
