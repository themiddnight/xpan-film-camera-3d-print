// X-Pan DIY Camera - Simple Pinhole Body v01  [STARTER]
// Units: millimeters
// Coordinate system (same convention as the film back):
//   X = width (film travel direction, cartridge->take-up)
//   Y = depth, +Y is FRONT (toward the lens/pinhole module)
//   Z = height
//
// This body is a light-tight dark chamber that mounts on the shared film
// back and receives an M42 front module (pinhole or lens). It sets the
// 50mm pinhole-to-film distance.
//
// STATUS: geometrically-correct STARTER. The dark chamber, optical depth,
// and M42 register are modelled to spec. The body<->film-back hook/latch
// tabs are provisional and MUST be test-fit against the printed film back
// (they mate to the film back's top hook rail and bottom 3mm latch pin).
// The M42 is modelled as a PLAIN register bore (see m42_mode) because a
// printed thread needs per-printer tuning — cut/tap it, print a threaded
// insert, or bond an M42 adapter ring.

$fn = 96;

part = "body"; // [body, viewfinder_clip]

// ---------- Interface constants (must match film-back-v01-fixed.scad) ----------
frame_w            = 65.0;
frame_h            = 24.0;
film_w             = 35.0;
body_h             = 62.0;   // film back height; body matches it
bridge_w           = 95.0;   // film back centre bridge width (mating zone)
front_bridge_y     = 20.0;   // film back front datum (rear->front)
film_plane_y       = 15.8;   // film plane inside the film back (rear->front)
// distance from the film back FRONT mating face back to the film plane:
film_to_datum      = front_bridge_y - film_plane_y;   // = 4.2mm

hook_lip_h         = 4.0;    // film back top hook rail height
hook_lip_d         = 5.0;    // film back top hook rail +Y projection
latch_pin_d        = 3.0;    // film back bottom latch pin
latch_pin_z        = 8.0;    // pin height above film back base (approx)
latch_pin_y        = front_bridge_y + 4.0;  // pin Y (in film-back frame)

// ---------- Optical / body depth ----------
pinhole_to_film    = 50.0;
// The body rear mating face sits on the film-back front datum, which is
// film_to_datum in front of the film plane. So the pinhole plane must be
// this far in front of the body rear face:
optical_len        = pinhole_to_film - film_to_datum;   // = 45.8mm
front_plate_t      = 6.0;    // thickness of the M42 front plate
body_len_y         = optical_len + front_plate_t;        // rear face(0) -> outer front

// ---------- Body envelope ----------
wall               = 3.0;
flange_extra_w     = 4.0;    // rear flange overhangs the bridge each side for the seal
body_W             = bridge_w + 2 * flange_extra_w;       // = 103mm
body_H             = body_h;                              // = 62mm
inner_W            = frame_w + 10.0;   // chamber wider than the frame for the light cone
inner_H            = frame_h + 10.0;

// ---------- M42 front mount ----------
m42_mode           = "plain_bore"; // [plain_bore, plain_counterbore]
m42_major_d        = 42.0;   // M42x1 nominal major diameter
m42_bore_d         = 42.4;   // plain register bore (tap to M42x1, or bond adapter)
m42_depth          = front_plate_t;  // full plate depth
light_hole_d       = 26.0;   // clear light path behind the mount into the chamber

// ---------- Colours ----------
body_color = [0.32, 0.32, 0.34, 1.0];
seal_color = [0.02, 0.02, 0.02, 0.85];

module box_from_to(p0, p1) {
    translate([p0[0], p0[1], p0[2]])
        cube([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]);
}

// ---------- Main dark chamber ----------
module body_shell() {
    difference() {
        // outer solid
        box_from_to([-body_W / 2, 0, 0], [body_W / 2, body_len_y, body_H]);

        // hollow dark chamber (open at the rear, closed by the front plate)
        box_from_to([-inner_W / 2, -1, (body_H - inner_H) / 2],
                    [ inner_W / 2, body_len_y - front_plate_t, (body_H + inner_H) / 2]);

        // widen the rear opening to the full inner frame + seal rebate zone
        box_from_to([-inner_W / 2, -1, wall],
                    [ inner_W / 2, wall + 0.01, body_H - wall]);

        // light path through the front plate + M42 register bore
        translate([0, body_len_y - m42_depth - 0.01, body_H / 2])
            rotate([-90, 0, 0])
                cylinder(d = m42_bore_d, h = m42_depth + 0.02);
        translate([0, body_len_y - front_plate_t - 0.01, body_H / 2])
            rotate([-90, 0, 0])
                cylinder(d = light_hole_d, h = front_plate_t + 0.02);
    }

    // internal anti-reflection baffle rings (two shallow ribs)
    for (yb = [optical_len * 0.4, optical_len * 0.7])
        translate([0, yb, body_H / 2])
            rotate([-90, 0, 0])
                difference() {
                    cylinder(d = inner_W - 2, h = 1.2, center = true);
                    cylinder(d = light_hole_d + 6, h = 2, center = true);
                }
}

// ---------- Film-back lock features (PROVISIONAL - test fit) ----------
module lock_features() {
    // TOP hook: a downward lip on the body rear-top that drops over the film
    // back top hook rail. Rail projects +Y by hook_lip_d at the top.
    box_from_to([-bridge_w / 2 + 8, 0, body_H - hook_lip_h - 2.0],
                [ bridge_w / 2 - 8, hook_lip_d + 1.5, body_H]);
    box_from_to([-bridge_w / 2 + 8, hook_lip_d - 0.5, body_H - hook_lip_h - 6.0],
                [ bridge_w / 2 - 8, hook_lip_d + 1.5, body_H - hook_lip_h - 2.0]);

    // BOTTOM latch: a flexible hook that snaps under the film back 3mm pin.
    // Printed as a cantilever tab; tune thickness for snap force.
    difference() {
        box_from_to([-10, 0, 2.0], [10, latch_pin_y + latch_pin_d, 6.0]);
        translate([0, latch_pin_y, 4.0])
            rotate([0, 90, 0])
                cylinder(d = latch_pin_d + 0.4, h = 22, center = true);
    }
}

// ---------- Rear sealing flange face (velvet lands, not printed thick) ----------
module rear_seal_lands() {
    color(seal_color) {
        // perimeter lip around the rear opening for a velvet light seal
        difference() {
            box_from_to([-body_W / 2 + 3, 0, 3], [body_W / 2 - 3, 1.2, body_H - 3]);
            box_from_to([-inner_W / 2 - 2, -1, wall], [inner_W / 2 + 2, 2, body_H - wall]);
        }
    }
}

module simple_body() {
    color(body_color) {
        body_shell();
        lock_features();
    }
    rear_seal_lands();
}

// ---------- Optional printed viewfinder clip (holds bent-wire frame) ----------
module viewfinder_clip() {
    difference() {
        cube([14, 10, 6], center = true);
        translate([0, 0, 1]) cube([10, 12, 4], center = true);
        rotate([90, 0, 0]) cylinder(d = 1.3, h = 20, center = true); // wire hole
    }
}

if      (part == "body")           simple_body();
else if (part == "viewfinder_clip") viewfinder_clip();
else                               simple_body();
