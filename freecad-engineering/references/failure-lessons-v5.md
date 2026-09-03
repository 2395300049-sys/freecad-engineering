# V5 Failure Lessons

## Design process

- Drawing a plausible shape before defining loads and interfaces creates false progress.
- An exact reconstruction is not automatically an optimized or safe design.
- A numerical score cannot compensate for missing evidence or a failed hard constraint.
- Mixing standards without an interpretation map creates ambiguous manufacturing and inspection requirements.

## Work conditions and safety

- Nominal steady load can miss startup, jam, impact, vibration, thermal, and maintenance cases.
- A large arbitrary safety factor does not repair a wrong load path, failure mode, or material assumption.
- A colorful FEA plot is not evidence without boundary conditions, mesh, convergence, reactions, units, and an independent check.
- Static strength does not prove fatigue life, buckling resistance, wear, sealing, or fastener retention.

## CAD and native assembly

- Correct static placement is not a native assembly tree.
- Ordinary groups and copied `Part::Feature` solids do not encode mating intent or degrees of freedom.
- A solved Joint does not prove real geometry has clearance.
- Joint references tied to unstable topology can break after feature edits; prefer stable datums and named references.
- Count physical linked occurrences separately from part definitions and containers.

## Gears and motion

- `Gears Joint` proves a motion ratio, not tooth backlash, contact, strength, or housing clearance.
- A screenshot can suggest tooth-phase error while the actual collision is with a neighboring seat or flange.
- Validate the full required travel and refine around minimum-clearance positions.
- Distinguish expected flank contact from forbidden root, hub, shaft, fastener, or housing contact.

## Manufacturing and tolerance

- A machinable-looking model may require impossible tool access, excessive setup, or unsupported aspect ratios.
- Tightening every tolerance increases cost and may reduce manufacturability without improving function.
- Fine surface texture can force grinding or polishing; assign it only where functional.
- Datums chosen for visual convenience may be inaccessible to fixtures and inspection.
- Worst-case and statistical stacks answer different questions and must not be mixed silently.

## Assembly and service

- Zero final-position interference does not prove a component can be inserted.
- Missing tool space, tightening order, adjustment access, or disassembly path can invalidate an otherwise correct model.
- Flexible hoses, cables, seals, springs, and temporary fixtures need explicit handling rules.

## Cost and supply

- Unit cost without batch quantity, region, currency date, quality level, and process route is not comparable.
- Material volume alone misses setup, inspection, treatment, tooling, assembly, scrap, and overhead.
- Supplier price, stock, and lead time expire; every recommendation needs a date.
- A standard part with no approved alternate can dominate schedule and lifecycle risk.

## Drawings and delivery

- A drawing without tolerances, datums, surface/process requirements, and inspection intent is incomplete.
- Over-annotating can create contradictions and unmeasurable requirements.
- Source-identical drawing pages and model-derived drawings are different artifacts.
- A successful batch rebuild does not prove GUI visibility, drawing readability, or engineering acceptance.
- Creating a GitHub repository does not prove it is private; query remote visibility after pushing.
- Never upload proprietary reference CAD, drawings, quotations, or credentials without explicit approval.
