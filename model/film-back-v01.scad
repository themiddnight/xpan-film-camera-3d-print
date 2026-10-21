// X-Pan DIY Camera - Film Back v01
// Units: millimeters
// Coordinate system:
//   X = film travel / camera width, left cartridge to right take-up
//   Y = rear-to-front depth, +Y is the body-interface/front side
//   Z = vertical height
//
// This is a parametric mechanism layout model, not a final print split.
// It keeps all key decisions visible for review before detailed part modeling.

$fn = 64;

// ---------- Global film parameters ----------
frame_w = 65.0;
frame_h = 24.0;
film_w = 35.0;
perf_pitch = 4.750;
perfs_per_frame = 14;
frame_advance = perf_pitch * perfs_per_frame;

// ---------- Film back envelope ----------
wall = 3.0;
inner_wall = 2.4;
body_h = 62.0;
bridge_w = 95.0;
supply_w = 42.0;
takeup_w = 58.0;
total_w = supply_w + bridge_w + takeup_w;
bridge_depth = 20.0;
chamber_depth = 54.0;
chamber_neck_front_gap = 0.0;
chamber_taper_back = 12.0;
front_chamber_solid_depth = 12.0;
rear_access_z_margin = wall + 1.0;
rear_gate_opening_margin_x = 2.0;
rear_gate_opening_margin_z = 9.0;

// X zone boundaries
x_bridge_l = -bridge_w / 2;
x_bridge_r = bridge_w / 2;
x_supply_l = x_bridge_l - supply_w;
x_takeup_r = x_bridge_r + takeup_w;

// Z layout
film_z = body_h / 2;
gate_z = film_z;
rail_w = 2.0;
rail_proud = 0.20;
film_channel_h = film_w + 3.0;
gate_corner_r = 1.0;
film_top_z = film_z + film_w / 2;
film_bottom_z = film_z - film_w / 2;
frame_top_z = gate_z + frame_h / 2;
frame_bottom_z = gate_z - frame_h / 2;
film_rebate_h = (film_w - frame_h) / 2;

// Y layout: lower Y is rear/loading side, higher Y is front/body side.
rear_face_y = 0;
front_bridge_y = bridge_depth;
front_chamber_y = chamber_depth;
film_plane_y = front_bridge_y - 4.2;
rear_gate_opening_y0 = rear_face_y - 0.5;
rear_opening_front_clearance = 0.6;
rear_gate_opening_y1 = film_plane_y + rear_opening_front_clearance;
gate_wall_t = 2.0;
dark_slide_slot_y = film_plane_y + 1.0;
dark_slide_slot_t = 1.3;
dark_slide_slot_w = 72.0;
rear_seal_lip_w = 1.3;
rear_seal_y0 = rear_face_y - 0.2;
rear_seal_y1 = rear_face_y + 0.25;
rear_cover_seal_x0 = x_supply_l + wall;
rear_cover_seal_x1 = x_takeup_r - wall;
rear_cover_seal_z0 = rear_access_z_margin;
rear_cover_seal_z1 = body_h - rear_access_z_margin;
rear_loading_opening_x0 = x_supply_l + wall;
rear_loading_opening_x1 = x_takeup_r - wall;
rear_loading_opening_y0 = rear_face_y - 0.5;
rear_loading_opening_y1 = film_plane_y + rear_opening_front_clearance;
rear_loading_opening_z0 = wall;
rear_loading_opening_z1 = body_h - wall;

// ---------- Film gate / rail details ----------
rail_x0 = x_bridge_l + 5.0;
rail_x1 = x_bridge_r + 28.0;
rail_rear_clearance_y = 0.02;
rail_depth = 1.15;
rail_y0 = film_plane_y + rail_rear_clearance_y;
rail_y1 = film_plane_y + rail_depth;
gate_frame_margin_x = 7.0;
gate_frame_margin_z = 1.5;
gate_frame_rear_clearance_y = 0.05;
gate_frame_depth = 1.30;
gate_frame_y0 = film_plane_y + gate_frame_rear_clearance_y;
gate_frame_y1 = film_plane_y + gate_frame_depth;
gate_cut_epsilon = 0.1;
side_guide_w = 3.0;
side_guide_clearance_x = 5.0;
left_side_guide_x0 = -frame_w / 2 - side_guide_clearance_x - side_guide_w;
left_side_guide_x1 = -frame_w / 2 - side_guide_clearance_x;
right_side_guide_x0 = frame_w / 2 + side_guide_clearance_x;
right_side_guide_x1 = frame_w / 2 + side_guide_clearance_x + side_guide_w;
film_edge_fence_w = 1.6;
film_edge_fence_gap_z = 0.8;
upper_fence_z0 = film_top_z + film_edge_fence_gap_z;
upper_fence_z1 = upper_fence_z0 + film_edge_fence_w;
lower_fence_z1 = film_bottom_z - film_edge_fence_gap_z;
lower_fence_z0 = lower_fence_z1 - film_edge_fence_w;
aperture_outline_y = gate_frame_y1 + 0.15;

