"""Phase 1 layout check: recomputes the derived values in the design docs.

Values are copied from film_back_design.md section 17 and simple_body_design.md
sections 7-8, so edit both together. Phase 2 replaces this with cad/params.py and
cad/checks.py, which read one source of truth.
"""
import math

FAIL = []


EPS = 1e-9


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        FAIL.append(name)


def info(name, detail):
    print(f"INFO  {name}: {detail}")


MIN_WALL = 1.2
FDM_CLEARANCE = 0.3

film_t = 0.13
perf_pitch = 4.750
teeth = 14
pitch_d = teeth * perf_pitch / math.pi
hub_d = 21.04
check("pitch diameter", abs(pitch_d - 21.17) < 0.005, f"{pitch_d:.3f}mm")
check("hub = pitch - film thickness", abs(hub_d + film_t - pitch_d) < 0.01,
      f"neutral-axis circumference {math.pi * (hub_d + film_t):.3f}mm vs 66.500")

perf_along, perf_across, edge = 1.981, 2.794, 2.01
tooth_along, tooth_across = 1.4, 2.0
check("tooth fits perforation along travel", tooth_along < perf_along - 0.4,
      f"{perf_along - tooth_along:.2f}mm total clearance")
check("tooth fits perforation across", tooth_across < perf_across - 0.5,
      f"{perf_across - tooth_across:.2f}mm total clearance")

fence_gap = 35.3
film_float = (fence_gap - 35.0) / 2
rail_w, rail_c = 1.2, 16.6
rail_lo, rail_hi = rail_c - rail_w / 2, rail_c + rail_w / 2
perf_outer_edge = 17.5 - edge
check("rails clear perforations with film float", rail_lo - (perf_outer_edge + film_float) >= 0.3,
      f"rail inner edge {rail_lo:.2f}, perforation edge {perf_outer_edge:.2f} + float {film_float:.2f}")
check("rails stay on the film", rail_hi < 17.5 - film_float,
      f"rail outer edge {rail_hi:.2f}, film edge {17.5 - film_float:.2f} at worst float")

slot_front, front_wall_end, velvet_groove = 2.20, 4.20, 0.6
check("front wall over dark slide slot", front_wall_end - slot_front - velvet_groove >= MIN_WALL,
      f"{front_wall_end - slot_front - velvet_groove:.2f}mm")
rim_w, groove_w = 4.6, 2.2
check("cover groove walls", (rim_w - groove_w) / 2 >= MIN_WALL - EPS, f"{(rim_w - groove_w) / 2:.2f}mm each side")

divider_x = 42.5
sprocket_x, flange_r = 55.0, 11.5
check("sprocket flange clears divider", sprocket_x - flange_r - divider_x >= 1.0,
      f"{sprocket_x - flange_r - divider_x:.2f}mm")

spool_x, spool_y = 81.0, 12.0
sprocket_y = hub_d / 2
roll_r, core_r = 12.0, 8.0
d = math.hypot(spool_x - sprocket_x, spool_y - sprocket_y)
check("wound roll clears sprocket flange", d - flange_r - roll_r >= 2.0,
      f"{d - flange_r - roll_r:.2f}mm")
# Film arrives along +X at the hub bottom and leaves on the internal tangent to the spool.
r_neutral = pitch_d / 2
center_angle = math.degrees(math.atan2(spool_y - sprocket_y, spool_x - sprocket_x))


def wrap(r_spool):
    return center_angle + math.degrees(math.asin((r_neutral + r_spool) / d))


w_empty, w_full = wrap(core_r), wrap(roll_r)
check("sprocket wrap engages >= 1.8 teeth", w_empty / 360 * teeth >= 1.8,
      f"{w_empty:.1f}-{w_full:.1f} deg, {w_empty / 360 * teeth:.1f}-{w_full / 360 * teeth:.1f} teeth")
shoe_end = -45.0
check("cover shoe stays inside the contact arc", -90 + w_empty >= shoe_end,
      f"film leaves at {-90 + w_empty:.1f} deg, shoe ends at {shoe_end} deg")

shell_x = (-77.5, 97.5)
width = shell_x[1] - shell_x[0]
check("shell fits 180mm print limit", width <= 180, f"{width:.1f}mm")

spool_tip, ceiling = 27.0, 28.5
check("cassette spool tip clears the ceiling", ceiling - spool_tip >= 1.0, f"{ceiling - spool_tip:.1f}mm")

