# STEP Round-Trip Validation V7

## Contents

1. Separate immutable-copy and rebuilt-file checks
2. Required metrics
3. Absolute and relative tolerance
4. Per-occurrence checks
5. Acceptance logic
6. Reporting

## 1. Separate immutable-copy and rebuilt-file checks

Use two different validation concepts:

- **Trusted copy integrity:** a byte-for-byte copy of the accepted input should retain the same SHA-256.
- **Rebuilt STEP geometry:** a newly serialized STEP is expected to have a different hash and must be compared geometrically.

Never overwrite the trusted input with the rebuilt export.

## 2. Required metrics

For reference and candidate record:

- file size and SHA-256;
- STEP import validity;
- solid count;
- bounding-box minima and maxima;
- bounding-box lengths;
- total volume and area;
- per-occurrence or per-family volume/bounds where available;
- critical axes, centers, lengths, diameters, and interface dimensions;
- placement/occurrence count;
- import warnings and rejected entities.

## 3. Absolute and relative tolerance

Calculate:

```text
delta_abs = abs(V_candidate - V_reference)
delta_ppm = delta_abs / max(abs(V_reference), 1) * 1,000,000
```

Pass volume when:

```text
delta_abs <= max(abs_tolerance, relative_tolerance * abs(V_reference))
```

Choose thresholds from file scale, B-Rep complexity, export kernel, and engineering need. Store the actual values in the report.

Example: a 7.8 million mm³ assembly with 6.7 mm³ drift has about 0.86 ppm difference. If solid count, validity, bounds, critical dimensions, and placements match, this is usually serialization drift rather than missing geometry.

## 4. Per-occurrence checks

Aggregate metrics can hide mistakes. When occurrence identity exists:

- match occurrence IDs or trusted placement signatures;
- compare each solid's bounds and volume;
- verify repeated parts remain in distinct positions;
- check that source quantity conflicts remain visible;
- detect mirrored or reordered occurrences without treating harmless serialization order as failure.

## 5. Acceptance logic

Block when any of these occur:

- invalid or null shape;
- unexpected solid count;
- bounds exceed tolerance;
- critical dimension or axis mismatch;
- missing occurrence;
- placement mismatch;
- unexplained large ppm drift;
- trusted-copy hash mismatch.

Permit a rebuilt hash difference when geometry metrics pass. Report it explicitly rather than hiding it.

Use `scripts/compare_step_geometry.py`.

## 6. Reporting

The report must include:

- reference/candidate paths and hashes;
- FreeCAD and OCCT version;
- all thresholds;
- measured deltas;
- individual check results;
- overall pass/fail;
- interpretation of any nonzero drift;
- production-release blockers unrelated to file serialization.

Do not let a passing STEP round trip imply that BOM, tolerances, gear contact, assembly sequence, or GUI visibility also pass.
