// Marker cube mount for a GE ultrasound probe: C-clip or screw clamp + stalk + marker cube, one part.
// Parametric starter for the 3D print. Units: mm. Open in OpenSCAD (free, openscad.org), press F6, export STL.
//
// Layout: the probe axis is Z (probe face at the bottom, cable out of the top). -Y is the FRONT of the handle
// (button side on the L4-12t-RS), +Y is the BACK where the cable drapes towards the operator's wrist.
// The stalk leans FORWARD (-Y), so the cube hangs over the patient in front of the hand, clear of the cable,
// the wrist and the forearm. The phone sits on the far side of the patient looking back at 45 degrees.
// With stalk_len 60 and stalk_lean 25 the cube stays about 74 mm above a flat surface when the probe is
// tilted 45 degrees towards it, and about 24 mm at 60 degrees. A more upright stalk gives more clearance;
// a longer stalk does not (the cube moves forward as fast as it moves up).
//
// EDIT THE HANDLE NUMBERS FIRST. The defaults are estimates read off a photo of the C1-5 next to a 35 mm
// marker (2026-10-30 session), about +-3 mm. Measure the real probe at the clip zone (100-130 mm above the
// probe face) with calipers before printing: width (across the array), thickness, and roughly how round the
// corners are. The L4-12t-RS has buttons on the handle: the clip must sit above them.
//
// Project: ultrasound completeness coach, AWSOM (Ben Zheng, Vahdeta Suljic, Sally Lin, Ashleigh Lacey; MS2).
// Why the shape is what it is: see the print sketch (MARKER_CUBE_PRINT_SKETCH.pdf) and the brief.

$fn = 72;

// ---------------- probe handle (MEASURE) ----------------
probe        = "C1-5";  // label only, embossed on the clip
handle_w     = 42;      // handle width at the clip zone   [ESTIMATE from photo, measure]
handle_t     = 27;      // handle thickness at the clip zone [ESTIMATE from photo, measure]
handle_r     = 9;       // corner radius of the handle cross-section (bigger = more oval)
foam         = 1.0;     // gap on every side for 1 mm foam tape (protects the probe, takes up tolerance)

// ---------------- clip ----------------
clamp        = "screw"; // "screw" = two halves joined by two M3 screws (recommended), "snap" = flexible C-clip
clip_wall    = 3;       // wall thickness
clip_h       = 20;      // clip height along the probe axis
clip_open    = handle_w - 8;  // snap mode only: opening on the BACK (cable) side, since the stalk root takes the front.
                              // Must be close to the handle width or the walls cannot flex enough; handle minus 8 mm
                              // is already a firm snap.
screw_d      = 3.4;     // M3 clearance hole
nut_af       = 5.5;     // M3 nut across flats
head_d       = 6.2;     // M3 socket head
boss_w       = 9;       // screw boss width (sticks out on both sides of the clip)

// ---------------- stalk ----------------
stalk_len    = 60;      // 50-80; shorter means less lever arm between cube and probe tip
stalk_d      = 12;      // round stalk; 12 mm PLA is stiff enough
stalk_lean   = 25;      // degrees FORWARD (over the patient), away from the cable and the operator; 20-30

// ---------------- cube ----------------
cube_e       = 60;      // cube edge (55-60 ok)
recess       = 52;      // square recess for the 51 mm sticker (35 mm marker + 8 mm white border)
recess_depth = 0.5;
label_size   = 3;       // face numbers 1-5
label_h      = 0.4;     // emboss height
// The cube is modelled solid: let the slicer hollow it (10-15 % infill, 4+ top/bottom layers, 3 perimeters).

// ---------------- derived ----------------
outer_w = handle_w + 2 * (foam + clip_wall);
outer_t = handle_t + 2 * (foam + clip_wall);
P0 = [0, -(outer_t / 2 + 3), clip_h - 2];                                   // stalk root, on the FRONT of the clip
P1 = P0 + stalk_len * [0, -sin(stalk_lean), cos(stalk_lean)];              // stalk top = centre of the cube's bottom face

module rrect(w, t, r) { offset(r = r) offset(delta = -r) square([w, t], center = true); }

// ---------------- clip ----------------
module clip_ring() { linear_extrude(clip_h) rrect(outer_w, outer_t, handle_r + foam + clip_wall); }

module stalk_root() { translate([-9, -(outer_t / 2 + 5), 0]) cube([18, 7, clip_h]); }   // block on the front wall

