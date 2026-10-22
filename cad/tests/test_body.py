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
    "tripod boss 14mm: nut corners break its wall": (
        replace(CAMERA, body=replace(CAMERA.body, tripod_boss_d=14.0)),
        {"body walls >= min wall (geometry)"},
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
    "front finder frame 2mm too wide": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, front_w=51.66)),
        {"finder frames give the 65 x 24 field from one eye point (geometry)"},
    ),
    "rear finder frame cut 3:1 instead of 65:24": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, rear_h=12.65)),
        {"finder frames give the 65 x 24 field from one eye point (geometry)"},
    ),
    "rear finder hinge on the film back, behind the body rear face": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, rear_axle_y=6.0, front_axle_y=15.0)),
        {"finder stays ahead of the body rear face (geometry)"},
    ),
    "finder axis 1mm lower: the M42 body cap rim shows in the bottom of the view": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, axis_z=41.4)),
        {"finder sight lines clear in the shooting pose (geometry)"},
    ),
    "front finder hinge 6mm forward: the folded frame overhangs the body front": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, front_axle_y=27.5, front_w=57.46, front_h=21.22)),
        {"folded finder lies inside the body top outline and under the height limit (geometry)"},
    ),
    "rear hinge no higher than the front: the rear leaf folds into the front leaf": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, stack_gap=-1.6)),
        {"finder folds and unfolds without a clash (geometry)"},
    ),
    "round knuckles: nothing holds the frames up": (
        replace(CAMERA, viewfinder=replace(CAMERA.viewfinder, detent_depth=0.0)),
        {"finder detents hold each frame raised and folded (geometry)"},
    ),
}