slot = (4.2, 6.2, 30.0)
tongue = (4.5, 5.9, 29.7)
check("body tongue clearance in hook slot",
      min(tongue[0] - slot[0], slot[1] - tongue[1], slot[2] - tongue[2]) >= FDM_CLEARANCE - EPS,
      f"Y {tongue[0] - slot[0]:.1f}/{slot[1] - tongue[1]:.1f}, Z {slot[2] - tongue[2]:.1f}mm")

shaft_d, clutch_spring_od, spring_wire = 3.0, 5.0, 0.4
check("clutch spring slides over the shaft", clutch_spring_od - 2 * spring_wire > shaft_d + 0.2,
      f"spring inside diameter {clutch_spring_od - 2 * spring_wire:.1f}mm on a {shaft_d}mm shaft")

notch_depth, button_travel = 1.8, 2.5
check("button lifts pawl clear of the notch", button_travel - notch_depth >= 0.5,
      f"{button_travel - notch_depth:.1f}mm margin at 1:1 lever ratio")

fork_top_engaged, lift, tower_top = 28.2, 8.0, 37.0
check("rewind fork lifts inside the tower", tower_top - (fork_top_engaged + lift) >= 0.5,
      f"{tower_top - (fork_top_engaged + lift):.1f}mm left at full lift")
check("lifted fork clears the spool tip", (22.5 + lift) - spool_tip >= 1.0,
      f"fork bottom {22.5 + lift:.1f} over spool tip {spool_tip}")
opening_top = 28.5
check("rear opening passes the cassette spool tip", opening_top - spool_tip >= 1.0,
      f"opening top {opening_top}, spool tip {spool_tip}")

pawl_lifted_top = 27.7
check("lifted pawl clears the ceiling", ceiling - pawl_lifted_top >= 0.5, f"{ceiling - pawl_lifted_top:.1f}mm")
button = (68.1, 23.6)
button_to_knob = math.hypot(button[0] - spool_x, button[1] - spool_y) - 3.0
check("release button clears the advance knob", button_to_knob - 13.0 >= 1.0,
      f"{button_to_knob - 13.0:.1f}mm edge to edge")
check("release button inside the chamber front wall", button[1] + 3.0 <= 27.0,
      f"button edge Y {button[1] + 3.0:.1f}, wall at 27.0")

pin_z, pin_y, pin_r = -25.5, 8.5, 1.5
body_rear_wall = (4.2, 6.7)
check("latch pin sits in front of the body rear wall", pin_y - pin_r - body_rear_wall[1] >= 0.3 - EPS,
      f"{pin_y - pin_r - body_rear_wall[1]:.1f}mm")
cantilever_top, hook_h = -27.0, 1.2
check("latch hook reaches the pin", cantilever_top + hook_h >= pin_z - pin_r + 0.3,
      f"hook top {cantilever_top + hook_h:.1f}, pin bottom {pin_z - pin_r:.1f}")

pinhole_y, datum_y = 50.0, 4.20
half_diag = math.hypot(65, 24) / 2
corner = math.degrees(math.atan(half_diag / pinhole_y))
info("corner ray angle", f"{corner:.1f} deg, cos^4 falloff {math.log2(math.cos(math.radians(corner)) ** -4):.2f} stops")

ap_w, ap_h = 67.0, 26.0
scale = (pinhole_y - datum_y) / pinhole_y
check("front aperture clears image cone at datum", ap_w > 65 * scale and ap_h > 24 * scale,
      f"cone {65 * scale:.1f} x {24 * scale:.1f} inside {ap_w} x {ap_h}")

m42_bore = 36.0
m42_depth_behind_pinhole = 10.0
cone_r = m42_depth_behind_pinhole * math.tan(math.radians(corner))
check("M42 bore clears corner rays", cone_r < m42_bore / 2,
      f"cone radius {cone_r:.1f}mm at {m42_depth_behind_pinhole}mm behind the pinhole, bore radius {m42_bore / 2}")

pinhole_d, wavelength = 0.30, 0.00055
optimal = 1.9 * math.sqrt(pinhole_y * wavelength)
check("pinhole near optimum", abs(pinhole_d - optimal) / optimal < 0.1,
      f"Rayleigh optimum {optimal:.3f}mm, f/{pinhole_y / pinhole_d:.0f}")

info("frames per 36-exp roll", f"{36 * 38.0 / 66.5:.1f} before loading waste")

print()
print("ALL PASS" if not FAIL else f"{len(FAIL)} FAILED: {', '.join(FAIL)}")
raise SystemExit(1 if FAIL else 0)
