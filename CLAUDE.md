# Teddy Bear Animatronic Servo Housings

## What this is
Swapping the original DC gearmotors in an animatronic teddy bear for SG90 9g micro servos. Each servo gets a 3D-printed housing that clips into the bear's existing frame the same way the original motor unit did.

## Servos
- **Eye servo**: housing designed, not yet test-printed. Shaft out the right side, drives the eye roller.
- **Upper jaw servo**: todo
- **Lower jaw servo**: todo

## Tooling rules
- Everything runs through **uv**, using uv-managed Python only (`python-preference = "only-managed"` in `pyproject.toml`). Never use system or Homebrew Python, and never pip install.
- CAD is **build123d** (B-rep, exports STEP for Fusion 360). No Blender, OpenSCAD, or other outside tools.
- `trimesh` + `manifold3d` are only used to check fit against the real SG90 mesh.

```
uv run eye_servo_housing.py   # writes out/*.step, out/*.stl, prints fit checks
uv run render_preview.py      # writes out/preview.png (housing + servo, 4 views)
```
`out/` is gitignored, so regenerate whenever you need it.

## Eye housing design
Coordinates: X runs front (tab) to back (nub), Y runs left to right (shaft side), Z is up.

- Open-top shell. The servo lies on its side and drops into a U-notch in the right wall. Its ears sit on the wall's outer face and are held by the SG90's own two self-tapping screws (1.6mm pilot holes).
- Front tab sticks out of the front face and slides into the frame slot. Rear tapered nub stands on a solid block on top.
- Sized from the servo plus the mount points, about 48 x 26 x 24mm overall.
- `reference/sg90.stl` gets moved into housing coordinates and saved as `out/sg90_placed.stl`. The generator checks it for zero overlap. Import both STEP and the placed servo into Fusion to eyeball it.

### Measured (calipers, original housing + frame)
```
tab   24.5 w x 4.0 h x 7.0 deep
nub   5.0 -> 3.0 dia taper, 9.0 tall
mount spacing 45.0 (tab front face to nub center)
frame slot 26.0 x 4.6 x 4.7
```

### Open questions (best guesses are in the code until answered)
1. **Body size.** The notes said 55 x 40 x 75mm, but the photos (penny for scale) put the original unit at roughly 47 x 22 x 45mm. Right now 55 x 40 x 75 is only used as a max-size warning.
2. **Tab height vs. nub.** How high the tab sits relative to the nub was never measured (`TAB_Z`, currently mid-height). We're also assuming the nub points up.
3. **Spring nub.** The original nub is spring-loaded. Ours is rigid. Does it need to flex, or is there a spring on the frame side?
4. **Which side is "right".** We're assuming +Y means right when facing the bear. Mirror it if that's wrong.
5. **Horn to eye roller.** How the servo horn connects to the eye roller is unknown, and it decides where the shaft has to sit.

## Next steps
1. Answer the open questions, then update the params at the top of `eye_servo_housing.py`
2. Check in Fusion 360 (`out/eye_servo_housing.step` + `out/sg90_placed.stl`)
3. Test print, tune `FIT` / `TAB_Z`
4. Upper and lower jaw housings, reusing the same approach

## Files
- `eye_servo_housing.py`: parametric generator + fit check
- `render_preview.py`: quick PNG preview
- `reference/sg90.stl`: SG90 reference model
- `photos/`: original housing on a cutting mat, with a penny for scale