// ---------- Film transport ----------
cartridge_d = 31.0;
cartridge_clearance_d = 33.0;
cartridge_center_x = x_supply_l + supply_w / 2;
cartridge_front_clearance = 1.0;
cartridge_center_y = front_chamber_y
                   - front_chamber_solid_depth
                   - cartridge_clearance_d / 2
                   - cartridge_front_clearance;
cartridge_center_z = film_z;

rewind_knob_d = 20.0;
rewind_knob_h = 8.0;

sprocket_teeth = 14;
sprocket_pitch_d = frame_advance / PI;
sprocket_body_d = 20.2;
sprocket_tooth_len = 1.4;     // along film travel tangent
sprocket_tooth_h = 1.2;       // along film height
sprocket_tooth_engage = 0.9;  // radial projection into perf row
sprocket_h = 13.0;
sprocket_shaft_d = 4.0;
sprocket_center_x = x_bridge_r + 14.0;
sprocket_center_y = film_plane_y + 7.0;
sprocket_center_z = film_z - film_w / 2 + 4.0;
sprocket_clearance_d = sprocket_body_d + 5.0;
sprocket_clearance_h = sprocket_h + 5.0;
sprocket_shaft_bottom_z = sprocket_center_z - sprocket_h / 2 - 1.0;
sprocket_shaft_top_z = body_h + 0.5;

cam_d = 17.0;
cam_h = 3.0;
cam_z = body_h - 12.0;
cam_notch_w = 2.4;
cam_notch_depth = 2.0;

takeup_core_d = 15.0;
takeup_max_d = 24.0;
takeup_h = 38.0;
takeup_center_x = x_bridge_r + 39.0;
takeup_center_y = 32.0;
takeup_center_z = film_z;
advance_knob_d = 26.0;
advance_knob_h = 9.0;
takeup_clearance_d = takeup_max_d + 6.0;

film_preview_t = 0.22;
film_preview_y1 = film_plane_y - 0.04;
film_preview_y0 = film_preview_y1 - film_preview_t;
film_exit_from_cartridge_x = cartridge_center_x + cartridge_d / 2 - 1.0;
film_straight_x0 = film_exit_from_cartridge_x;
film_straight_x1 = sprocket_center_x + sprocket_body_d / 2 + 4.0;
rear_film_path_opening_x0 = film_straight_x0 - 1.0;
rear_film_path_opening_x1 = film_straight_x1 + 1.0;
rear_film_path_opening_y0 = rear_face_y - 0.5;
rear_film_path_opening_y1 = film_plane_y + 0.35;
rear_film_path_opening_z0 = film_bottom_z - 1.5;
rear_film_path_opening_z1 = film_top_z + 1.5;
film_lead_to_takeup_len = 42.0;
film_lead_to_takeup_angle = 21.0;
film_lead_to_takeup_x = sprocket_center_x + 15.0;
film_lead_to_takeup_y = film_plane_y + 7.0;
cartridge_throat_x0 = film_exit_from_cartridge_x - 2.0;
cartridge_throat_x1 = x_bridge_l + 6.0;
cartridge_throat_y0 = film_preview_y0 - 0.4;
cartridge_throat_y1 = film_plane_y + 2.0;
film_throat_clearance_z = 1.0;
throat_seal_h = 1.8;
throat_seal_gap_z = 0.4;
sprocket_strip_x0 = sprocket_center_x - sprocket_body_d / 2 - 3.0;
sprocket_strip_x1 = sprocket_center_x + sprocket_body_d / 2 + 3.0;
sprocket_strip_y0 = film_preview_y0 - 0.2;
sprocket_strip_y1 = sprocket_center_y + sprocket_body_d / 2 + 2.0;
sprocket_strip_clearance_z = 2.0;
sprocket_guide_t = 1.2;
takeup_leader_guide_t = 1.4;
takeup_leader_guide_w = 2.0;

