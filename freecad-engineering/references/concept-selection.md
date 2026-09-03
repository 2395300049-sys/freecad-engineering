# Concept Selection and Tradeoffs

## Generate credible options

For new-design or redesign work, compare distinct architectures rather than cosmetic variants. Include a baseline/reference option when available.

## Apply hard constraints first

Reject an option before scoring if it violates a mandatory envelope, load capacity, safety rule, interface, deadline, process capability, or unavailable critical component.

## Score remaining options

Typical criteria include:

- Functional performance and controllability.
- Strength, life, stability, thermal behavior, and safety risk.
- Manufacturability, inspection, assembly, adjustment, and service.
- Mass, size, energy use, noise, and cleanliness.
- Prototype cost, production cost, tooling, and lifecycle cost.
- Standard-part content, supplier concentration, lead time, and substitution options.
- Technical maturity, validation burden, and schedule risk.

Normalize criteria consistently and define whether lower or higher values are better. Record weights and owners.

## Sensitivity and uncertainty

- Vary dominant weights and uncertain inputs.
- Identify options whose ranking changes easily.
- Do not hide missing evidence behind precise scores.
- Use qualitative risk bands when quantitative data are not defensible.

## Decision record

Preserve:

- Options considered.
- Hard-constraint results.
- Raw evidence and normalized scores.
- Sensitivity results.
- Eliminated options and reasons.
- Selected option, residual risks, and approver.

Use `scripts/score_design_options.py` with `assets/templates/design-options.template.json`.
