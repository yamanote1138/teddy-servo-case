#!/usr/bin/env python3
"""
Generate eye servo housing for teddy bear animatronic
Two-point mount: front tab + rear spring nub
"""

import trimesh
import numpy as np

# ========== PARAMETERS ==========
# Set version: 'photo_estimate' or 'measured'
VERSION = 'measured'

# Servo dimensions (SG90 standard)
SERVO_LENGTH = 22.8
SERVO_WIDTH = 12.2
SERVO_HEIGHT = 22.5
SERVO_TAB_WIDTH = 32
SERVO_SHAFT_HEIGHT = 15.5  # From bottom to shaft center

# Build tolerance
FIT_TOLERANCE = 0.3

if VERSION == 'photo_estimate':
    # Estimated from photos (US penny = 19.05mm diameter)
    FRONT_TAB_WIDTH = 11.0
    FRONT_TAB_HEIGHT = 5.0
    FRONT_TAB_THICKNESS = 3.5

    BACK_NUB_DIAMETER = 3.5
    BACK_NUB_HEIGHT = 3.5

    MOUNT_SPACING = 28.0  # Front tab to back nub center distance

    HOUSING_LENGTH = 38.0
    HOUSING_WIDTH = 16.0
    HOUSING_HEIGHT = 26.0

else:  # measured
    # Actual caliper measurements
    FRONT_TAB_WIDTH = 24.5
    FRONT_TAB_HEIGHT = 4.0
    FRONT_TAB_THICKNESS = 7.0

    BACK_NUB_DIAMETER_BASE = 5.0  # Base diameter
    BACK_NUB_DIAMETER_TIP = 3.0   # Tip diameter (tapers)
    BACK_NUB_HEIGHT = 9.0

    MOUNT_SPACING = 45.0  # Front tab face to nub center

    HOUSING_LENGTH = 55.0
    HOUSING_WIDTH = 40.0
    HOUSING_HEIGHT = 75.0

    # Slot dimensions (for reference/validation)
    SLOT_WIDTH = 26.0
    SLOT_HEIGHT = 4.6
    SLOT_DEPTH = 4.7

# Wall thickness
WALL_THICKNESS = 2.0
FLOOR_THICKNESS = 2.0

# ========== GEOMETRY GENERATION ==========

def create_box(size, center=False):
    """Create a box mesh"""
    box = trimesh.creation.box(extents=size)
    if not center:
        box.apply_translation([size[0]/2, size[1]/2, size[2]/2])
    return box

def create_cylinder(radius, height, center=False):
    """Create a cylinder mesh"""
    cyl = trimesh.creation.cylinder(radius=radius, height=height)
    # Rotate to vertical orientation (Z-up)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi/2, [1, 0, 0]
    ))
    if not center:
        cyl.apply_translation([0, 0, height/2])
    return cyl

def create_cone(radius_base, radius_tip, height, center=False):
    """Create a tapered cone/cylinder mesh"""
    # Create a cone using trimesh
    if radius_tip == 0:
        # True cone
        cone = trimesh.creation.cone(radius_base, height)
    else:
        # Truncated cone - use cylinder at base and scale top
        # Create by interpolating between two circles
        cone = trimesh.creation.cone(radius_base, height, sections=32)

        # Scale the top vertices to create truncated cone
        vertices = cone.vertices.copy()
        for i, v in enumerate(vertices):
            if v[2] > height * 0.9:  # Top vertices
                scale = radius_tip / radius_base
                vertices[i][0] *= scale
                vertices[i][1] *= scale

        cone = trimesh.Trimesh(vertices=vertices, faces=cone.faces)

    # Rotate to vertical orientation (Z-up)
    cone.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi/2, [1, 0, 0]
    ))

    if not center:
        cone.apply_translation([0, 0, height/2])

    return cone

print(f"Generating {VERSION} housing...")

# Main housing body
body = create_box([HOUSING_LENGTH, HOUSING_WIDTH, HOUSING_HEIGHT])

# Servo cavity
servo_cavity_length = SERVO_LENGTH + FIT_TOLERANCE
servo_cavity_width = SERVO_WIDTH + FIT_TOLERANCE
servo_cavity_height = SERVO_HEIGHT + 2  # Extra clearance on top

servo_cavity = create_box([servo_cavity_length, servo_cavity_width, servo_cavity_height])
# Position servo cavity
servo_x_offset = (HOUSING_LENGTH - servo_cavity_length) / 2
servo_y_offset = (HOUSING_WIDTH - servo_cavity_width) / 2
servo_cavity.apply_translation([servo_x_offset, servo_y_offset, FLOOR_THICKNESS])

# Shaft access hole on right side (when facing bear)
shaft_hole_diameter = 8.0
shaft_hole = create_cylinder(shaft_hole_diameter/2, HOUSING_WIDTH + 4, center=True)
# Rotate to Y-axis and position at shaft height
shaft_hole.apply_transform(trimesh.transformations.rotation_matrix(
    np.pi/2, [0, 1, 0]
))
shaft_hole.apply_translation([
    HOUSING_LENGTH/2,
    HOUSING_WIDTH/2,
    FLOOR_THICKNESS + SERVO_SHAFT_HEIGHT
])

# Wire access cutout at back
wire_cutout = create_box([6, servo_cavity_width, FLOOR_THICKNESS + 1])
wire_cutout.apply_translation([
    HOUSING_LENGTH - 6,
    servo_y_offset,
    0
])

# Front mounting tab
front_tab = create_box([FRONT_TAB_THICKNESS, FRONT_TAB_WIDTH, FRONT_TAB_HEIGHT])
front_tab.apply_translation([
    -FRONT_TAB_THICKNESS,  # Projects forward
    (HOUSING_WIDTH - FRONT_TAB_WIDTH) / 2,
    HOUSING_HEIGHT / 2 - FRONT_TAB_HEIGHT / 2  # Center vertically
])

# Back spring nub
if VERSION == 'measured':
    # Tapered nub (5mm base to 3mm tip) - using base diameter for now
    # TODO: Implement proper truncated cone or taper in CAD
    back_nub = create_cylinder(BACK_NUB_DIAMETER_BASE/2, BACK_NUB_HEIGHT)
else:
    # Simple cylinder for photo estimate
    back_nub = create_cylinder(BACK_NUB_DIAMETER/2, BACK_NUB_HEIGHT)

# Position at rear, centered
nub_x_position = MOUNT_SPACING - FRONT_TAB_THICKNESS/2
back_nub.apply_translation([
    nub_x_position,
    HOUSING_WIDTH / 2,
    HOUSING_HEIGHT / 2 - BACK_NUB_HEIGHT / 2  # Align with tab height
])

# Boolean operations
print("Performing boolean operations...")
housing = trimesh.boolean.difference([body, servo_cavity, shaft_hole, wire_cutout], engine='blender')
housing = trimesh.boolean.union([housing, front_tab, back_nub], engine='blender')

# Export
filename = f'eye_servo_housing_{VERSION}.stl'
housing.export(filename)
print(f"Generated {filename}")
print(f"Dimensions: {HOUSING_LENGTH:.1f} x {HOUSING_WIDTH:.1f} x {HOUSING_HEIGHT:.1f} mm")
print(f"Mount spacing: {MOUNT_SPACING:.1f} mm")
print(f"\nNext: Update VERSION = 'measured' and fill in actual dimensions")