release_button_w = 9.0;
release_button_d = 7.0;
release_button_h = 4.0;
release_button_x = sprocket_center_x - 13.0;
release_button_y = sprocket_center_y;
release_plunger_d = 3.0;
release_plunger_clearance_d = 3.6;
release_boss_w = 12.0;
release_boss_d = 9.5;
release_boss_h = 2.4;
release_button_z = body_h + release_boss_h + 0.25;

// ---------- Rear cover preview ----------
door_t = 3.0;
door_gap = 1.0;
door_y = rear_face_y - door_gap - door_t;
door_hinge_d = 3.0;
foam_t = 2.0;
pressure_pad_t = 2.0;
pressure_pad_y = door_y + door_t + 0.2;
door_lip_t = 2.0;
rear_cover_preview_offset_x = total_w + 22.0;
rear_cover_preview_offset_y = 0.0;
rear_cover_preview_offset_z = 0.0;
rear_cover_x0 = x_supply_l + 2.0;
rear_cover_x1 = x_takeup_r - 2.0;

// ---------- Body module interface ----------
hook_lip_h = 4.0;
hook_lip_d = 5.0;
latch_pin_d = 3.0;
latch_pin_len = 78.0;

// ---------- Display toggles ----------
show_shell = true;
show_transport = true;
show_rear_covers_preview = true;
show_body_interface = true;
show_dark_slide_preview = false;
show_cutaway_film = true;

film_color = [0.82, 0.02, 0.40, 1.0];
body_color = [0.44, 0.44, 0.40, 1.0];
rail_color = [0.02, 0.28, 0.08, 1.0];
slide_color = [0.0, 0.55, 0.15, 0.55];
sprocket_color = [1.0, 0.76, 0.0, 1.0];
takeup_color = [1.0, 0.55, 0.0, 1.0];
cartridge_color = [0.0, 0.55, 1.0, 1.0];
hardware_color = [0.65, 0.65, 0.65, 1.0];
foam_color = [0.2, 0.8, 0.75, 0.55];
seal_color = [0.02, 0.02, 0.02, 0.75];
cover_color = [0.26, 0.26, 0.25, 0.96];

// ---------- Helpers ----------
module rounded_box(size, r = 2, center = false) {
    // 2D-rounded box extruded along Z.
    sx = size[0];
    sy = size[1];
    sz = size[2];
    translate(center ? [-sx / 2, -sy / 2, -sz / 2] : [0, 0, 0])
        linear_extrude(height = sz)
            offset(r = r)
                square([sx - 2 * r, sy - 2 * r], center = true);
}

module box_from_to(p0, p1) {
    translate([p0[0], p0[1], p0[2]])
        cube([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]);
}

module cyl_z(d, h, center = true) {
    cylinder(d = d, h = h, center = center);
}

module cyl_x(d, h, center = true) {
    rotate([0, 90, 0])
        cylinder(d = d, h = h, center = center);
}

module cyl_y(d, h, center = true) {
    rotate([90, 0, 0])
        cylinder(d = d, h = h, center = center);
}

module screw_boss(x, y, z, od = 8.0, id = 3.2, h = 8.0) {
    difference() {
        translate([x, y, z])
            cyl_z(od, h);
        translate([x, y, z])
            cyl_z(id, h + 0.4);
    }
}

module prism_xy(points, h) {
    linear_extrude(height = h)
        polygon(points = points);
}

module prism_xy_from_z(points, z0, z1) {
    translate([0, 0, z0])
        prism_xy(points, z1 - z0);
}

module supply_rear_access_void(z0 = rear_access_z_margin,
                               z1 = body_h - rear_access_z_margin) {
    prism_xy_from_z([
        [x_supply_l + wall, rear_face_y - 0.5],
        [x_bridge_l - wall, rear_face_y - 0.5],
        [x_bridge_l - wall, front_bridge_y],
        [x_bridge_l - chamber_taper_back - wall,
         front_chamber_y - front_chamber_solid_depth],
        [x_supply_l + wall, front_chamber_y - front_chamber_solid_depth]
    ], z0, z1);
}

