---
name: freecad-engineering
description: Design, reconstruct, correct, audit, and release FreeCAD parts, assemblies, drawings, and exchange files from requirements, 2D drawings, marked images, PDFs, FCStd, STEP/STP, IGES, SLDPRT, SLDASM, or trusted reference models. Use when mechanical CAD work needs traceable geometry, placement, interference, motion, tolerance, manufacturing, drawing, GUI, STEP, portability, or release-readiness evidence. Do not treat generated geometry or passed scripts as production approval.
---

# FreeCAD Engineering

Produce an auditable engineering result, not merely a plausible-looking model. Scale the work to the request: ordinary part edits need fewer gates than a production assembly, but every claimed result must have evidence appropriate to that claim.

## Route the task

Choose one primary mode and any necessary secondary modes before editing CAD:

- `2d_to_3d`: reconstruct parts or assemblies from dimensioned drawings.
- `3d_to_2d`: create or audit engineering drawings from accepted solids.
- `marked_correction`: apply a local change identified in an image or markup.
- `reference_calibration`: compare or replace geometry using a trusted 3D source.
- `assembly`: build or audit occurrences, hierarchy, joints, interfaces, and motion.
- `new_design`: turn requirements into a production-oriented mechanical design.
- `engineering_review`: audit an existing design without silently redesigning it.
- `delivery_repair`: correct exports, GUI state, paths, packaging, or version structure.
- `repository_release`: prepare a sanitized reusable Skill or project repository.

For inherited routing and gate selection, read [references/workflow-router-v6.md](references/workflow-router-v6.md) and [references/validation-gates-v6.md](references/validation-gates-v6.md).

Use ordinary Python for metadata, layout, cost, tolerance, and release validators. Run scripts that import `FreeCAD`, `Part`, `Mesh`, `Import`, or `Gui` through the installed FreeCAD Python environment or `FreeCADCmd`/`freecadcmd`; do not assume a Windows executable path. Read [references/local-software-architecture.md](references/local-software-architecture.md) when locating or integrating the runtime.

## Establish authority before modeling

1. Inventory the supplied drawings, CAD files, screenshots, BOMs, requirements, standards, and requested outputs.
2. Preserve source files unchanged when permitted and record hashes for accepted baselines.
3. Assign authority separately for geometry, occurrence placement, quantities, dimensions, tolerances, materials, treatments, standards, and approval.
4. Classify important values as `explicit`, `derived`, `measured`, `inferred`, `assumed`, or `conflicting`.
5. Stop only when a missing choice would materially change the design; otherwise use clearly labeled assumptions and continue.

Do not let a STEP file silently override a drawing quantity, or let a screenshot reshape trusted geometry outside the marked region. For conflicting sources or nested reference models, read [references/trusted-reference-and-authority-v7.md](references/trusted-reference-and-authority-v7.md), [references/reference-calibration.md](references/reference-calibration.md), and [references/placement-occurrence-and-tree-v7.md](references/placement-occurrence-and-tree-v7.md).

## Build or correct geometry

- Create stable datums and named parameters before dependent features.
- Resolve cross-view orientation, symmetry, sections, hidden depth, repeated features, and units explicitly.
- Prefer parameterized reconstruction when dimensions are complete. If trusted reference geometry is authoritative for surfaces, preserve the reconstruction history and discrepancy record.
- Treat definitions, containers, compounds, BOM rows, and physical occurrences as different objects. Count physical leaf occurrences only.
- Recover global placement through the full parent chain before copying nested geometry.
- Validate solids, bounds, volume, center, topology, critical dimensions, and orthographic projections; visual similarity alone is insufficient.

For marked corrections or invalid B-Reps, read [references/repair-and-change-control-v8.md](references/repair-and-change-control-v8.md). Change the smallest authoritative parameter set and prove declared before/after invariants with `scripts/validate_repair_evidence_v8.py`.

## Build and validate assemblies

- Use native FreeCAD Assembly components and joints when the installed version supports them. Describe independent placed solids as a static assembly, not a solved native assembly.
- Ground the installation reference and record intended degrees of freedom.
- Separate kinematic relations from backlash, clearance, contact, interference, strength, and serviceability evidence.
- Classify candidate pairs as expected engagement, allowed contact, numerical overlap, unresolved penetration, or not applicable. Every approved pair needs a reason and authority.
- Test critical rotating or translating components through the required travel, not only at one pose.
- Check assembly order, tool access, adjustment, inspection, removal, and maintenance independently.

Read only the references needed for the assembly scope:

- Native structure and joints: [references/native-assembly-tree.md](references/native-assembly-tree.md)
- Interference: [references/interference-validation-v5.md](references/interference-validation-v5.md)
- Gears and motion: [references/gear-mesh-and-motion.md](references/gear-mesh-and-motion.md)
- Assembly and service sequence: [references/assembly-sequence-and-service.md](references/assembly-sequence-and-service.md)

Use `scripts/audit_native_assembly_tree.py`, `scripts/audit_assembly_interference.py`, `scripts/validate_gear_pairs.py`, `scripts/audit_motion_clearance.py`, and `scripts/audit_assembly_sequence.py` as applicable.

