# Strength, Safety, Stability, and Life

## Start with failure modes

Create a matrix mapping each part/interface and load case to applicable modes:

- Yielding, ultimate fracture, fatigue, low-cycle fatigue, creep, wear, fretting, and corrosion.
- Buckling, local instability, excessive deformation, loss of preload, loosening, and leakage.
- Bearing life, gear tooth bending/contact, shaft torsion/bending, key/spline shear/bearing, and fastener tension/shear.
- Contact pressure, Hertzian damage, surface fatigue, thermal distortion, seizure, and lubrication failure.
- Weld, adhesive, composite, pressure, lifting, guarding, or other industry-specific modes.

## Demand and allowable

For every check, record:

- Component and failure mode.
- Load case and load combination.
- Analysis method and governing standard/profile.
- Material condition, temperature, direction, and statistical basis.
- Demand value and unit.
- Allowable/capacity value and unit.
- Required and calculated safety/margin factor.
- Evidence file, reviewer, status, and limitations.

Do not compare incompatible stress definitions, units, material conditions, or life bases.

## Safety-factor selection

Select safety/margin factors from the governing standard and project risk, considering:

- Consequence of failure.
- Load and material uncertainty.
- Manufacturing variation and defects.
- Inspection and quality control.
- Environment, degradation, and maintenance.
- Model fidelity and validation evidence.
- Required reliability and life.

There is no universal factor that makes every design safe.

## Analytical calculations and FEA

- Use analytical calculations for load paths, order-of-magnitude checks, and simple components.
- Use FEA when geometry, contact, nonlinear response, thermal coupling, or local detail requires it.
- Document geometry idealization, element type/order, mesh convergence, contacts, constraints, loads, solver settings, and result extraction.
- Check reaction balance, deformation shape, singularities, local coordinate systems, and units.
- Compare FEA with an independent estimate or test where practical.

## Fatigue and life

- Use the actual load spectrum or justified equivalent cycles.
- Include mean stress, stress concentration, size, surface, temperature, reliability, corrosion, residual stress, and notch sensitivity as applicable.
- Separate infinite-life, finite-life, crack-growth, and inspection-based approaches.
- Do not use static peak stress alone as a fatigue conclusion.

## Release boundary

Safety-critical or regulated designs require the responsible engineer, required independent review, and physical validation specified by the project. Run `scripts/validate_engineering_checks.py` to audit evidence completeness, not to replace the calculation method.