module takeup_rear_access_void(z0 = rear_access_z_margin,
                               z1 = body_h - rear_access_z_margin) {
    prism_xy_from_z([
        [x_bridge_r + wall, rear_face_y - 0.5],
        [x_takeup_r - wall, rear_face_y - 0.5],
        [x_takeup_r - wall, front_chamber_y - front_chamber_solid_depth],
        [x_bridge_r + chamber_taper_back + wall,
         front_chamber_y - front_chamber_solid_depth],
        [x_bridge_r + wall, front_bridge_y]
    ], z0, z1);
}

// ---------- Main shell ----------
module chamber_outer_shapes() {
    // Center bridge: thin body-interface datum.
    // This is intentionally a long shallow bridge, not a full-depth rectangle.
    box_from_to([x_bridge_l, rear_face_y, 0], [x_bridge_r, front_bridge_y, body_h]);

    // Supply chamber pod, tapered into the bridge like the rough top-view sketch.
    prism_xy([
        [x_supply_l, rear_face_y],
        [x_bridge_l - chamber_neck_front_gap, rear_face_y],
        [x_bridge_l, front_bridge_y],
        [x_bridge_l - chamber_taper_back, front_chamber_y],
        [x_supply_l, front_chamber_y]
    ], body_h);

    // Take-up chamber pod, tapered into the bridge like the rough top-view sketch.
    prism_xy([
        [x_bridge_r + chamber_neck_front_gap, rear_face_y],
        [x_takeup_r, rear_face_y],
        [x_takeup_r, front_chamber_y],
        [x_bridge_r + chamber_taper_back, front_chamber_y],
        [x_bridge_r, front_bridge_y]
    ], body_h);
}

module chamber_inner_voids() {
    // Left chamber relief for 135 cartridge and hand loading.
    translate([cartridge_center_x, cartridge_center_y, cartridge_center_z])
        cyl_z(cartridge_clearance_d, body_h - 2 * wall);

    // Rear access follows the tapered chamber wall. A rectangular cut here
    // would slice through the sloped neck and leave visible side holes.
    supply_rear_access_void();

    // Right chamber access and reliefs for sprocket and take-up spool.
    takeup_rear_access_void();
    translate([takeup_center_x, takeup_center_y, takeup_center_z])
        cyl_z(takeup_clearance_d, body_h - 2 * wall);
    translate([sprocket_center_x, sprocket_center_y, sprocket_center_z])
        cyl_z(sprocket_clearance_d, sprocket_clearance_h);

    // Film channel through center bridge.
    box_from_to([x_bridge_l - 1, film_plane_y - 0.6, film_z - film_channel_h / 2],
                [x_bridge_r + 1, film_plane_y + 1.2, film_z + film_channel_h / 2]);
    box_from_to([cartridge_throat_x0, cartridge_throat_y0, film_bottom_z - film_throat_clearance_z],
                [cartridge_throat_x1, cartridge_throat_y1, film_top_z + film_throat_clearance_z]);
    box_from_to([sprocket_strip_x0, sprocket_strip_y0, sprocket_center_z - sprocket_h / 2 - sprocket_strip_clearance_z],
                [sprocket_strip_x1, sprocket_strip_y1, sprocket_center_z + sprocket_h / 2 + sprocket_strip_clearance_z]);

    // One large rear loading mouth under the single rear cover. This keeps
    // the -Y side open across cartridge, gate, sprocket, and take-up so the
    // loaded 35mm strip is not hidden by internal rear walls.
    box_from_to([rear_loading_opening_x0,
                 rear_loading_opening_y0,
                 rear_loading_opening_z0],
                [rear_loading_opening_x1,
                 rear_loading_opening_y1,
                 rear_loading_opening_z1]);

    // Continuous open-back film lane. This removes internal rear posts in
    // the loaded film band so the film reads as one uninterrupted strip.
    box_from_to([rear_film_path_opening_x0,
                 rear_film_path_opening_y0,
                 rear_film_path_opening_z0],
                [rear_film_path_opening_x1,
                 rear_film_path_opening_y1,
                 rear_film_path_opening_z1]);

    // Rear service opening behind the gate. With the rear cover open,
    // the loaded film strip must be visible and reachable from the back.
    box_from_to([x_bridge_l + rear_gate_opening_margin_x,
                 rear_gate_opening_y0,
                 gate_z - film_w / 2 - rear_gate_opening_margin_z],
                [x_bridge_r - rear_gate_opening_margin_x,
                 rear_gate_opening_y1,
                 gate_z + film_w / 2 + rear_gate_opening_margin_z]);

