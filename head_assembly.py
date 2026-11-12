"""Approximate head frame with all three servo housings installed (eyes, upper lip, lower lip).

Run: uv run head_assembly.py   (after eye_servo_housing.py)
Writes out/head_frame.{step,stl}, out/wheels.stl, and out/assembly.json (unit placements, springs).

Head coords: X runs face (0) to back of head, Y runs across the head, Z is up.
Frame size, unit heights and wheel sizes are guesses from reference/teddyref2/3/6 and schematic1.
Each unit's tab sits in a slot in the frame's front bar, its roller drives the rim of a pivoted wheel
at the front, and a spring runs from its back nub straight back to a nub on the frame's back bar.
"""

import json
import math

import numpy as np
import trimesh
from build123d import Align, Box, Cylinder, Pos, Rot, export_step, export_stl

import eye_servo_housing as hs

MN = (Align.MIN, Align.MIN, Align.MIN)

# --- Frame guesses (outer size from the hand in teddyref6 and unit size in teddyref2) ---
FRAME_X = 80.0  # face to back
FRAME_Z = 115.0  # tall
FRAME_Y = 40.0  # depth across the head
BAR = 6.0  # ring bar thickness in the X/Z plane
FRAME_NUB_D = 4.0
FRAME_NUB_L = 6.0

# --- Units: (name, center height Z, which side of the roller its wheel is on) ---
UNITS = [("eyes", 91.0, "up"), ("upper lip", 59.0, "up"), ("lower lip", 26.0, "down")]
WHEEL_R = 5.0  # placeholder pivoted wheels
WHEEL_ANGLE = 30.0  # contact angle from vertical, leaning toward the face

SLOT_W, SLOT_H, SLOT_D = hs.SLOT


def unit_transform(zc):
    """4x4 from housing coords to head coords. Tab seats fully in its slot; roller on the -Y side."""
    t = np.eye(4)
    t[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]  # housing Y -> up, housing Z (shaft) -> -Y across
    across = hs.ROLLER_Z0 + hs.ROLLER_W  # unit's full extent across the head
    t[:3, 3] = np.array([BAR - SLOT_D + hs.TAB_T, 0, zc]) - t[:3, :3] @ np.array([0, hs.W / 2, across / 2])
    return t


def apply(t, p):
    return (t[:3, :3] @ np.asarray(p, float)) + t[:3, 3]


def build_frame(placements):
    ring = Box(FRAME_X, FRAME_Y, FRAME_Z, align=MN)
    ring -= Pos(BAR, -1, BAR) * Box(FRAME_X - 2 * BAR, FRAME_Y + 2, FRAME_Z - 2 * BAR, align=MN)
    ring = Pos(0, -FRAME_Y / 2, 0) * ring
    for t in placements:
        c = apply(t, (-hs.TAB_T / 2, hs.W / 2, hs.TAB_Z))
        ring -= Pos(BAR - SLOT_D / 2, c[1], c[2]) * Box(SLOT_D + 0.01, SLOT_H, SLOT_W)
        n = apply(t, (hs.L, hs.W / 2, hs.NUB_Z))
        ring += Pos(FRAME_X - BAR - FRAME_NUB_L / 2, n[1], n[2]) * Rot(0, 90, 0) * Cylinder(FRAME_NUB_D / 2, FRAME_NUB_L)
    ring += Pos(FRAME_X / 2 - 9, -8, -10) * Box(18, 16, 10, align=MN)
    return ring


def wheel_center(t, side):
    """Placeholder wheel touching the roller rim, leaning toward the face."""
    axis = apply(t, (hs.ROLLER_X, hs.SHAFT_Y, hs.ROLLER_Z))
    a = math.radians(WHEEL_ANGLE)
    d = hs.ROLLER_D / 2 + WHEEL_R
    s = 1 if side == "up" else -1
    return axis + np.array([-d * math.sin(a), 0, s * d * math.cos(a)]), axis


if __name__ == "__main__":
    placements = [unit_transform(zc) for _, zc, _ in UNITS]
    frame = build_frame(placements)
    export_step(frame, hs.OUT / "head_frame.step")
    export_stl(frame, hs.OUT / "head_frame.stl")

    wheels = None
    for (_, _, side), t in zip(UNITS, placements):
        wc, _ = wheel_center(t, side)
        w = Pos(*wc) * Rot(90, 0, 0) * (Cylinder(WHEEL_R, hs.ROLLER_W) - Cylinder(1.0, hs.ROLLER_W))
        wheels = w if wheels is None else wheels + w
    export_stl(wheels, hs.OUT / "wheels.stl")

    housing = trimesh.load(hs.OUT / "eye_servo_housing.stl")
    servo = trimesh.load(hs.OUT / "sg90_placed.stl")
    roller = trimesh.load(hs.OUT / "roller_placed.stl")
    frame_m = trimesh.load(hs.OUT / "head_frame.stl")
    wheels_m = trimesh.load(hs.OUT / "wheels.stl")

    worst, placed, units = 0.0, [], []
    for (name, zc, side), t in zip(UNITS, placements):
        parts = [m.copy().apply_transform(t) for m in (housing, servo, roller)]
        for label, m in zip(("housing", "servo", "roller"), parts):
            for other, om in (("frame", frame_m), ("wheels", wheels_m)):
                v = hs.overlap(om, m)
                worst = max(worst, v)
                if v > 0.01:
                    print(f"COLLISION {name} {label} vs {other}: {v:.3f} mm3")
        placed.append(parts)
        wc, axis = wheel_center(t, side)
        nub_tip = apply(t, (hs.L + hs.NUB_GROOVE_AT, hs.W / 2, hs.NUB_Z))
        frame_nub = np.array([FRAME_X - BAR - FRAME_NUB_L + 1.5, nub_tip[1], nub_tip[2]])
        units.append({"name": name, "wheel": side, "matrix": t.T.flatten().round(4).tolist(),
                      "nub": nub_tip.round(2).tolist(), "frame_nub": frame_nub.round(2).tolist(),
                      "roller": axis.round(2).tolist(), "wheel_center": wc.round(2).tolist()})
    v = hs.overlap(frame_m, wheels_m)
    worst = max(worst, v)
    print(f"wheels vs frame: {v:.3f} mm3")
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            v = sum(hs.overlap(a, b) for a in placed[i] for b in placed[j])
            worst = max(worst, v)
            print(f"{UNITS[i][0]} vs {UNITS[j][0]}: {v:.3f} mm3")
    print("All clear" if worst < 0.01 else "COLLISION somewhere above")
    for u in units:
        gap = u["frame_nub"][0] - u["nub"][0]
        print(f"{u['name']:10s} roller axis {u['roller']}, wheel {u['wheel']} at {u['wheel_center']}, spring length {gap:.1f} mm")

    (hs.OUT / "assembly.json").write_text(json.dumps(
        {"frame": [FRAME_X, FRAME_Y, FRAME_Z, BAR], "wheel_r": WHEEL_R, "roller_w": hs.ROLLER_W, "units": units}, indent=1))
