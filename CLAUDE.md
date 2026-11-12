# Teddy Bear Animatronic Servo Housing Project

## Context
Replacing original servos in animatronic teddy bear with 9g micro servos (SG90). Need custom housings that mount to existing bear frame geometry.

## Servos Required
- **Eye servo** (in progress) - shaft right, moves roller for eyes
- **Upper jaw servo** (todo)
- **Lower jaw servo** (todo)

## Eye Servo Housing - Current Status

### Mounting System
- **Front:** Horizontal slot mount (tab slides in)
- **Back:** Spring-loaded nub
- **Shaft orientation:** Right side (when facing bear)

### Key Measurements (caliper verified)
```
tab_w = 24.5mm, tab_h = 4mm, tab_t = 7mm
nub_d = 5mm (tapers to 3mm), nub_h = 9mm
mount_spacing = 45mm
body = 55 x 40 x 75mm
slot = 26 x 4.6 x 4.7mm
```

### Files
- `2051_servo_tower-pro-sg90.pk2.stl` - SG90 servo reference model
- `generate_eye_servo_housing.py` - Parametric generator (uv managed)
- `eye_servo_housing_measured.stl` - Current housing based on measurements ✓
- Photos in `photos/` show original housing with penny for scale

### Next Steps
1. Import measured STL + servo STL into Fusion 360
2. Verify servo cavity fit
3. Refine (taper nub if needed, adjust clearances)
4. Test print
5. Repeat for upper/lower jaw servos

## Tech Stack
- Python 3.12 + uv for dependency management
- trimesh + numpy-stl for STL generation
- Target: Fusion 360 for final refinement