    // Exact 65 x 24 frame aperture through the front gate datum.
    box_from_to([-frame_w / 2, film_plane_y - 1.4, frame_bottom_z],
                [frame_w / 2, front_bridge_y + 1.0, frame_top_z]);

    // Dark slide top-down slot.
    box_from_to([-dark_slide_slot_w / 2, dark_slide_slot_y, body_h - 1],
                [dark_slide_slot_w / 2, dark_slide_slot_y + dark_slide_slot_t, body_h + 9]);
    box_from_to([-dark_slide_slot_w / 2, dark_slide_slot_y, gate_z - film_w / 2 - 2],
                [dark_slide_slot_w / 2, dark_slide_slot_y + dark_slide_slot_t, body_h + 1]);

    // Shaft openings.
    translate([cartridge_center_x, cartridge_center_y, body_h - 1])
        cyl_z(5.0, 18);
    translate([takeup_center_x, takeup_center_y, body_h - 1])
        cyl_z(5.0, 18);
    translate([sprocket_center_x, sprocket_center_y, body_h - 1])
        cyl_z(5.0, 24);
    translate([release_button_x, release_button_y, body_h - 1])
        cyl_z(release_plunger_clearance_d, 14);
}

module film_back_shell() {
    color(body_color)
        difference() {
            chamber_outer_shapes();
            chamber_inner_voids();
        }
}

module shaft_seal_bosses() {
    color(body_color) {
        translate([cartridge_center_x, cartridge_center_y, body_h + 1.5])
            difference() {
                cyl_z(13.0, 3.0);
                cyl_z(5.2, 3.5);
            }
        translate([takeup_center_x, takeup_center_y, body_h + 1.5])
            difference() {
                cyl_z(13.0, 3.0);
                cyl_z(5.2, 3.5);
            }
        translate([sprocket_center_x, sprocket_center_y, body_h + 1.5])
            difference() {
                cyl_z(11.0, 3.0);
                cyl_z(5.2, 3.5);
            }
        difference() {
            translate([release_button_x - release_boss_w / 2,
                       release_button_y - release_boss_d / 2,
                       body_h])
                cube([release_boss_w, release_boss_d, release_boss_h]);
            translate([release_button_x,
                       release_button_y,
                       body_h + release_boss_h / 2])
                cyl_z(release_plunger_clearance_d, release_boss_h + 0.4);
        }
    }
}

module rear_opening_seals() {
    color(seal_color) {
        // One-piece rear cover seal. Keep seals around the outside only;
        // internal posts would block the open-back loading view.
        box_from_to([rear_cover_seal_x0,
                     rear_seal_y0,
                     rear_cover_seal_z0],
                    [rear_cover_seal_x1,
                     rear_seal_y1,
                     rear_cover_seal_z0 + rear_seal_lip_w]);
        box_from_to([rear_cover_seal_x0,
                     rear_seal_y0,
                     rear_cover_seal_z1 - rear_seal_lip_w],
                    [rear_cover_seal_x1,
                     rear_seal_y1,
                     rear_cover_seal_z1]);
        box_from_to([rear_cover_seal_x0,
                     rear_seal_y0,
                     rear_cover_seal_z0],
                    [rear_cover_seal_x0 + rear_seal_lip_w,
                     rear_seal_y1,
                     rear_cover_seal_z1]);
        box_from_to([rear_cover_seal_x1 - rear_seal_lip_w,
                     rear_seal_y0,
                     rear_cover_seal_z0],
                    [rear_cover_seal_x1,
                     rear_seal_y1,
                     rear_cover_seal_z1]);
    }
}

// ---------- Gate / rails / datum ----------
module film_gate_and_rails() {
    // Printed front gate frame around the exact aperture. It sits on the +Y
    // side of the film so it does not hide the loaded strip from the open back.
    color(body_color)
        difference() {
            box_from_to([-frame_w / 2 - gate_frame_margin_x,
                         gate_frame_y0,
                         frame_bottom_z - gate_frame_margin_z],
                        [frame_w / 2 + gate_frame_margin_x,
                         gate_frame_y1,
                         frame_top_z + gate_frame_margin_z]);
            box_from_to([-frame_w / 2,
                         gate_frame_y0 - gate_cut_epsilon,
                         frame_bottom_z],
                        [frame_w / 2,
                         gate_frame_y1 + gate_cut_epsilon,
                         frame_top_z]);
        }

