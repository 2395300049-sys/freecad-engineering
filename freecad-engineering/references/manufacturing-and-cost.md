# Manufacturing and Cost Engineering

## Select the manufacturing route before freezing detail

Choose the likely blank and process chain:

- Bar, plate, tube, extrusion, casting, forging, weldment, additive preform, or purchased near-net component.
- Turning, milling, drilling, boring, broaching, shaping, grinding, honing, lapping, EDM, laser/waterjet, bending, forming, welding, heat treatment, coating, and inspection as applicable.

## DFM review

Check:

- Tool and spindle access, cutter length, feature depth-to-width ratio, drill wander, and chip evacuation.
- Clamping surfaces, setup count, datum transfer, rigidity, distortion, and thin-wall behavior.
- Standard stock sizes, standard tooling, common radii, thread runout, undercuts, reliefs, and deburring access.
- Whether tolerances and roughness match the selected process capability.
- Heat-treatment distortion, grinding allowance, coating thickness, masking, and post-treatment inspection.
- Casting draft, parting line, cores, machining allowance, shrinkage, and porosity risk.
- Welding access, sequence, distortion, residual stress, inspection, and stress relief.

## Cost model

Separate:

- Material and purchased blank.
- Scrap and yield loss.
- Setup/programming amortized by batch quantity.
- Machine cycle time and labor.
- Tooling, fixtures, gauges, and consumables.
- Subcontract operations, heat treatment, coating, and special processes.
- Inspection, testing, documentation, assembly, packaging, freight, overhead, and contingency.

Do not compare unit cost without the same quantity, currency date, region, quality level, and quotation assumptions.

## Tolerance-cost loop

When a tolerance or surface requirement exceeds normal process capability:

1. Confirm the functional need.
2. Consider datum or architecture changes.
3. Evaluate selective assembly, adjustment, shimming, or standard precision components.
4. Add the required finishing and inspection operations to cost.
5. Re-run the tolerance stack and concept comparison.

Use `assets/templates/manufacturing-plan.template.json`, `scripts/audit_manufacturability.py`, `assets/templates/manufacturing-cost.template.json`, and `scripts/estimate_manufacturing_cost.py`.
