"""Servo housing for the teddy bear animatronic (SG90 driving a friction roller). Same part for eyes and both lips.

Run: uv run eye_servo_housing.py
Writes out/eye_servo_housing.{step,stl}, out/roller.{step,stl}, plus out/sg90_placed.stl and
out/roller_placed.stl (both in housing coords) for fit checks and previews.

Housing coords: X runs front (tab, toward the face) to back (nub), Z is the servo shaft direction,
Y is the remaining side. In the head, X stays face-to-back, Y is vertical, and Z runs across the head.
The servo drops into a pocket from the top (+Z) and its ears screw to the top face. The roller sits on
the shaft at the front end, beside the housing, and its rim drives the mechanism's pivoted wheel.
A spring runs from the back nub straight back to a nub on the head frame.
"""

from pathlib import Path

import trimesh
from build123d import Align, Axis, Box, Cone, Cylinder, Pos, Rot, export_step, export_stl, fillet

OUT = Path(__file__).parent / "out"
REF_STL = Path(__file__).parent / "reference" / "sg90.stl"
MN = (Align.MIN, Align.MIN, Align.MIN)

# --- Mount interface (caliper measured off the original housing) ---
TAB_W = 24.5  # along Y (vertical in the head)
TAB_H = 4.0  # along Z
TAB_T = 7.0  # how far it sticks out the front, X
NUB_D_BASE = 5.0
NUB_D_TIP = 3.0
NUB_H = 9.0
MOUNT_SPACING = 45.0  # tab front face to the nub; taken here as to the nub's base on the back face
SLOT = (26.0, 4.6, 4.7)  # frame slot the tab slides into (w, h, depth), for reference

# --- Guesses, replace with calipers ---
TAB_Z = 12.5  # tab center across the head; kept above the servo cable exit
NUB_Z = 9.0  # nub center across the head (spring line)
ROLLER_D = 18.0  # original bracket opening is ~20mm
ROLLER_W = 9.0
NUB_GROOVE_AT = 7.0  # spring-retaining groove, measured out from the nub base
NUB_GROOVE_DEPTH = 0.4
NUB_GROOVE_W = 1.0
TAB_ROUND = 1.5  # rounded front edges so the unit can rock in the slot
ENVELOPE_MAX = (55.0, 40.0, 75.0)  # old "body" note; only used as a max-size warning

# --- SG90 (from reference/sg90.stl; there the ear underside is z=0, shaft points +z at x=9.9) ---
SERVO_L = 22.7  # case length, along X here
SERVO_W = 12.4  # case width, along Y here
SERVO_EAR_TO_BOTTOM = 16.0  # ear underside to case bottom
SERVO_EAR_TO_BOSS = 11.0  # ear underside to top of the gear boss
SERVO_EAR_TO_SPLINE_TIP = 13.8
SERVO_SHAFT_OFFSET = 5.35  # shaft axis from case center, toward the cable end
SERVO_EAR_HOLE_SPACING = 27.5
CABLE_NOTCH = (5.5, 9.0)  # width (Y) and height (Z, from the floor) of the cable exit through the front wall
SPLINE_D = 4.9  # socket for the output spline (press fit, plus the horn screw)
SCREW_D = 2.3

# --- Print settings ---
FIT = 0.3  # clearance per side around the servo case
FLOOR = 2.0
PILOT_D = 1.6  # pilot hole for the SG90's self-tapping screws
PILOT_DEPTH = 6.0

# --- Derived layout ---
L = MOUNT_SPACING - TAB_T  # body length, front face to back face
W = TAB_W  # body height in the head
H = FLOOR + SERVO_EAR_TO_BOTTOM  # ears sit on the top face
CASE_X0 = 4.0  # case front end; the cable bulge pokes out the front through the notch
CASE_X = CASE_X0 + SERVO_L / 2
ROLLER_X = CASE_X - SERVO_SHAFT_OFFSET  # shaft (and roller) toward the front
SHAFT_Y = W / 2
ROLLER_Z0 = H + SERVO_EAR_TO_BOSS + 0.2  # roller inner face, just clear of the gear boss
ROLLER_Z = ROLLER_Z0 + ROLLER_W / 2