    color(rail_color) {
        // Top and bottom raised rails sit just in front of the loaded film plane.
        box_from_to([rail_x0, rail_y0, frame_top_z],
                    [rail_x1, rail_y1, frame_top_z + rail_w]);
        box_from_to([rail_x0, rail_y0, frame_bottom_z - rail_w],
                    [rail_x1, rail_y1, frame_bottom_z]);

        // Side guide pads, kept outside the exposed frame.
        box_from_to([left_side_guide_x0, rail_y0, frame_bottom_z],
                    [left_side_guide_x1, rail_y1, frame_top_z]);
        box_from_to([right_side_guide_x0, rail_y0, frame_bottom_z],
                    [right_side_guide_x1, rail_y1, frame_top_z]);

        // Shallow lane fences outside the 35mm film edges, only for lateral control.
        box_from_to([rail_x0, rail_y0, upper_fence_z0],
                    [rail_x1, rail_y1, upper_fence_z1]);
        box_from_to([rail_x0, rail_y0, lower_fence_z0],
                    [rail_x1, rail_y1, lower_fence_z1]);
    }

    // Red 65 x 24 aperture outline for design review, not a printed feature.
    // It is drawn on the +Y/front body-interface face.
    color([1, 0, 0, 0.95])
        translate([0, aperture_outline_y, gate_z])
            rotate([90, 0, 0])
                linear_extrude(height = 0.5)
                    difference() {
                        offset(r = gate_corner_r)
                            square([frame_w, frame_h], center = true);
                        offset(r = gate_corner_r)
                            square([frame_w - 2.0, frame_h - 2.0], center = true);
                    }
}

module dark_slide_preview() {
    color(slide_color)
        box_from_to([-dark_slide_slot_w / 2, dark_slide_slot_y + 0.08, gate_z - film_w / 2 - 1.0],
                    [dark_slide_slot_w / 2, dark_slide_slot_y + 1.08, body_h + 18.0]);
}

module film_preview() {
    color(film_color)
        union() {
            // Straight run across cartridge exit, gate, and sprocket.
            box_from_to([film_straight_x0, film_preview_y0, film_bottom_z],
                        [film_straight_x1, film_preview_y1, film_top_z]);

            // Angled lead from sprocket toward take-up spool.
            translate([film_lead_to_takeup_x, film_lead_to_takeup_y, film_z])
                rotate([0, 0, film_lead_to_takeup_angle])
                    cube([film_lead_to_takeup_len, film_preview_t, film_w], center = true);
        }
}

module film_transport_guides() {
    color(seal_color) {
        // Felt/velvet cartridge throat, shown as two soft seal lands.
        box_from_to([cartridge_throat_x0,
                     cartridge_throat_y0,
                     film_top_z + throat_seal_gap_z],
                    [cartridge_throat_x1,
                     cartridge_throat_y1,
                     film_top_z + throat_seal_gap_z + throat_seal_h]);
        box_from_to([cartridge_throat_x0,
                     cartridge_throat_y0,
                     film_bottom_z - throat_seal_gap_z - throat_seal_h],
                    [cartridge_throat_x1,
                     cartridge_throat_y1,
                     film_bottom_z - throat_seal_gap_z]);
    }

    color(rail_color) {
        // Lower perf-row guide around the sprocket so the film stays engaged.
        box_from_to([sprocket_strip_x0,
                     rail_y0,
                     sprocket_center_z - sprocket_h / 2 - sprocket_guide_t],
                    [sprocket_strip_x1,
                     rail_y1,
                     sprocket_center_z - sprocket_h / 2]);
        box_from_to([sprocket_strip_x0,
                     rail_y0,
                     sprocket_center_z + sprocket_h / 2],
                    [sprocket_strip_x1,
                     rail_y1,
                     sprocket_center_z + sprocket_h / 2 + sprocket_guide_t]);

        // Simple leader guide pointing from sprocket toward the take-up spool.
        // Keep it centered on the leader so it does not protrude through the
        // outer +X wall in the review model.
        translate([film_lead_to_takeup_x,
                   film_lead_to_takeup_y - takeup_leader_guide_w / 2,
                   film_bottom_z - takeup_leader_guide_t / 2])
            rotate([0, 0, film_lead_to_takeup_angle])
                cube([film_lead_to_takeup_len, takeup_leader_guide_w, takeup_leader_guide_t], center = true);
    }
}

