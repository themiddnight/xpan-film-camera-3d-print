"""Seeded errors for the transport checks; collected by test_checks.py."""
from dataclasses import replace

from params import CAMERA

POCKET = "pawl nose sits in the cam pocket at rest (geometry)"
NOSE_FIT = "pawl nose fits the pocket (geometry)"
SWING = "pawl nose clears the cam pocket the whole way up and down (geometry)"
LIFT = "button travel lifts the pawl clear of the cam (geometry)"
CEILING = "lifted pawl lever clears the ceiling (geometry)"
SPRING = "pawl spring seats on the spigot and works between free and solid (geometry)"
SPINNING = "pawl bore and spool bore fit the 3mm pin (geometry)"
LEADER = "take-up spool leader slot passes the film and spares the shaft bore (geometry)"
GLUED = "glued bores fit the filed rod without touching it (geometry)"
COLLAR = "release button fits its collar bore (geometry)"
REST = "release button rests on the pawl button end (geometry)"
DRIVE = "release button drives the pawl without sinking into it the whole press (geometry)"
STROKE = "release button stroke fits under the cap (geometry)"
LUG = "release button lug passes under the ceiling when pressed (geometry)"
CAP_KNOB = "release button cap clears the advance knob (geometry)"
KNOBS = "knobs clear the shell top and the rewind tower (geometry)"
FLANGE = "take-up spool flanges clear the sprocket flange (geometry)"
CLUTCH = "take-up clutch stack closes with spring preload (geometry)"
TAKEUP_SHAFT = "take-up shaft seats in the floor and the knob (geometry)"
FORK_KEY = "rewind fork engages the spool key over its full depth (geometry)"
FORK_TOWER = "rewind fork lifts inside the tower and clear of the spool (geometry)"
REWIND_SHAFT = "rewind shaft clears the fork slot and stops in the knob (geometry)"
PIN = "sprocket pin passes the bore and stops under the hub top (geometry)"
OVERLAP = "transport parts do not overlap each other (geometry)"
BED = "printed transport parts fit the print bed (geometry)"


def _pawl(**kw):
    return replace(CAMERA, pawl=replace(CAMERA.pawl, **kw))


def _takeup(**kw):
    return replace(CAMERA, takeup=replace(CAMERA.takeup, **kw))


def _rewind(**kw):
    return replace(CAMERA, rewind=replace(CAMERA.rewind, **kw))


SEEDS = {
    "pawl nose floats above the pocket": (_pawl(nose_floor_gap=1.5), {POCKET}),
    "pawl tip wider than the pocket": (_pawl(tip_w=2.4), {NOSE_FIT}),
    "pawl nose longer than the pocket": (_pawl(nose_len=2.6), {NOSE_FIT}),
    "pawl nose square, its lower corner swings into the pocket wall": (_pawl(nose_swing_r=7.6), {SWING}),
    "pawl ratio 1:3 lifts the nose too little": (_pawl(tip_arm=3.0, button_arm=9.0), {LIFT}),
    "pawl button travel 1.8mm only": (_pawl(button_travel=1.8), {LIFT}),
    "pawl button travel 4mm hits the ceiling": (_pawl(button_travel=4.0), {CEILING}),
    "pawl spring free length 6.5mm, no preload": (_pawl(spring_free_len=6.5), {SPRING}),
    "pawl spigot wider than the spring": (_pawl(spigot_d=3.2), {SPRING}),
    "bores 3.05mm, tight on the pin": (replace(CAMERA, fit=replace(CAMERA.fit, shaft_bore=3.05)), {SPINNING}),
    "leader slot cut too close to the shaft bore": (_takeup(leader_slot_offset=2.5), {LEADER}),
    "leader slot narrower than the film": (_takeup(leader_slot_w=0.4), {LEADER}),
    "glued bores 3.0mm, no room for epoxy": (_takeup(glued_bore=3.0), {GLUED}),
    "glued bores 2.8mm cut into the rods": (_takeup(glued_bore=2.8), {GLUED, OVERLAP}),
    "button collar bore 6.2mm": (_pawl(button_hole_d=6.2), {COLLAR}),
    "lever stops at the button axis": (_pawl(button_end=0.5), {REST}),
    "button bottom flat, its inner edge sinks into the turning lever": (_pawl(button_nose_r=0.0), {DRIVE}),
    "button nose 3mm, the blunt dome sinks into the lever": (_pawl(button_nose_r=3.0), {DRIVE}),
    "button nose 0.5mm, the flat face around it sinks into the lever": (_pawl(button_nose_r=0.5), {DRIVE}),
    "button cap sits on the shell top": (_pawl(button_cap_gap=0.0), {STROKE}),
    "button lug starts above the top wall": (_pawl(button_lug_z=31.0), {LUG}),
    "button cap as wide as the knob allows no more": (_pawl(button_cap_d=8.0), {CAP_KNOB}),
    "advance knob inside the shell top": (_takeup(knob_z0=31.0), {KNOBS}),
    "rewind knob on the tower top": (_rewind(knob_gap=0.0), {KNOBS}),
    "take-up flange 28mm, 0.5mm from the sprocket flange": (_takeup(flange_d=28.0), {FLANGE}),
    "clutch spring 13mm free, 0.5mm preload": (_takeup(clutch_spring_free=13.0), {CLUTCH}),
    "take-up shaft 75mm, through the knob": (_takeup(shaft_len=75.0), {TAKEUP_SHAFT}),
    "take-up shaft sunk into the floor": (_takeup(shaft_bottom_z=-29.8, shaft_len=70.0), {TAKEUP_SHAFT}),
    "rewind fork 1mm too high for the key": (_rewind(fork_bottom=23.5), {FORK_KEY}),
    "rewind fork 7.4mm, jams in the tower": (_rewind(fork_od=7.4), {FORK_TOWER}),
    "rewind shaft runs into the fork slot": (_rewind(shaft_gap_to_roof=-1.0), {REWIND_SHAFT}),
    "sprocket pin 65mm, hits the hub roof": (_takeup(sprocket_pin_len=65.0), {PIN}),
    "advance knob 190mm, off the print bed": (_takeup(knob_d=190.0), {BED}),
}
