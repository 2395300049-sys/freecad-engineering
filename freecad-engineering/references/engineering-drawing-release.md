# Engineering Drawing Release

## Drawing purpose

The released drawing must allow manufacturing, inspection, assembly, procurement, and configuration control without relying on undocumented CAD intent.

## Part drawing content

Include as applicable:

- Drawing number, title, revision, status, sheet, scale, units, projection, model revision, and approval fields.
- Material specification, condition, blank, heat treatment, hardness, coating, surface treatment, and mass.
- Functional and manufacturing views, sections, details, breaks, and local enlarged views.
- Overall, interface, size, location, depth, angle, radius, chamfer, thread, keyway, groove, and pattern dimensions.
- Dimensional tolerances, limits/fits, datum feature symbols, feature-control frames, and geometric tolerances.
- Surface texture, lay, machining allowance, edge/burr, cleanliness, marking, and special process notes.
- Critical-to-quality characteristics and inspection requirements.

## Assembly drawing content

Include as applicable:

- Complete BOM and balloons tied to occurrence IDs.
- Installation envelope, mounting datums, interface dimensions, utilities, center distances, and adjustment ranges.
- Section views exposing fits, fasteners, bearings, seals, keys, retaining devices, lubrication, and internal position relationships.
- Torque, preload, endplay, backlash, timing, alignment, sealant, lubricant, and locking instructions.
- Subassembly references, assembly sequence notes, safety notes, and service information.

## Dimensioning rules

- Dimension from functional datums and avoid relying on scaling.
- Avoid duplicate dimensions and inconsistent closed chains.
- Use sections rather than dimensioning hidden lines when practical.
- Keep basic dimensions, reference dimensions, limits, and inspection dimensions distinct.
- Ensure text, symbols, leaders, and dimensions do not overlap geometry or each other.

## Annotation logic

- Do not add a fit, GD&T control, roughness, or process symbol without a functional or manufacturing reason.
- Confirm the symbol syntax and interpretation against the selected standards profile.
- Tie critical drawing requirements back to calculations, tolerance stacks, interfaces, or process capability.
- Record deviations from company templates and customer requirements.

## Release checks

- Model and drawing revision match.
- All BOM items exist and quantities match the native assembly.
- Every critical interface is dimensioned and toleranced once.
- Datums are accessible and consistent with assembly/inspection.
- General tolerance does not conflict with explicit controls.
- Notes are measurable and unambiguous.
- PDF page size, fonts, line weights, hidden lines, centerlines, hatching, and title block render correctly.

Use `assets/templates/drawing-release.template.json` and `scripts/validate_drawing_release.py`, then perform visual PDF QA.
