# Gear Mesh and Coupled Motion

## Separate four questions

1. `kinematics`: Is the ratio, direction, axis, and motion law correct?
2. `geometry`: Do the real solids mesh and clear surrounding components?
3. `tolerance`: Does backlash/alignment remain acceptable at manufacturing and thermal limits?
4. `capacity`: Do tooth root, flank contact, wear, lubrication, and life meet the load case?

Passing one question does not pass the others.

## Engineering gear-pair record

Record as applicable:

- Gear type: spur, helical, bevel, hypoid, worm, internal, rack-pinion, or other.
- Driver and follower occurrence names.
- Tooth counts and theoretical ratio.
- Normal/transverse module or diametral pitch.
- Pressure angle, helix angle/hand, shaft angle, profile shift, face width, cone angles, offset, and hand.
- Pitch, base, tip, and root geometry basis.
- Nominal phase and rotation direction.
- Target backlash range and measurement basis.
- Accuracy grade, material, hardness, heat treatment, lubrication, duty, torque, speed, life, and governing method.
- Manufacturing method and inspection method.

## Kinematic checks

- Verify ratio magnitude from tooth counts or defined pitch relationship.
- Verify direction for external/internal meshes and crossed axes.
- Verify driver/follower speed and torque conventions.
- Establish basic Revolute or Slider joints before adding Gears, Screw, Belt, or RackPinion coupling.
- Confirm the coupled joint references the intended occurrences and axes.

## Bevel-gear checks

- Verify shaft angle and that the intended pitch-cone apex relationship is satisfied.
- Verify pitch-cone angles from tooth ratio and shaft angle for the selected geometry class.
- Confirm face width, cone distance, mounting distance, apex position, and bearing support are mutually consistent.
- Check both heel and toe clearance and the surrounding bearing seat/housing envelope.
- Do not repair an apparent mesh problem by changing phase before auditing the gear against every neighboring solid.

## Backlash and tolerance

- Define where and how backlash is measured.
- Include tooth-thickness variation, center/mounting distance, runout, bearing clearance, shaft deflection, housing tolerance, thermal growth, and adjustment range.
- Compute worst-case limits when guaranteed non-jamming clearance is required.
- Use statistical results only with justified process distributions and control.
- Record adjustment shims, eccentric features, selective assembly, or inspection procedure when backlash is set during assembly.

## Dynamic solid validation

- Preserve baseline global shapes and axis definitions.
- Rotate/translate the driver through the complete required cycle.
- Apply the kinematic law to followers.
- At each sample, audit moving parts against all non-excluded solids.
- Keep expected tooth contact separate from forbidden contact with roots, hubs, shafts, housings, fasteners, and adjacent gears.
- Refine sampling around the smallest clearance or detected penetration.
- Save sample angle, common volume, minimum distance, and object pair.

## Capacity boundary

FreeCAD Boolean clearance is not a tooth-contact stress or microgeometry solver. For capacity and contact-pattern claims, use an appropriate recognized calculation method, specialist gear software, validated FEA/contact model, inspection, or physical test. Record the method and assumptions.

Use `assets/templates/gear-pairs.template.json`, `scripts/validate_gear_pairs.py`, and `scripts/audit_motion_clearance.py`.
