# V6 Validation Gates

## Configuration gate

- Primary operation is explicit.
- Release intent is explicit.
- Drawing profile validates.
- Input and output formats match the operation.
- Privacy mode and output directory are explicit.

## Source understanding gate

- Every sheet is rendered and visually inspected.
- Parts, views, sections, dimensions, notes, symbols, BOM, and title blocks are indexed.
- Ambiguities and source conflicts are recorded.
- Original source remains unchanged and hashable.

## Geometry gate

- Shapes are valid and have the expected solid count.
- Named parameters and datums exist.
- Critical dimensions match evidence.
- STEP round trip preserves solids, bounds, and critical dimensions.

## Drawing planning gate

- Every required feature is covered by a visible, section, detail, removed-section, or auxiliary view.
- No view exists only because of a fixed template.
- Dimension classes and annotation sources are recorded.

## Source-faithful gate

- Sheet, scale, view placement, sectioning, geometry, dimension values, notes, BOM, and title block are compared.
- Source defects are documented rather than silently changed.
- No engineering-suggested annotation appears on the source-faithful sheet.

## Engineering-enhanced gate

- Functional datums are established.
- Added tolerances and GD&T have design and inspection interpretations.
- Fits match mating functions and assembly conditions.
- Gear, bearing, seal, fastener, and interface requirements are complete as applicable.
- Suggested values remain visibly non-released until approved.

## Layout gate

- Text, arrows, dimensions, hatch, centerlines, symbols, balloons, and tables do not collide.
- Line weights and print scale render correctly.
- PDF and DXF/DWG are visually opened and checked.

## Assembly gate

- Native assembly tree, links, grounding, joints, and intended freedoms pass.
- Static and full-travel interference checks pass.
- Backlash, endplay, preload, contact, and clearance are checked separately.
- Assembly, adjustment, service, and removal paths are feasible.

## Release gate

- Model, drawing, BOM, source code, and exports share a revision.
- Validation reports are present.
- Clean-path rebuild succeeds.
- Delivery layout audit passes.
- Private/public status matches explicit user authorization.
