# Standards Profile

## Select one controlled profile

Record the governing family for:

- Technical drawing presentation and projection.
- Dimensional tolerances and limits/fits.
- Geometrical product specifications and GD&T.
- Surface texture and edge indications.
- Threads, splines, keys, gears, bearings, fasteners, welds, castings, and materials.
- Strength, fatigue, pressure, lifting, guarding, electrical, or industry-specific safety rules.

Use GB/T, ISO, ASME, DIN, JIS, company standards, or another system only when applicable. Do not mix symbols or interpretation rules without a documented equivalence map.

## Edition control

- Record standard identifier, title, edition/revision, publication date, source, and access date.
- Verify current editions from official standards bodies, regulators, or authoritative controlled subscriptions.
- Record contractually frozen older editions separately from current editions.
- Do not quote or redistribute copyrighted standard text beyond permitted use.

## Conflict hierarchy

Define the project hierarchy explicitly, for example:

1. Applicable law and regulation.
2. Customer contract and approved specification.
3. Industry safety standard.
4. Company design standard.
5. General drawing/tolerance standard.
6. Engineering assumption.

Escalate conflicts instead of selecting the easiest requirement.

## Units and decimal conventions

- Declare the base length, mass, force, pressure, torque, temperature, angle, and time units.
- Store calculation values with units or explicit schema units.
- Distinguish decimal separator formatting from numeric storage.
- Do not round intermediate calculations to drawing precision.

Use `assets/templates/standards-profile.template.json` as the project record and run `scripts/validate_standards_profile.py`.