// ---------- Cartridge / rewind ----------
module cartridge_mockup() {
    color(cartridge_color)
        intersection() {
            union() {
                translate([cartridge_center_x, cartridge_center_y, cartridge_center_z])
                    cyl_z(cartridge_d, body_h - 12);
                translate([cartridge_center_x, cartridge_center_y, cartridge_center_z])
                    cyl_z(13.0, body_h - 8);
            }
            // Keep the blue cartridge preview inside the actual chamber void
            // so it cannot visually poke through closed shell surfaces.
            supply_rear_access_void();
        }

    color(hardware_color) {
        translate([cartridge_center_x, cartridge_center_y, body_h + rewind_knob_h / 2])
            cyl_z(rewind_knob_d, rewind_knob_h);
        translate([cartridge_center_x, cartridge_center_y, body_h / 2])
            cyl_z(4.0, body_h + rewind_knob_h + 2);
    }
}

// ---------- Sprocket / auto-lock ----------
module sprocket_tooth(i) {
    angle = i * 360 / sprocket_teeth;
    rotate([0, 0, angle])
        translate([sprocket_body_d / 2 + sprocket_tooth_engage / 2, 0, 0])
            cube([sprocket_tooth_engage, sprocket_tooth_len, sprocket_tooth_h], center = true);
}

module sprocket_wheel() {
    color(sprocket_color)
        translate([sprocket_center_x, sprocket_center_y, sprocket_center_z])
            difference() {
                union() {
                    cyl_z(sprocket_body_d, sprocket_h);
                    for (i = [0 : sprocket_teeth - 1])
                        sprocket_tooth(i);
                }
                cyl_z(sprocket_shaft_d, sprocket_h + 1);
            }
}

module cam_disc() {
    color([0.85, 0.85, 0.85, 1])
        translate([sprocket_center_x, sprocket_center_y, cam_z])
            difference() {
                cyl_z(cam_d, cam_h);
                translate([cam_d / 2 - cam_notch_depth / 2, 0, 0])
                    cube([cam_notch_depth + 0.4, cam_notch_w, cam_h + 0.5], center = true);
                cyl_z(sprocket_shaft_d, cam_h + 0.5);
            }

    // visual index dot
    color([1, 0, 0, 1])
        translate([sprocket_center_x + cam_d / 2 - 2.2, sprocket_center_y, cam_z + cam_h / 2 + 0.4])
            cyl_z(2.2, 0.8);
}

module release_button_and_pawl() {
    color([0.2, 0.2, 0.2, 1])
        translate([release_button_x - release_button_w / 2, release_button_y - release_button_d / 2, release_button_z])
            cube([release_button_w, release_button_d, release_button_h]);

    // Pawl lever is inside the take-up chamber, under the top cover.
    color([0.8, 0.1, 0.45, 1]) {
        box_from_to([sprocket_center_x - 20, sprocket_center_y - 2, cam_z + 3.5],
                    [sprocket_center_x + 5, sprocket_center_y + 2, cam_z + 6.5]);
        translate([sprocket_center_x + cam_d / 2 - 1.7, sprocket_center_y, cam_z + 0.7])
            rotate([0, 0, 45])
                cube([2.0, 4.0, 6.0], center = true);
    }

    color(hardware_color)
        translate([release_button_x, release_button_y, (cam_z + release_button_z) / 2])
            cyl_z(release_plunger_d, release_button_z - cam_z + 0.6);
}

module sprocket_lock_assembly() {
    sprocket_wheel();
    color(hardware_color)
        translate([sprocket_center_x,
                   sprocket_center_y,
                   (sprocket_shaft_bottom_z + sprocket_shaft_top_z) / 2])
            cyl_z(sprocket_shaft_d,
                  sprocket_shaft_top_z - sprocket_shaft_bottom_z);
    cam_disc();
    release_button_and_pawl();
}

