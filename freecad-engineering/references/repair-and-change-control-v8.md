# Repair and Change Control V8

## Contents

1. Localized marked corrections
2. Trusted B-Rep repair
3. Regression scope
4. Acceptance evidence

## 1. Localized marked corrections

Treat circles, arrows, colors, and handwritten notes as change-location evidence, not complete dimensional authority. Preserve the original image and record the marked region coordinates.

Create a change request containing:

- the source file and page/image locator;
- the target part, occurrence, feature, and parameter;
- the stated difference and desired result;
- connected interfaces and downstream drawings;
- the selected authority and remaining uncertainty;
- before/after artifact identifiers.

Inspect enough surrounding context to understand the feature. Do not limit the correction to the painted pixels when the geometry is controlled by a shared datum, pattern, mate, or sketch constraint.

## 2. Trusted B-Rep repair

Use the least invasive operation that addresses the diagnosed defect. Candidate operations include tolerance normalization, splitter removal, sewing, shell repair, self-fuse, or targeted face replacement. Never chain healing operations without recording each one.

Record before and after:

- shape validity and diagnostic message;
- shape/solid/shell/face/edge/vertex counts;
- global placement;
- axis-aligned bounds;
- volume, area, and center of mass;
- critical dimensions and interface geometry;
- repair command, runtime, and software version.

Declare numerical thresholds before accepting the result. A typical import-repair gate may require unchanged solid count and placement, bounds within 0.001 mm, and volume drift below a job-specific ppm threshold. Do not use these example values automatically for precision-critical parts.

## 3. Regression scope

Map every change to affected gates:

| Change | Minimum regression |
|---|---|
| local feature size | validity, critical dimensions, bounds, drawing |
| hole/axis location | placement, mating interfaces, interference, drawing |
| occurrence placement | global bounds, occurrence ledger, interference, viewport |
| topology repair | validity, topology, volume/bounds/center, STEP round trip |
| fastener/support detail | BOM mapping, occurrence count, interference, assembly sequence |
| visual-only GUI state | reopen, visibility, camera, viewport screenshot |

Escalate the scope when shared parameters or references propagate beyond the initial feature.

## 4. Acceptance evidence

Accept a correction or repair only when:

- the requested local difference is visibly and dimensionally resolved;
- selected authorities remain satisfied;
- declared invariants pass;
- no new unresolved penetration or missing occurrence appears;
- the delivery manifest references the new revision;
- the prior accepted revision remains recoverable;
- release readiness is recalculated rather than inherited.

Use `change-request.template.json` and `repair-evidence.template.json`. Validate repair evidence with `validate_repair_evidence_v8.py`.
