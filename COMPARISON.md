# Housing Version Comparison

## Photo Estimate vs. Measured Dimensions

| Feature | Photo Estimate | Measured | Delta |
|---------|---------------|----------|-------|
| **Front Tab** |
| Width | 11.0mm | 24.5mm | +13.5mm (223%) |
| Height | 5.0mm | 4.0mm | -1.0mm (80%) |
| Thickness | 3.5mm | 7.0mm | +3.5mm (200%) |
| **Back Nub** |
| Diameter | 3.5mm | 5.0mm base* | +1.5mm (143%) |
| Height | 3.5mm | 9.0mm | +5.5mm (257%) |
| **Spacing** |
| Mount spacing | 28.0mm | 45.0mm | +17.0mm (161%) |
| **Overall** |
| Length | 38.0mm | 55.0mm | +17.0mm (145%) |
| Width | 16.0mm | 40.0mm | +24.0mm (250%) |
| Height | 26.0mm | 75.0mm | +49.0mm (288%) |

*Measured nub tapers from 5mm to 3mm (currently modeled as 5mm cylinder)

## Key Findings

**Photo estimation was significantly off:**
- Housing is ~3x taller than estimated
- ~2.5x wider than estimated
- Tab is over 2x wider and thicker
- Nub is 2.5x taller

**Why the estimation failed:**
- Penny scale reference worked for small features but large perspective distortion on overall housing
- Housing is much larger than typical servo enclosures

## Files Generated

- `eye_servo_housing_photo_estimate.stl` - Based on photo analysis
- `eye_servo_housing_measured.stl` - Based on caliper measurements ✓

## Notes

- Measured version uses 5mm diameter cylinder for nub (not tapered yet)
- Tab dimensions closely match slot dimensions (26mm slot vs 24.5mm tab = good fit)
- Can refine taper in Fusion 360 if needed

## Next Steps

1. Import `eye_servo_housing_measured.stl` into Fusion 360
2. Import `2051_servo_tower-pro-sg90.pk2.stl` as reference
3. Verify servo fits in cavity
4. Refine if needed (taper nub, adjust clearances, etc.)
5. Test print
