"""Seeded errors for the body checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA

SEEDS: dict = {
    "body cap stack 1mm deeper than the shim ring can absorb": (
        replace(CAMERA, measured=replace(CAMERA.measured, m42_seat_to_pinhole=3.0)),
        {"pinhole plane 50.0 from the film plane, M42 stack seated (geometry)",
         "body cap flange seats on the ring, not the body (geometry)"},
    ),
    "body front face proud of the M42 seat": (
        replace(CAMERA, body=replace(CAMERA.body, front_face_y=48.3)),
        {"body cap flange seats on the ring, not the body (geometry)"},
    ),
    "baffle openings inside the image cone": (
        replace(CAMERA, body=replace(CAMERA.body, baffle_clearance=-0.5)),
        {"baffles clear the image cone by 0.5mm (geometry)"},
    ),
    "rear cap cut to a 12mm opening": (
        replace(CAMERA, optics=replace(CAMERA.optics, m42_bore=12.0)),
        {"M42 mount clears the corner rays (geometry)"},
    ),
    "body footprint wider than the bridge span": (
        replace(CAMERA, body=replace(CAMERA.body, rear_half_w=40.5)),
        {"body rear face on the datum, inside the bridge span (geometry)"},
    ),
    "tongue too tall for the hook slot": (
        replace(CAMERA, body_link=replace(CAMERA.body_link, tongue_top_z=29.9)),
        {"body tongue fits the hook slot with clearance (geometry)", "body tongue clearance in hook slot"},
    ),
    "latch hook 1.2mm on the body": (
        replace(CAMERA, body_link=replace(CAMERA.body_link, latch_hook_h=1.2)),
        {"latch hook sits behind the pin and rises past its centre (geometry)"},
    ),
    "M42 pocket wall 0.8mm": (
        replace(CAMERA, body=replace(CAMERA.body, wall=0.8)),
        {"body walls >= min wall (geometry)"},
    ),
    "tripod nut moved into the M42 pocket wall": (
        replace(CAMERA, body=replace(CAMERA.body, tripod_y=32.5)),
        {"body walls >= min wall (geometry)"},
    ),
    "body wider than the print bed": (
        replace(CAMERA, body=replace(CAMERA.body, rear_half_w=95.0)),
        {"body and pinhole printed parts fit the print bed (geometry)"},
    ),
}
