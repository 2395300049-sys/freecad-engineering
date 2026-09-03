# Assembly Sequence, Disassembly, and Service

## Static clearance is insufficient

A final position can be interference-free while no collision-free insertion path exists. Validate the ordered process used by manufacturing and service personnel.

## Sequence definition

For each step, record:

- Step ID, subassembly, component occurrence, prerequisite steps, and responsible process.
- Initial and final pose or insertion direction/travel.
- Temporary orientation, fixture, support, lifting point, and handling limit.
- Fasteners, adhesive, lubricant, sealant, heat/cool fit, press force, torque, and tightening order.
- Adjustment, measurement, inspection hold point, and acceptance criterion.
- Required tool and tool-envelope geometry.
- Rework and removal method.

## Precedence graph

- Require an acyclic normal assembly sequence unless a documented loop represents iterative adjustment.
- Detect missing components, duplicate installation, and unsatisfied prerequisites.
- Group stable subassemblies where they reduce risk and handling complexity.
- Identify components trapped by later operations.

## Path and access checks

- Check the swept envelope from initial to final pose.
- Include hands, grippers, fixtures, press tooling, torque tools, pullers, and gauges where space is critical.
- Verify fastener head access, wrench swing, driver alignment, and thread engagement.
- Include cable, hose, seal, spring, and flexible-part routing constraints.

## Adjustment and inspection

- Define how preload, backlash, endplay, alignment, timing, and seal compression are set and measured.
- Ensure adjustment remains accessible before the closing step.
- Record witness marks, locking method, torque record, and inspection evidence.

## Serviceability

- Define service items and replacement intervals.
- Verify removal sequence, drainage, isolation, cleanliness, lifting, and safe stored-energy release.
- Minimize destruction of unrelated parts and one-time-use components unless justified.
- Confirm replacement parts and tools fit through available access.

Use `assets/templates/assembly-sequence.template.json` and `scripts/audit_assembly_sequence.py`. Validate sequence structure before geometric path simulation.
