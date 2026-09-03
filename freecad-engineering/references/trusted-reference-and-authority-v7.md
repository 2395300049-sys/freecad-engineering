# Trusted Reference and Authority Contract V7

## Contents

1. Why authority must be split
2. Authority classes
3. Reference inventory
4. Conflict resolution
5. Acceptance records

## 1. Why authority must be split

A trusted 3D file may contain exact geometry but incomplete BOM quantities, suppressed hardware, missing drawing tolerances, or a different configuration. A source drawing may contain nominal dimensions and notes but not uniquely define every 3D surface. Treating either artifact as globally authoritative creates silent errors.

V7 therefore assigns authority by data class.

## 2. Authority classes

Record at least:

| Data class | Typical authority | Required evidence |
|---|---|---|
| Exact B-Rep surfaces | trusted STEP/FCStd | hash, import inventory, validity |
| Occurrence placement | trusted assembly or approved placement ledger | global transform and bounds |
| BOM names and source quantities | source drawing/BOM | page and row locator |
| Nominal functional dimensions | source drawing or approved design record | dimension locator |
| Fits and explicit tolerances | source drawing or standards-approved design | locator and mating pair |
| Material and treatment | source notes/design specification | note locator or approval |
| Engineering suggestions | calculation/review proposal | rationale and unreleased status |
| Production release | responsible engineer | signed approval record |

Use `assets/templates/authority-contract.template.json`.

## 3. Reference inventory

For every imported object record:

- object name and label;
- parent chain and hierarchy depth;
- object type and shape type;
- local placement and composed global placement;
- solid count, validity, area, volume, and center of mass;
- bounding-box minima, maxima, and lengths;
- topology counts;
- possible BOM item and confidence;
- whether it is a definition, container, compound, or physical occurrence.

Create geometry-family signatures from rounded dimensions, area, volume, topology, and optional shape hashes. Do not use these signatures as occurrence placement identifiers.

## 4. Conflict resolution

When evidence disagrees:

1. Preserve both values and source locators.
2. Determine whether the conflict is geometry, quantity, nominal/tolerance, configuration, suppression, rounding, or misread text.
3. Select the controlling authority only for the affected data class.
4. Mark downstream artifacts blocked when the conflict affects production release.
5. Keep the nonselected value in the report; never erase it from history.

Examples:

- Source BOM quantity 10, trusted STEP occurrences 4: model the 4 trusted placements, retain source quantity 10, and block release until resolved.
- Source nominal center distance 57±0.05, trusted axes measure 57: accept both as mutually confirming.
- Source screenshot appears to show a 64 center distance, but extension lines show 64 belongs to a housing feature: reject the proximity interpretation.

## 5. Acceptance records

The accepted reference package must include:

- immutable trusted input copy when permitted;
- SHA-256 for unchanged source copies;
- import inventory;
- authority contract;
- conflict ledger;
- per-family and per-occurrence comparison;
- coordinate-system record;
- accepted and rejected interpretation notes;
- release status and remaining blockers.

Do not label the job `geometry-valid` until exact surfaces, placements, occurrence counts, and critical dimensions agree with the selected authorities.
