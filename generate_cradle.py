#!/usr/bin/env python3
"""Generate a friction-fit cradle for 9g micro servo (SG90)"""

import trimesh
import numpy as np

# Servo dimensions (SG90 standard)
SERVO_LENGTH = 22.8
SERVO_WIDTH = 12.2
SERVO_HEIGHT = 22.5
SERVO_TAB_WIDTH = 32
SERVO_TAB_THICKNESS = 2.5

# Cradle parameters
WALL_THICKNESS = 2.0
FIT_TOLERANCE = 0.3  # Adjust for your printer
FLOOR_THICKNESS = 2.0

# Calculated dimensions
inner_length = SERVO_LENGTH + FIT_TOLERANCE
inner_width = SERVO_WIDTH + FIT_TOLERANCE
inner_height = SERVO_HEIGHT * 0.6  # Holds ~60% of servo

outer_length = inner_length + (WALL_THICKNESS * 2)
outer_width = inner_width + (WALL_THICKNESS * 2)
outer_height = inner_height + FLOOR_THICKNESS

def create_box(size, center=False):
    """Create a box mesh"""
    box = trimesh.creation.box(extents=size)
    if not center:
        # Move from center to corner origin
        box.apply_translation([size[0]/2, size[1]/2, size[2]/2])
    return box

# Create outer shell
outer_box = create_box([outer_length, outer_width, outer_height])

# Create inner cavity (servo pocket)
inner_box = create_box([inner_length, inner_width, inner_height + 1])
inner_box.apply_translation([WALL_THICKNESS, WALL_THICKNESS, FLOOR_THICKNESS])

# Create tab cutout
tab_cutout = create_box([
    SERVO_TAB_WIDTH + FIT_TOLERANCE * 2,
    outer_width + 2,
    SERVO_TAB_THICKNESS + FIT_TOLERANCE + 1
])
tab_cutout.apply_translation([
    outer_length/2 - (SERVO_TAB_WIDTH + FIT_TOLERANCE * 2)/2,
    -1,
    FLOOR_THICKNESS + SERVO_HEIGHT * 0.4
])

# Boolean operations to create the cradle
cradle = trimesh.boolean.difference([outer_box, inner_box, tab_cutout], engine='blender')

# Export to STL
cradle.export('servo_cradle.stl')
print(f"Generated servo_cradle.stl")
print(f"Dimensions: {outer_length:.1f} x {outer_width:.1f} x {outer_height:.1f} mm")
