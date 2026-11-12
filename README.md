# Teddy Servo Case

3D-printable housings that swap the dead motor units in an animatronic teddy bear's head for SG90 9g micro servos. There's one housing for the eyes, upper lip and lower lip. Each servo spins a rubber-tired roller that drives the mechanism's pivoted wheel by friction, just like the original.

**Status:** early draft. The layout matches how the original sits in the head, but most of the sizes are still guesses from photos. Not printed yet.

## Run it

Needs [uv](https://docs.astral.sh/uv/). Everything else installs itself.

```
uv run eye_servo_housing.py   # housing + roller as STEP/STL in out/, plus fit checks
uv run head_assembly.py       # rough head frame with all three units, collision checks
uv run render_preview.py      # out/preview.png
```

The STEP files open in Fusion 360 as normal solids. All the sizes are parameters at the top of each script.

## What's here

- `eye_servo_housing.py`: the housing and roller (build123d)
- `head_assembly.py`: rough head frame, placeholder wheels, three-unit layout
- `render_preview.py`: quick PNG preview
- `reference/`: SG90 model, reference photos, service manual page
- `photos/`: the original motor unit, with a penny for scale (the cutting mat grid is 1/2 inch)
- `CLAUDE.md`: detailed notes, measurements, guesses and open questions
