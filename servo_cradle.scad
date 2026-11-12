// 9g Micro Servo (SG90) Friction-Fit Cradle
// Parametric design - adjust tolerances as needed

// Servo body dimensions (SG90 standard)
servo_length = 22.8;
servo_width = 12.2;
servo_height = 22.5;
servo_tab_width = 32;
servo_tab_thickness = 2.5;

// Cradle parameters
wall_thickness = 2;
fit_tolerance = 0.3; // Adjust for your printer (0.2-0.5mm typical)
floor_thickness = 2;

// Calculated dimensions
inner_length = servo_length + fit_tolerance;
inner_width = servo_width + fit_tolerance;
inner_height = servo_height * 0.6; // Cradle holds ~60% of servo height

outer_length = inner_length + (wall_thickness * 2);
outer_width = inner_width + (wall_thickness * 2);
outer_height = inner_height + floor_thickness;

// Build the cradle
module servo_cradle() {
    difference() {
        // Outer shell
        cube([outer_length, outer_width, outer_height]);

        // Hollow out the servo pocket
        translate([wall_thickness, wall_thickness, floor_thickness])
            cube([inner_length, inner_width, inner_height + 1]);

        // Cutout for servo tabs (so they don't interfere)
        translate([outer_length/2 - servo_tab_width/2 - fit_tolerance,
                   -1,
                   floor_thickness + servo_height * 0.4])
            cube([servo_tab_width + fit_tolerance*2,
                  outer_width + 2,
                  servo_tab_thickness + fit_tolerance + 1]);
    }

    // Optional: Add wire channel
    translate([wall_thickness + inner_length/2 - 3,
               wall_thickness,
               0])
        cube([6, inner_width, floor_thickness]);
}

servo_cradle();
