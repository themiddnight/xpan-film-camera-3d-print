// X-Pan DIY Camera - M42 Pinhole Module v01  [STARTER]
// Units: millimeters
//
// An M42 front module that screws into the simple body. It holds a hand/
// laser-drilled 0.30mm brass pinhole shim and a sliding brass blade shutter.
//
// STATUS: printable STARTER. The brass pinhole plate and the shutter blade
// are NOT printed (per lens_design.md) - they are thin metal parts that drop
// into the printed seats here. The M42 male is modelled as a PLAIN spigot
// (see m42_mode) because printed threads need per-printer tuning; thread it,
// print a threaded ring, or bond an M42 male adapter to the spigot.

$fn = 120;

part = "cap"; // [cap, shutter_blade_template]

// ---------- Optical reference (from lens_design.md) ----------
pinhole_d          = 0.30;   // in the brass shim, NOT printed
pinhole_to_film    = 50.0;

// ---------- M42 male mount ----------
m42_mode           = "plain_spigot"; // [plain_spigot]
m42_major_d        = 42.0;
spigot_d           = 41.6;   // plain spigot; thread/adapt to M42x1
spigot_len         = 8.0;

// ---------- Cap body ----------
cap_d              = 50.0;
cap_t              = 4.0;    // front face thickness
light_bore_d       = 20.0;   // clearance behind the pinhole seat

// ---------- Pinhole seat (glue the brass shim here, centred) ----------
shim_seat_d        = 12.0;
shim_seat_depth    = 0.5;    // recess for a ~0.1mm brass shim + adhesive
printed_hole_d     = 2.0;    // oversized printed hole; brass shim carries the real 0.30mm

// ---------- Sliding blade shutter ----------
blade_t            = 0.5;    // brass/steel blade thickness
blade_slot_t       = blade_t + 0.4;   // channel clearance
blade_w            = 16.0;   // blade width (covers the aperture)
blade_travel       = 22.0;
retainer_t         = 1.2;    // printed cover strip that traps the blade

body_color = [0.20, 0.20, 0.22, 1.0];

module cap() {
    difference() {
        union() {
            // front cap disc
            cylinder(d = cap_d, h = cap_t);
            // M42 male spigot (rear)
            translate([0, 0, -spigot_len])
                cylinder(d = spigot_d, h = spigot_len + 0.01);
        }
        // through light path
        translate([0, 0, -spigot_len - 1])
            cylinder(d = light_bore_d, h = spigot_len + cap_t + 2);
        // brass-shim seat on the FRONT face, centred
        translate([0, 0, cap_t - shim_seat_depth])
            cylinder(d = shim_seat_d, h = shim_seat_depth + 0.1);
        // small printed aperture (brass shim provides the true 0.30mm hole)
        translate([0, 0, -1]) cylinder(d = printed_hole_d, h = cap_t + spigot_len + 2);

        // ---- sliding blade channel across the front face ----
        // a rectangular slot the blade slides through, above the shim seat
        translate([-blade_travel / 2, -blade_w / 2, cap_t - shim_seat_depth - blade_slot_t])
            cube([blade_travel + cap_d, blade_w, blade_slot_t]);
        // finger notch opening on one side
        translate([cap_d / 2 - 2, -4, cap_t - shim_seat_depth - blade_slot_t - 0.1])
            cube([8, 8, blade_slot_t + 0.2]);
    }

    // retainer strip that traps the blade in its channel (leaves aperture clear)
    color(body_color)
        difference() {
            translate([-blade_travel / 2, -blade_w / 2 - retainer_t, cap_t - shim_seat_depth - blade_slot_t - retainer_t])
                cube([blade_travel, blade_w + 2 * retainer_t, retainer_t]);
            translate([0, 0, -1]) cylinder(d = shim_seat_d + 2, h = cap_t + 4);
        }
}

// A flat template to cut the brass/steel shutter blade from sheet.
module shutter_blade_template() {
    linear_extrude(height = blade_t)
        union() {
            square([blade_travel + 6, blade_w], center = true);
            translate([blade_travel / 2 + 3, 0]) square([8, 6], center = true); // finger tab
        }
}

if      (part == "cap")                    color(body_color) cap();
else if (part == "shutter_blade_template") shutter_blade_template();
else                                       color(body_color) cap();
