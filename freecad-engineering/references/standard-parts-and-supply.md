# Standard Parts, Make/Buy, and Supply Chain

## Prefer controlled reuse

Before designing a custom item, search approved standard and purchased components that meet function, environment, life, safety, and interface requirements.

Typical selections include bearings, seals, fasteners, motors, gearboxes, couplings, springs, keys, retaining rings, sensors, valves, fittings, cylinders, lubricants, and electrical components.

## Selection record

For each purchased item, record:

- BOM item, internal part number, manufacturer, manufacturer part number, revision/configuration, and description.
- Functional ratings, derating, material, environmental limits, approvals, and interface dimensions.
- Supplier and authorized source status.
- Unit price, currency, quantity basis, MOQ, packaging quantity, and quotation date.
- Stock status, standard lead time, quoted lead time, expedite option, and required-on-site date.
- Lifecycle state, last-time-buy risk, geographic/export risk, and single-source risk.
- Approved alternates and interchangeability restrictions.
- Datasheet, drawing, certificate, and quotation source locators.

## Time-dependent data

Price, stock, supplier, and lead time can change quickly. Query current authoritative supplier/manufacturer information when making a purchasing recommendation, and record access time. Do not reuse an old lead time without flagging its age.

## Criticality and alternatives

- Classify safety, function, schedule, and replacement criticality.
- Require at least one technically reviewed alternate for critical items when feasible.
- Validate alternate geometry, ratings, certifications, tolerances, and lifecycle, not only description text.
- Record the cost and schedule consequence of substitution.

## Make/buy review

Compare internal capability, tooling, quality, intellectual property, quantity, lead time, supplier risk, and lifecycle cost. Do not select custom manufacture only because the CAD model is easy to draw.

Use `assets/templates/bom-sourcing.template.csv` and `scripts/audit_bom_supply.py`.
