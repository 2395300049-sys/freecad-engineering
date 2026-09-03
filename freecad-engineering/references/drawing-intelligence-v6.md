# Drawing Intelligence V6

## Lessons from the 19th drawing test

The source is a strong reconstruction drawing, not a complete production release. It demonstrates functional view selection, assembly sections, local sections, removed sections, fit dimensions, roughness, gear tables, balloons, BOM, and technical notes. It also exposes the limits of contest drawings: incomplete datum systems, limited GD&T, incomplete general tolerances, weak assembly clearance requirements, and incomplete gear inspection data.

The drawing does contain selected tolerances such as H7, K7, h6, k5, N9, and explicit plus/minus values. Do not describe it as having no tolerances. Describe it as lacking a complete tolerance and inspection system.

## Source-faithful drawing rules

- Preserve sheet size, projection, scale, view direction, section location, detail location, dimensions, notes, BOM, and title-block content.
- Preserve source omissions unless the user explicitly requests an enhanced edition.
- Compare geometry and annotation separately.
- Permit font substitution only when it does not change content or placement acceptance.
- Record source defects rather than silently correcting them.

## Engineering-enhanced drawing rules

- Establish functional A/B/C datums.
- Replace long coordinate or chain schemes with basic dimensions and positional control where justified.
- Add functional size tolerances, fits, GD&T, roughness, material condition, treatment, and inspection requirements only from evidence.
- Add gear tooth-thickness or equivalent inspection, runout, backlash, heat-treatment verification, and bevel-gear pairing/mounting requirements as applicable.
- Add assembly interface, installation, endplay, preload, backlash, torque, lubrication, and acceptance requirements as applicable.
- Keep every added annotation linked to its source and approval status.

## View planning

Use a feature-coverage matrix. A view is required only when it contributes unique information.

- Internal cavities and bearing seats: full or offset section.
- Local counterbores, blind holes, oil passages: local section or detail.
- Shaft keys and grooves: removed sections.
- Inclined faces and true shapes: auxiliary views.
- Assembly transmission paths: functional sections through shafts, gears, bearings, and retainers.

Reject the fixed principal/top/side/isometric template when it does not expose the needed features.

## Dimension planning

Classify dimensions as:

- functional;
- assembly;
- manufacturing;
- inspection;
- reference.

Link each dimension to a feature, datum, source, and release status. Bounding-box width, height, and depth are only supplementary envelope dimensions.

## Drawing quality audit

Check at least:

- feature coverage by visible or sectioned geometry;
- dimension completeness without duplication or contradiction;
- datum and tolerance closure;
- text, arrow, hatch, centerline, and symbol collisions;
- correct section conventions;
- BOM/balloon consistency;
- title block, revision, material, scale, units, and projection;
- model and drawing revision match;
- PDF and DXF/DWG visual rendering.
