"""Registry of printed parts: how to build each, where it sits, how it prints."""
from dataclasses import dataclass
from typing import Callable

from build123d import Location, Part

from params import Camera
from parts import sprocket


@dataclass(frozen=True)
class PartSpec:
    build: Callable[[Camera], Part]
    place: Callable[[Camera], Location]
    print_rotation: tuple[float, float, float]
    color: str
    spins: bool = False
    """Turns about the vertical axis through its placement origin (mechanism preview)."""


PARTS: dict[str, PartSpec] = {
    "sprocket": PartSpec(
        build=sprocket.build,
        place=lambda c: Location((c.layout.sprocket_x, c.sprocket_y, 0), (0, 0, sprocket.rest_rotation(c))),
        print_rotation=(0, 0, 0),
        color="#c9a227",
        spins=True,
    ),
}
