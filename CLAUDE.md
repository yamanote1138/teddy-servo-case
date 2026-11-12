# Teddy Bear Animatronic Servo Housings

## What this is
Swapping the original DC gearmotors in an animatronic teddy bear for SG90 9g micro servos. Each servo gets a 3D-printed housing that clips into the bear's existing frame the same way the original motor unit did.

## Servos
- **All three (eyes, upper lip, lower lip)**: one shared housing + roller, drafted from photo guesses and user corrections, not yet test-printed.

## Tooling rules
- Everything runs through **uv**, using uv-managed Python only (`python-preference = "only-managed"` in `pyproject.toml`). Never use system or Homebrew Python, and never pip install.
- CAD is **build123d** (B-rep, exports STEP for Fusion 360). No Blender, OpenSCAD, or other outside tools.
- `trimesh` + `manifold3d` are only used to check fit against the real SG90 mesh.

```
uv run eye_servo_housing.py   # writes out/*.step, out/*.stl, prints fit checks
uv run render_preview.py      # writes out/preview.png (housing + servo + roller, 4 views)
uv run head_assembly.py       # approximate head frame + all 3 units, collision checks, out/assembly.json
```
`out/` is gitignored, so regenerate whenever you need it.

## Housing design (same part for eyes and both lips)
Housing coords: X runs front (tab, toward the face) to back (nub), Z is the servo shaft direction, Y is the other side.
In the head: X stays face-to-back, housing Y is vertical, housing Z runs across the head.

- Solid block, 38 x 24.5 x 18mm. The servo drops into a pocket from the top (+Z) and its ears screw to the top face (SG90's own screws, 1.6mm pilots).
- Shaft points across the head, toward the front of the unit. The printed roller (`out/roller.stl`) sits on the spline beside the housing, and its rim drives the rim of the mechanism's pivoted wheel. Its groove takes an O-ring or silicone tube as the tire.
- Tab on the front face (rounded edges so it can rock). The nub points straight back from the back face, with a groove near the tip for the spring loop.
- The servo cable leaves through a notch in the front face, below the tab.
- The generator moves `reference/sg90.stl` into housing coords and checks that servo, roller, and housing don't overlap.

### In the head (`head_assembly.py`, from teddyref2/3/6 + `reference/schematic1.webp` + user)
- Orange ring frame. Units stacked: eyes on top, upper lip in the middle, lower lip at the bottom, all in the same orientation.
- Tab sits in a slot in the frame's **front bar**. The rollers are at the **front** of the frame, axles running across the head, and each one drives the **rim of a pivoted wheel** for the eyes or a jaw.
- The frame's **back bar has three nubs on the inside**, one per unit. A spring runs straight back from each unit's nub to its frame nub.
- Frame (80 x 40 x 115mm, 6mm bars), unit heights, and the 5mm placeholder wheels (eyes and upper lip above the roller, lower lip below) are guesses.

### Current guesses (replace with calipers)
`ROLLER_D` 18, `ROLLER_W` 9, `TAB_Z` 12.5, `NUB_Z` 9, and the 45mm spacing read as tab face to nub *base*. Frame, unit heights, and wheels live at the top of `head_assembly.py`.

### Measured (calipers, original housing + frame)
```
tab   24.5 w x 4.0 h x 7.0 deep
nub   5.0 -> 3.0 dia taper, 9.0 tall
mount spacing 45.0 (tab front face to nub center)
frame slot 26.0 x 4.6 x 4.7
```

### How the original works (from `reference/teddyref*.jpeg` + user)
- Three motor units that look identical (eyes, upper jaw, lower jaw), stacked in the orange head frame.
- Each unit is a DC motor + gearbox turning a **rubber roller**. The roller's rim presses on the rim of a pivoted wheel that works the eyes or a jaw, driving it by friction.
- The **front tab is a pivot** in the frame slot. A **spring runs from the rear nub to a nub on the frame's back bar** and keeps the roller pressed on its wheel, with some give.
- If the mechanism jams or hits its end stop, the roller just slips, which protects the gears.
- **5 wires per unit:** 2 for the motor, 3 for a position pot (the small board with the wiper). The bear's control board read the pot and drove the motor, so the original was basically a servo with its controller elsewhere. The pot reads the roller side, so a slip loses track of the mechanism.

### Still to measure
- Roller: diameter, width, bore, and its center measured from the tab
- Pivoted wheels: diameter, pivot position, and which side of the roller each touches
- Frame: inside size, tab slot heights, back nub positions
- Is the 45mm mount spacing to the nub's base or its center?
- How far each wheel's rim moves from open to closed

### Open questions
1. **Body size.** The old 55 x 40 x 75mm note doesn't match the photos (~44 x 22 x 42). It's only used as a max-size warning.
2. **Controller.** A new controller, or the bear's original board with SG90s rewired to 5 wires? Wiring only, the housing doesn't change.

## Next steps
1. Answer the open questions, then update the params at the top of `eye_servo_housing.py`
2. Check in Fusion 360 (the STEP files plus `out/sg90_placed.stl` and `out/roller_placed.stl`)
3. Test print, tune `FIT` / `TAB_Z`
4. Confirm the same housing fits the upper and lower lip positions

## Files
- `eye_servo_housing.py`: parametric generator + fit check
- `render_preview.py`: quick PNG preview
- `head_assembly.py`: approximate head frame + 3-unit layout
- `reference/sg90.stl`: SG90 reference model
- `photos/`: original housing on a cutting mat, with a penny for scale
