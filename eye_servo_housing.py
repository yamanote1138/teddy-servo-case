"""Eye servo housing for the teddy bear animatronic (SG90, shaft out the right side).

Run: uv run eye_servo_housing.py
Writes out/eye_servo_housing.{step,stl} and out/sg90_placed.stl (reference servo in housing coords).

Coordinates: X runs front (tab) to back (nub), Y runs left to right (shaft side), Z is up.
The housing floor sits at Z=0 and its front face at X=0.
"""

from pathlib import Path

import numpy as np
import trimesh
from build123d import Align, Box, Cone, Cylinder, Pos, Rot, export_step, export_stl

OUT = Path(__file__).parent / "out"
REF_STL = Path(__file__).parent / "reference" / "sg90.stl"

# --- Mount interface (caliper measured off the original housing) ---
TAB_W = 24.5  # across Y
TAB_H = 4.0  # Z
TAB_T = 7.0  # how far it sticks out the front, X
NUB_D_BASE = 5.0
NUB_D_TIP = 3.0
NUB_H = 9.0
MOUNT_SPACING = 45.0  # front face of tab to nub center, along X
SLOT = (26.0, 4.6, 4.7)  # bear frame slot the tab slides into (w, h, depth), for reference

# --- Not measured yet, best guesses (see CLAUDE.md open questions) ---
TAB_Z = None  # tab center height; None = middle of the housing
ENVELOPE_MAX = (55.0, 40.0, 75.0)  # recorded "body" size; treated as a max envelope

# --- SG90 (from reference/sg90.stl) ---
SERVO_L = 22.7  # case length, along shaft-to-cable direction
SERVO_W = 12.4  # case width
SERVO_EAR_H = 16.0  # case bottom to underside of the mounting ears
SERVO_EAR_L = 32.5
SERVO_EAR_HOLE_SPACING = 27.5
SERVO_SHAFT_OFFSET = 5.35  # shaft axis from case center, toward the cable end

# --- Print settings ---
FIT = 0.3  # clearance per side around the servo case
WALL = 2.5
FLOOR = 2.0
PLATE_T = 3.5  # right wall the ears screw to
PILOT_D = 1.6  # pilot hole for the SG90's self-tapping screws
NUB_BLOCK = 6.0  # solid rear block the nub stands on

# --- Derived layout ---
NUB_X = MOUNT_SPACING - TAB_T
L = NUB_X + NUB_BLOCK / 2
W = max(TAB_W + 1.5, SERVO_EAR_H + WALL)
H = FLOOR + SERVO_W + FIT
SERVO_X = 20.0  # case center; leaves room for the cable bulge at the front end
SERVO_Z = FLOOR + SERVO_W / 2  # case centerline
tab_z = TAB_Z if TAB_Z is not None else H / 2


def build_housing():
    mn = (Align.MIN, Align.MIN, Align.MIN)
    shell = Box(L, W, H, align=mn)

    # Pocket for the servo case, open at the top so the servo drops in
    pocket_x0 = WALL
    pocket_x1 = NUB_X - NUB_BLOCK / 2
    shell -= Pos(pocket_x0, WALL, FLOOR) * Box(pocket_x1 - pocket_x0, W - WALL - PLATE_T, H, align=mn)

    # U-notch through the right plate for the case; the ears sit on the plate's outer face
    notch_l = SERVO_L + 2 * FIT
    shell -= Pos(SERVO_X - notch_l / 2, W - PLATE_T - 1, FLOOR) * Box(notch_l, PLATE_T + 2, H, align=mn)

    # Pilot holes for the ear screws
    for dx in (-SERVO_EAR_HOLE_SPACING / 2, SERVO_EAR_HOLE_SPACING / 2):
        shell -= Pos(SERVO_X + dx, W - PLATE_T / 2, SERVO_Z) * Rot(90, 0, 0) * Cylinder(PILOT_D / 2, PLATE_T + 2)

    tab = Pos(-TAB_T, (W - TAB_W) / 2, tab_z - TAB_H / 2) * Box(TAB_T, TAB_W, TAB_H, align=mn)
    nub = Pos(NUB_X, W / 2, H) * Cone(
        NUB_D_BASE / 2, NUB_D_TIP / 2, NUB_H, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    return shell + tab + nub


def place_reference_servo():
    """Move reference/sg90.stl into housing coords: shaft along +Y, ears on the plate face."""
    m = trimesh.load(REF_STL)
    # In the STL: case x 3.9..26.6, width along y, shaft up +z, ear underside at z=0, cable end at -x
    case_cx = (3.9 + 26.6) / 2
    case_cy = (44.8 + 57.2) / 2
    m.apply_translation([-case_cx, -case_cy, 0])
    # ref x -> X, ref z (shaft) -> +Y, ref y -> -Z  (proper rotation, det = +1)
    rot = np.eye(4)
    rot[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
    m.apply_transform(rot)
    m.apply_translation([SERVO_X, W, SERVO_Z])
    return m


def check(housing_stl: Path, servo: trimesh.Trimesh):
    h = trimesh.load(housing_stl)
    overlap = trimesh.boolean.intersection([h, servo], engine="manifold").volume
    b = h.bounds
    size = b[1] - b[0]
    print(f"Housing size (incl. tab + nub): {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    print(f"Watertight: {h.is_watertight}, volume: {h.volume / 1000:.1f} cm3")
    print(f"Servo/housing overlap: {overlap:.3f} mm3 {'OK' if overlap < 0.01 else 'COLLISION'}")
    for name, s, mx in zip("XYZ", size, ENVELOPE_MAX):
        if s > mx:
            print(f"WARNING: {name} size {s:.1f} exceeds recorded envelope {mx}")
    clearance = SLOT[0] - TAB_W, SLOT[1] - TAB_H
    print(f"Tab-in-slot clearance: {clearance[0]:.1f} mm wide, {clearance[1]:.1f} mm tall")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    housing = build_housing()
    export_step(housing, OUT / "eye_servo_housing.step")
    export_stl(housing, OUT / "eye_servo_housing.stl")
    servo = place_reference_servo()
    servo.export(OUT / "sg90_placed.stl")
    check(OUT / "eye_servo_housing.stl", servo)
