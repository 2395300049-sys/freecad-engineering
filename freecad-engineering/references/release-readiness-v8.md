# Release Readiness V8

## Contents

1. State model
2. Gate semantics
3. Blocking findings
4. Approval rules

## 1. State model

Use three independent declarations:

| State | Meaning |
|---|---|
| `geometry_review_ready` | Declared geometry scope can be inspected and exchanged reliably. |
| `engineering_review_ready` | Applicable functional, assembly, drawing, manufacturing, and inspection evidence can be reviewed. |
| `production_release_ready` | All mandatory evidence passes and a responsible engineer has approved production release. |

Set each state explicitly. A lower state does not imply a higher state, and a blocked higher state does not erase useful lower-state deliverables.

## 2. Gate semantics

Use only `pass`, `fail`, `blocked`, or `not_applicable` for gates.

- `pass`: evidence exists and satisfies the declared threshold.
- `fail`: evidence exists and does not satisfy the threshold.
- `blocked`: required evidence or authority is missing.
- `not_applicable`: the gate is outside the declared scope with a recorded reason.

Geometry review normally requires source evidence, geometry validity, critical dimensions, occurrence/placement when applicable, STEP exchange, GUI state, and viewport checks.

Engineering review additionally requires the applicable assembly, interference, motion, drawing, manufacturing, inspection, service, and standards gates.

Production release requires every mandatory gate, zero unresolved blocking findings, and an approval record identifying the responsible authority and date.

## 3. Blocking findings

Keep findings structured with an identifier, severity, affected state, evidence locator, owner, and disposition. Examples include:

- unresolved solid penetration;
- unmatched BOM quantity or occurrence;
- inferred tolerance presented as released;
- invalid or unverified repaired topology;
- missing clean-room rebuild;
- missing responsible-engineer approval.

Never downgrade a blocker merely to make a summary pass.

## 4. Approval rules

Automated checks may establish that evidence passes. They cannot create production approval. Require an explicit record with `approved: true`, approver identity or role, approval date, and scope.

Run `validate_release_status_v8.py` before packaging. Preserve its report with the delivery manifest.
