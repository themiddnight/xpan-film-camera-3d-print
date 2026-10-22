"""Seeded errors for the shell checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA

C = CAMERA

SEEDS: dict = {
    "gate aperture printed 66mm wide": (
        replace(C, film=replace(C.film, frame_w=66.0)),
        {"gate aperture 65.0 x 24.0, centred, rounded and bevelled (geometry)"},
    ),
    "rails moved onto the perforations": (
        replace(C, gate=replace(C.gate, rail_z=15.5)),
        {"rails on the film edge band, proud of the gate recess (geometry)"},
    ),
    "gate recess only 0.1mm under the rails": (
        replace(C, gate=replace(C.gate, recess=0.1)),
        {"rails on the film edge band, proud of the gate recess (geometry)"},
    ),
    "2.5mm front wall moves the body datum": (
        replace(C, gate=replace(C.gate, front_wall=2.5)),
        {"body datum face at Y = 4.20 and the body bay clear (geometry)"},
    ),
    "dark slide slot too tight for the sheet": (
        replace(C, gate=replace(C.gate, slot=0.6)),
        {"dark slide slot width, depth and mouth (geometry)"},
    ),
    "press holes bigger than the pins": (
        replace(C, fit=replace(C.fit, pin_press_hole=3.1)),
        {"pin, shaft, insert and collar bore fits (geometry)"},
    ),
    "cover tongue as wide as its groove": (
        replace(C, cover=replace(C.cover, tongue_w=2.2)),
        {"cover tongue fits its groove with clearance (geometry)"},
    ),
    "pad rim tall enough to hit the fences": (
        replace(C, cover=replace(C.cover, pad_rim_h=2.5)),
        {"rear cover closes on the shell and swings open clear of it and the released latches (geometry)"},
    ),
    "hinge axis at the tongue tip": (
        replace(C, cover=replace(C.cover, hinge_axis_y=1.27)),
        {"rear cover closes on the shell and swings open clear of it and the released latches (geometry)",
         "hinge axis at the tongue mid-depth, cover knuckle under the shell bottom"},
    ),
    "left turn button swings into the rewind tower": (
        replace(C, cover=replace(C.cover, button_x=48.0)),
        {"turn buttons clear the tower, collars, knob, release button and slide handle (geometry)"},
    ),
    "latch dog too short to stop the cover": (
        replace(C, cover=replace(C.cover, dog_h=0.1)),
        {"latched turn buttons stop the cover opening (geometry)"},
    ),
    "latch groove cut for the opposite turn": (
        replace(C, cover=replace(C.cover, button_release_deg=-90.0)),
        {"turn buttons turn a quarter to release, clear of everything round them (geometry)"},
    ),
    "turn buttons so far back the released dog sits in the lip": (
        replace(C, cover=replace(C.cover, button_y=1.0)),
        {"rear cover closes on the shell and swings open clear of it and the released latches (geometry)"},
    ),
    "shell longer than the print bed": (
        replace(C, shell=replace(C.shell, x_max=105.0)),
        {"shell-module printed parts fit the print bed (geometry)"},
    ),
    "pawl cheeks pinch the lever": (
        replace(C, pawl=replace(C.pawl, cheek_gap=3.0)),
        {"pawl cheeks, spring shelf and button bayonet match the pawl interface (geometry)"},
    ),
    "bayonet leg cut through the top of the wall": (
        replace(C, shell=replace(C.shell, button_lug_rest_z=30.5)),
        {"pawl cheeks, spring shelf and button bayonet match the pawl interface (geometry)"},
    ),
    "film throat pinches the film": (
        replace(C, shell=replace(C.shell, throat_gap=0.2)),
        {"film throat centres the film with clearance (geometry)"},
    ),
    "cover shoe presses the film into the hub": (
        replace(C, cover=replace(C.cover, shoe_film_gap=-0.05)),
        {"cover shoe holds the film on the sprocket teeth (geometry)"},
    ),
    "pad foam too thick for the cover gap": (
        replace(C, shell=replace(C.shell, pad_foam=2.5)),
        {"pressure pad squeeze and coverage (geometry)"},
    ),
    "dark slide keeps its 28mm carry handle": (
        replace(C, cover=replace(C.cover, slide_top_z=60.0)),
        {"dark slide pull tab is a pinch grip, low over the cover lip (geometry)"},
    ),
    "pull tab narrower than a fingertip": (
        replace(C, cover=replace(C.cover, handle_w=12.0)),
        {"dark slide pull tab is a pinch grip, low over the cover lip (geometry)"},
    ),
    "holder channel no deeper than the slide": (
        replace(C, cover=replace(C.cover, holder_gap=0.5)),
        {"stowed dark slide fits its holder with clearance and is held (geometry)"},
    ),
    "holder bumps too low to touch the slide": (
        replace(C, cover=replace(C.cover, holder_bump_h=0.25)),
        {"stowed dark slide fits its holder with clearance and is held (geometry)"},
    ),
    "stowed slide's tab stands over the cover top": (
        replace(C, cover=replace(C.cover, stowed_bottom_z=-20.0)),
        {"stowed dark slide and its holder clear everything, cover closed and swung open (geometry)"},
    ),
    "holder over the eye line where the face rests": (
        replace(C, cover=replace(C.cover, holder_x=30.0)),
        {"stowed dark slide and its holder clear everything, cover closed and swung open (geometry)"},
    ),
    "holder hung below the tripod seat": (
        replace(C, cover=replace(C.cover, stowed_bottom_z=-40.0)),
        {"stowed dark slide and its holder clear everything, cover closed and swung open (geometry)",
         "tripod seat is the lowest plane, plate-clear of the hinge knuckles (geometry)"},
    ),
    "cover swings far enough to drive the stowed slide into the body's feet": (
        replace(C, cover=replace(C.cover, open_deg=200.0)),
        {"stowed dark slide and its holder clear everything, cover closed and swung open (geometry)"},
    ),
}
