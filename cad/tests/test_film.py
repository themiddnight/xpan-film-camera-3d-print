"""Seeded errors for the film checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA

SEEDS: dict = {
    "v03 hub 20.2mm drags the film off the rails and the hub": (
        replace(CAMERA, sprocket=replace(CAMERA.sprocket, hub_d=20.2)),
        {"film lies on the rails across the gate (geometry)", "film sits on the sprocket hub (geometry)"},
    ),
    "cassette seated at X = -10, film starts past the gate centre": (
        replace(CAMERA, layout=replace(CAMERA.layout, cassette_x=-10.0)),
        {"film run from gate centre to sprocket tangent (geometry)", "film lies on the rails across the gate (geometry)",
         "cassette fits its chamber (geometry)"},
    ),
    "perforations loaded 1.0mm off the teeth": (
        replace(CAMERA, bought=replace(CAMERA.bought, film_phase=1.0)),
        {"perforation centred on every tooth in the wrap (geometry)"},
    ),
    "film 35.6mm wide in a 35.4mm flange gap": (
        replace(CAMERA, film=replace(CAMERA.film, width=35.6)),
        {"film clears the sprocket flanges (geometry)"},
    ),
    "cassette lip envelope measured 33mm": (
        replace(CAMERA, measured=replace(CAMERA.measured, cassette_lip_envelope=33.0)),
        {"cassette fits its chamber (geometry)"},
    ),
    "spool key end measured 10mm tall": (
        replace(CAMERA, measured=replace(CAMERA.measured, spool_top_protrusion=10.0)),
        {"cassette fits its chamber (geometry)"},
    ),
}