module screw_bosses() {
    for (s = [-1, 1])
        translate([s * (outer_w / 2 + boss_w / 2 - 1.5), 0, clip_h / 2])
            difference() {
                cube([boss_w + 3, outer_t, clip_h], center = true);
                rotate([90, 0, 0]) cylinder(d = screw_d, h = outer_t + 2, center = true);        // through hole along Y
                translate([0, outer_t / 2 - 2.5, 0]) rotate([90, 0, 0])                           // nut pocket, back half
                    cylinder(d = nut_af / cos(30), h = 5.2, center = true, $fn = 6);
                translate([0, -(outer_t / 2 - 2), 0]) rotate([90, 0, 0])                         // head recess, front half
                    cylinder(d = head_d, h = 4.2, center = true);
            }
}

module probe_label() {
    // on the front face of the stalk root, embossed outwards, readable from the camera side
    translate([0, -(outer_t / 2 + 5), clip_h / 2]) rotate([90, 0, 0])
        linear_extrude(label_h) text(probe, size = 4, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
}

module clip() {
    difference() {
        union() {
            clip_ring();
            stalk_root();
            if (clamp == "screw") screw_bosses();
        }
        // bore for the handle + foam
        translate([0, 0, -1]) linear_extrude(clip_h + 2) rrect(handle_w + 2 * foam, handle_t + 2 * foam, handle_r + foam);
        if (clamp == "snap")   // opening on the back (cable side, +Y); the front carries the stalk
            translate([-clip_open / 2, outer_t / 2 - clip_wall - 1, -1]) cube([clip_open, clip_wall + 2, clip_h + 2]);
        if (clamp == "screw")  // split into a front half and a back half (gap 0.8 mm so the screws can squeeze)
            translate([-(outer_w / 2 + boss_w + 3), -0.4, -1]) cube([outer_w + 2 * boss_w + 6, 0.8, clip_h + 2]);
    }
}

// ---------------- stalk ----------------
module stalk() {
    translate(P0) sphere(d = stalk_d);
    translate(P0) rotate([stalk_lean, 0, 0]) cylinder(d = stalk_d, h = stalk_len);     // +X rotation tips +Z towards -Y (forward)
    translate(P1 - [0, 0, 6]) cylinder(d = 22, h = 6.01);      // boss under the cube
}

// ---------------- marker cube ----------------
// faces: [number, rotation that carries the +Z face onto this face, pre-rotation about Z so "up" is up]
// 1 = top, 2 = front (-Y, towards the camera), 3 = right (+X), 4 = back (+Y, cable side), 5 = left (-X). Bottom: stalk.
faces = [[1, [0, 0, 0], 0], [2, [90, 0, 0], 0], [3, [0, 90, 0], 90], [4, [-90, 0, 0], 180], [5, [0, -90, 0], -90]];

module on_face(f) { rotate(f[1]) rotate([0, 0, f[2]]) children(); }

module pocket() { translate([-recess / 2, -recess / 2, cube_e / 2 - recess_depth]) cube([recess, recess, recess_depth + 1]); }

module face_labels(n) {
    rim_y = (cube_e / 2 + recess / 2) / 2;           // middle of the 4 mm rim along the top edge of the face
    translate([-(cube_e / 2) + 6, rim_y, cube_e / 2]) linear_extrude(label_h)
        text(str(n), size = label_size, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
    if (n != 1)                                      // up-arrow on every side face
        translate([0, rim_y, cube_e / 2]) linear_extrude(label_h) polygon([[-1.6, -1.5], [1.6, -1.5], [0, 1.5]]);
}

module marker_cube() {
    difference() {
        cube(cube_e, center = true);
        for (f = faces) on_face(f) pocket();
    }
    for (f = faces) on_face(f) face_labels(f[0]);
}

// ---------------- assembly ----------------
module mount() {
    union() {
        clip();
        probe_label();
        stalk();
        translate(P1 + [0, 0, cube_e / 2]) marker_cube();
    }
}

mount();

// Numbers the software needs once this is printed (type into cube_layout.json / the tracker):
echo(str("cube edge ", cube_e, " mm; recess ", recess, " mm; stalk top at ", P1));
echo(str("cube centre above the clip bottom (z): ", P1[2] + cube_e / 2, " mm; in front of the handle axis: ", -P1[1], " mm"));
echo("Add the clip-bottom-to-probe-face distance measured on the probe to get cube-centre-to-probe-face.");
