"""Registry of every part: how to build it, where it sits, how it prints.

Each module owns its parts (docs/superpowers/specs/2026-10-22-phase3-4-parts.md, section 2).
"""
from parts import body, film, pinhole, shell, sprocket, transport
from parts.spec import PartSpec

PARTS: dict[str, PartSpec] = {}
for _module in (shell, sprocket, transport, body, pinhole, film):
    for _name, _spec in _module.PARTS.items():
        if _name in PARTS:
            raise ValueError(f"part {_name} registered twice")
        PARTS[_name] = _spec