def build_housing():
    body = Box(L, W, H, align=MN)
    body -= Pos(CASE_X0 - FIT, SHAFT_Y - SERVO_W / 2 - FIT, FLOOR) * Box(SERVO_L + 2 * FIT, SERVO_W + 2 * FIT, H, align=MN)
    body -= Pos(-1, SHAFT_Y - CABLE_NOTCH[0] / 2, FLOOR) * Box(CASE_X0 + 1, CABLE_NOTCH[0], CABLE_NOTCH[1] - FLOOR, align=MN)
    for dx in (-SERVO_EAR_HOLE_SPACING / 2, SERVO_EAR_HOLE_SPACING / 2):
        body -= Pos(CASE_X + dx, SHAFT_Y, H) * Cylinder(PILOT_D / 2, 2 * PILOT_DEPTH)

    tab = Pos(-TAB_T, (W - TAB_W) / 2, TAB_Z - TAB_H / 2) * Box(TAB_T, TAB_W, TAB_H, align=MN)
    tab = fillet(tab.edges().filter_by(Axis.Y).filter_by_position(Axis.X, -TAB_T - 0.1, -TAB_T + 0.1), TAB_ROUND)
    return body + tab + Pos(L, W / 2, NUB_Z) * Rot(0, 90, 0) * build_nub()


def build_nub():
    """Tapered nub along +Z from the origin, with a groove near the tip for the spring loop."""

    def d_at(z):
        return NUB_D_BASE + (NUB_D_TIP - NUB_D_BASE) * z / NUB_H

    up = (Align.CENTER, Align.CENTER, Align.MIN)
    z0, z1 = NUB_GROOVE_AT - NUB_GROOVE_W / 2, NUB_GROOVE_AT + NUB_GROOVE_W / 2
    lower = Cone(d_at(0) / 2, d_at(z0) / 2, z0, align=up)
    neck = Pos(0, 0, z0) * Cylinder(d_at(z1) / 2 - NUB_GROOVE_DEPTH, NUB_GROOVE_W, align=up)
    upper = Pos(0, 0, z1) * Cone(d_at(z1) / 2, d_at(NUB_H) / 2, NUB_H - z1, align=up)
    return lower + neck + upper


def build_roller():
    """Printed roller on the SG90 spline; groove takes an O-ring or silicone tube as the rubber tire."""
    along = (Align.CENTER, Align.CENTER, Align.MIN)
    r = Cylinder(ROLLER_D / 2, ROLLER_W, align=along)
    r -= Cylinder(SPLINE_D / 2, SERVO_EAR_TO_SPLINE_TIP - SERVO_EAR_TO_BOSS - 0.2, align=along)
    r -= Cylinder(SCREW_D / 2, ROLLER_W, align=along)
    tire_w = ROLLER_W - 3.0
    groove = Cylinder(ROLLER_D / 2 + 1, tire_w, align=along) - Cylinder(ROLLER_D / 2 - 1.0, tire_w, align=along)
    return r - Pos(0, 0, 1.5) * groove


def place(shape):
    """Move a roller built along +Z at the origin onto the servo shaft."""
    return Pos(ROLLER_X, SHAFT_Y, ROLLER_Z0) * shape


def place_reference_servo():
    """Move reference/sg90.stl into housing coords: same axes, ears on the top face, shaft at the front."""
    m = trimesh.load(REF_STL)
    m.apply_translation([ROLLER_X - 9.9, SHAFT_Y - (44.8 + 57.2) / 2, H])
    return m


def overlap(a, b):
    return trimesh.boolean.intersection([a, b], engine="manifold").volume


def check(housing, servo, roller):
    b = trimesh.util.concatenate([housing, servo, roller]).bounds
    size = b[1] - b[0]
    print(f"Unit size with servo + roller: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm (incl. tab and nub)")
    print(f"Watertight: housing {housing.is_watertight}, roller {roller.is_watertight}; housing {housing.volume / 1000:.1f} cm3")
    for name, v in (("servo/housing", overlap(housing, servo)), ("roller/housing", overlap(housing, roller))):
        print(f"{name} overlap: {v:.3f} mm3 {'OK' if v < 0.01 else 'COLLISION'}")
    for axis, s, mx in zip("XYZ", size, ENVELOPE_MAX):
        if s > mx:
            print(f"WARNING: {axis} size {s:.1f} exceeds recorded envelope {mx}")
    print(f"Roller front edge {ROLLER_X - ROLLER_D / 2:.1f} mm behind the body's front face; 180 deg sweep = {3.14159 * ROLLER_D / 2:.1f} mm of rim travel")
    print(f"Tab-in-slot clearance: {SLOT[0] - TAB_W:.1f} mm wide, {SLOT[1] - TAB_H:.1f} mm tall")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    housing = build_housing()
    roller = build_roller()
    export_step(housing, OUT / "eye_servo_housing.step")
    export_stl(housing, OUT / "eye_servo_housing.stl")
    export_step(roller, OUT / "roller.step")
    export_stl(roller, OUT / "roller.stl")
    export_stl(place(roller), OUT / "roller_placed.stl")
    servo = place_reference_servo()
    servo.export(OUT / "sg90_placed.stl")
    check(trimesh.load(OUT / "eye_servo_housing.stl"), servo, trimesh.load(OUT / "roller_placed.stl"))