// ---------- Take-up / advance ----------
module takeup_spool() {
    color(takeup_color) {
        translate([takeup_center_x, takeup_center_y, takeup_center_z])
            cyl_z(takeup_core_d, takeup_h);
        translate([takeup_center_x, takeup_center_y, takeup_center_z + takeup_h / 2 - 2])
            cyl_z(takeup_max_d, 4);
        translate([takeup_center_x, takeup_center_y, takeup_center_z - takeup_h / 2 + 2])
            cyl_z(takeup_max_d, 4);

        // Film leader slot.
        translate([takeup_center_x - 1, takeup_center_y - takeup_core_d / 2 - 0.1, takeup_center_z])
            cube([2, 2, takeup_h - 9], center = true);
    }

    color(hardware_color) {
        translate([takeup_center_x, takeup_center_y, body_h + advance_knob_h / 2])
            cyl_z(advance_knob_d, advance_knob_h);
        translate([takeup_center_x, takeup_center_y, body_h / 2])
            cyl_z(4.0, body_h + advance_knob_h + 2);
    }
}

// ---------- Rear covers / pressure pad preview ----------
module rear_covers_preview() {
    translate([rear_cover_preview_offset_x, rear_cover_preview_offset_y, rear_cover_preview_offset_z]) {
        // One-piece rear cover preview. It is placed beside the film back so
        // it does not hide the rear loading openings.
        color(cover_color) {
            box_from_to([rear_cover_x0, door_y, 3],
                        [rear_cover_x1, door_y + door_t, body_h - 3]);
        }

        // Continuous overlap lip for velvet/felt sealing.
        color(seal_color) {
            box_from_to([rear_cover_x0 + 5, door_y - door_lip_t, 6],
                        [rear_cover_x1 - 5, door_y, 9]);
            box_from_to([rear_cover_x0 + 5, door_y - door_lip_t, body_h - 9],
                        [rear_cover_x1 - 5, door_y, body_h - 6]);
            box_from_to([rear_cover_x0 + 5, door_y - door_lip_t, 6],
                        [rear_cover_x0 + 8, door_y, body_h - 6]);
            box_from_to([rear_cover_x1 - 8, door_y - door_lip_t, 6],
                        [rear_cover_x1 - 5, door_y, body_h - 6]);
        }

        // One continuous hand-cut foam pad on the inside of the rear cover.
        color(foam_color) {
            box_from_to([x_bridge_l + 7, pressure_pad_y, film_z - film_w / 2 - 1.0],
                        [sprocket_center_x + 10, pressure_pad_y + pressure_pad_t, film_z + film_w / 2 + 1.0]);
        }

        // Relief cut drawn as a darker patch where sprocket teeth need clearance.
        color([0.05, 0.05, 0.05, 0.65])
            translate([sprocket_center_x, pressure_pad_y + pressure_pad_t + 0.05, sprocket_center_z])
                cyl_y(sprocket_body_d + 5.0, 0.4);

        // Single bottom hinge rod for the one-piece cover.
        color(hardware_color) {
            translate([0, door_y + door_t + 1.0, 4.5])
                cyl_x(door_hinge_d, rear_cover_x1 - rear_cover_x0 - 12);
        }
    }
}

// ---------- Body module lock / interface ----------
module body_interface_features() {
    color(body_color) {
        // Top receiving hook rail.
        box_from_to([x_bridge_l + 5, front_bridge_y, body_h - hook_lip_h],
                    [x_bridge_r - 5, front_bridge_y + hook_lip_d, body_h]);
        box_from_to([x_bridge_l + 5, front_bridge_y + hook_lip_d - 2.0, body_h - hook_lip_h - 2.0],
                    [x_bridge_r - 5, front_bridge_y + hook_lip_d, body_h - hook_lip_h]);
    }

    // Bottom latch pin.
    color(hardware_color)
        translate([0, front_bridge_y + 4.0, 8.0])
            cyl_x(latch_pin_d, latch_pin_len);
}

// ---------- Assembly ----------
module film_back_v01() {
    if (show_shell) {
        film_back_shell();
        rear_opening_seals();
    }
    shaft_seal_bosses();

    film_gate_and_rails();
    film_transport_guides();

    if (show_dark_slide_preview)
        dark_slide_preview();

    if (show_cutaway_film)
        film_preview();

    if (show_transport) {
        cartridge_mockup();
        sprocket_lock_assembly();
        takeup_spool();
    }

    if (show_rear_covers_preview)
        rear_covers_preview();

    if (show_body_interface)
        body_interface_features();
}

film_back_v01();
