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
        {"M42 mount and shutter clear the corner rays (geometry)"},
    ),
    "shutter front opening too small for the field": (
        replace(CAMERA, pinhole=replace(CAMERA.pinhole, front_opening=(3.0, 1.5))),
        {"M42 mount and shutter clear the corner rays (geometry)"},
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
    "blade hole too small for the field": (
        replace(CAMERA, pinhole=replace(CAMERA.pinhole, blade_hole_d=1.5)),
        {"shutter blade covers the pinhole closed and clears the field open (geometry)"},
    ),
    "M42 pocket wall 0.8mm": (
        replace(CAMERA, body=replace(CAMERA.body, wall=0.8)),
        {"body and pinhole walls >= min wall (geometry)"},
    ),
    "tripod boss 14mm: nut corners break its wall": (
        replace(CAMERA, body=replace(CAMERA.body, tripod_boss_d=14.0)),
        {"body and pinhole walls >= min wall (geometry)"},
    ),
    "v01 boss 0.5mm under the film-back bottom, knuckles hang lower": (
        replace(CAMERA, body=replace(CAMERA.body, seat_clear=-6.8)),
        {"tripod seat is the lowest plane, plate-clear of the hinge knuckles (geometry)"},
    ),
    "seat only 0.2mm under the knuckles": (
        replace(CAMERA, body=replace(CAMERA.body, seat_clear=0.2)),
        {"tripod seat is the lowest plane, plate-clear of the hinge knuckles (geometry)"},
    ),
    "7mm of plastic under the nut: a 5mm screw never reaches it": (
        replace(CAMERA, body=replace(CAMERA.body, tripod_floor=7.0)),
        {"a 5mm tripod screw reaches the nut through a clear hole (geometry)"},
    ),
    "rear feet 6mm apart under the latch notch: the camera tips sideways": (
        replace(CAMERA, body=replace(CAMERA.body, foot_x=(2.0, 8.0))),
        {"camera stands level on its three feet, centre of mass inside them (geometry)"},
    ),
    "body wider than the print bed": (
        replace(CAMERA, body=replace(CAMERA.body, rear_half_w=95.0)),
        {"body and pinhole printed parts fit the print bed (geometry)"},
    ),
}
