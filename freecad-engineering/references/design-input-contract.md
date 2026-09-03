# Design Input Contract

## Purpose

Prevent geometry from being mistaken for engineering. Every project starts with a machine-readable input contract and an explicit list of blocking unknowns.

## Input status

Assign one status to every important field:

- `confirmed`: supported by the user, drawing, contract, test, official standard, or supplier evidence.
- `assumed`: selected temporarily, with owner, rationale, risk, and approval state.
- `unknown`: not available; may block dependent work.
- `not_applicable`: reviewed and intentionally excluded.

Do not convert `unknown` into `assumed` silently.

## Minimum input groups

### Project

- Project identifier, revision, task mode, owner, design authority, due date, confidentiality.
- Product function and measurable success criteria.
- Required deliverables and accepted CAD/drawing formats.

### Interfaces

- Mounting envelope, datums, neighboring components, connection geometry, utilities, controls, and service space.
- Fixed dimensions that may not change during redesign.
- Exchangeability and backward-compatibility requirements.

### Operating conditions

- Loads, torque, pressure, speed, acceleration, duty cycle, life, vibration, temperature, environment, lubrication, contamination, and misuse cases.
- Installation, transport, storage, maintenance, and emergency states.

### Production and process

- Prototype or production status, annual and batch quantity, available processes and equipment, supplier geography, inspection capability, and preferred materials.
- Target cost, currency, quotation basis, and required delivery date.

### Standards and safety

- Governing industry, drawing, tolerance, material, calculation, safety, and regulatory standards.
- Safety classification, consequence of failure, review level, and required physical tests.

## Dependency behavior

- Missing loads block safety-factor and life claims.
- Missing production quantity blocks meaningful unit-cost comparison.
- Missing process capability blocks final tolerance release.
- Missing supplier region/date blocks lead-time claims.
- Missing standards profile blocks final GD&T, drawing-symbol, and regulated acceptance claims.
- Missing interface datums block native assembly and tolerance-stack release.

## Evidence record

For each critical input, preserve:

- Value and unit.
- Status.
- Source type and source locator.
- Source date or revision.
- Owner and approver.
- Confidence or uncertainty.
- Dependent decisions.

Use `assets/templates/design-input.template.json` and run `scripts/validate_design_inputs.py`.