## Apply production-engineering gates

For new designs, redesigns, or production claims:

1. Freeze the design-input contract, standards profile, operating conditions, and load cases.
2. Compare concepts against hard constraints before weighted scoring.
3. Check applicable strength, stiffness, fatigue, buckling, contact, wear, thermal, bearing, and fastener failure modes.
4. Define materials, manufacturing routes, datum strategy, fits, tolerances, GD&T, surface condition, treatments, inspection, and functional tolerance stacks.
5. Record assembly feasibility, make/buy decisions, dated quotations, lead times, lifecycle risk, alternatives, and transparent cost assumptions.

Load only the relevant production references: [references/design-input-contract.md](references/design-input-contract.md), [references/standards-profile.md](references/standards-profile.md), [references/operating-conditions.md](references/operating-conditions.md), [references/concept-selection.md](references/concept-selection.md), [references/strength-safety-and-life.md](references/strength-safety-and-life.md), [references/fits-tolerances-gdandt.md](references/fits-tolerances-gdandt.md), [references/manufacturing-and-cost.md](references/manufacturing-and-cost.md), and [references/standard-parts-and-supply.md](references/standard-parts-and-supply.md).

Never invent loads, material properties, tolerances, safety factors, costs, stock, lead times, standards editions, test results, or approvals.

## Create and audit drawings

Choose one intent:

- `source_faithful`: preserve the accepted source layout and annotation semantics, including its documented defects.
- `engineering_enhanced`: add justified datums, functional dimensions, fits, tolerances, GD&T, surface/process symbols, inspection characteristics, BOM data, balloons, and revision controls.

Issue separate revisions when both are requested. Trace annotations to their authority and mark proposals unreleased until approved. Export an editable master and a printable PDF, render the PDF, and inspect text, line weights, arrows, hatching, centerlines, dimensions, view collisions, tables, title block, scale, units, and projection method.

Read [references/drawing-quality-and-iteration-v7.md](references/drawing-quality-and-iteration-v7.md), [references/engineering-drawing-release.md](references/engineering-drawing-release.md), and [references/assembly-drawing.md](references/assembly-drawing.md) when drawing work is in scope. Validate release metadata with `scripts/validate_drawing_release.py`.

## Verify exchange files, GUI state, and portability

Treat these as independent gates:

- STEP round trip: re-import and compare solid/occurrence counts, validity, bounds, volume, critical dimensions, placements, and declared drift tolerances.
- FCStd GUI state: confirm visible accepted geometry, hidden helper objects, saved camera, successful GUI reopen, and a real viewport capture.
- Portable rebuild: rebuild in an empty path using only advertised inputs; verify current outputs and avoid undeclared caches or machine-specific paths.
- Delivery structure: keep working files separate from accepted output, preserve prior accepted revisions, and include a manifest of advertised artifacts.

Use [references/step-roundtrip-validation-v7.md](references/step-roundtrip-validation-v7.md), [references/freecad-gui-and-viewport-v7.md](references/freecad-gui-and-viewport-v7.md), and [references/portable-delivery-and-file-layout-v7.md](references/portable-delivery-and-file-layout-v7.md). Relevant scripts include `compare_step_geometry.py`, `validate_step_export.py`, `audit_fcstd_gui_state.py`, `fix_fcstd_gui_visibility.py`, `capture_freecad_viewport_v7.py`, and `build_delivery_manifest_v7.py`.

## Declare status precisely

Report the highest demonstrated state, plus failed and untested gates:

- `geometry_review_ready`: declared geometry, occurrence, STEP, GUI, and viewport checks pass.
- `engineering_review_ready`: applicable drawing, interference, motion, manufacturing, inspection, and service evidence also passes.
- `production_release_ready`: all mandatory gates pass, no blocking findings remain, and a responsible engineer approval record exists.

A lower state never implies a higher one. Use `scripts/validate_release_status_v8.py` and [references/release-readiness-v8.md](references/release-readiness-v8.md).

## Package or publish a repository

Require explicit authorization immediately before uploading. Keep repository visibility and licensing as separate decisions.

- Include only approved reusable instructions, scripts, templates, metadata, or project source.
- Exclude credentials, customer drawings, private CAD, quotations, generated task outputs, logs, caches, and machine-specific absolute paths unless explicitly included in scope.
- Inspect staged files, commit identity, branch, remote owner, visibility, and license decision before pushing.
- Verify the committed remote tree and visibility after pushing; a local success message is not enough.
- Run `scripts/audit_public_release_v8.py` against the exact release tree even for a private repository; use [references/public-repository-release-v8.md](references/public-repository-release-v8.md) for the release contract.

Do not add an open-source license unless the user explicitly authorizes that grant.

## Completion report

State:

- the operation performed and authoritative inputs used;
- exact output paths and versions;
- passed, failed, blocked, and untested gates;
- measurements and tolerances behind accepted claims;
- assumptions, conflicts, repairs, and remaining risk;
- the highest justified release-readiness state;
- whether a responsible engineer, supplier, physical test, inspection, or regulatory approval is still required.

Never report production readiness from visual appearance, successful script execution, a valid STEP alone, or an unreviewed simulation.
