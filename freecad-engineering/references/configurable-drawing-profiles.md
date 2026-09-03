# Configurable Drawing Profiles

## Checkbox design principle

A checkbox enables a module; it does not supply missing engineering evidence. Store every selection in a versioned JSON profile and show dependencies before execution.

## Recommended UI groups

### Release mode

- Source-faithful reproduction
- Engineering-enhanced release
- Produce both

### Views

- Automatic functional view planning
- Full/offset section
- Local section
- Removed section
- Detail view
- Auxiliary view
- Isometric reference view
- Exploded assembly view

### Dimensions and annotations

- Functional dimensions
- Manufacturing dimensions
- Inspection dimensions
- General tolerance
- Explicit dimensional tolerances
- Fits
- Datums
- GD&T
- Surface roughness
- Threads and hole notes
- Gear parameter table
- Material and heat treatment
- Process notes
- Critical-characteristic marks

### Assembly

- Native assembly tree
- Joints and degrees of freedom
- BOM and balloons
- Interference
- Full-travel motion clearance
- Backlash/endplay/preload
- Assembly sequence
- Service/removal path
- Tightening and lubrication notes

### Business engineering

- Manufacturing route
- Cost estimate
- Standard-part selection
- Supplier and lead-time audit
- Safety/strength checks

### Outputs

- FCStd
- STEP/STP
- Portable Python
- PDF
- DXF
- DWG
- SVG/PNG preview
- Validation report

## Tolerance selector

Use a segmented selector rather than a single checkbox:

| Mode | Behavior | Release status |
|---|---|---|
| `off` | No added tolerances | Draft/source use only |
| `source_only` | Reproduce explicit source values | Source-faithful |
| `engineering_suggested` | Add labeled proposals with assumptions | Review only |
| `production_verified` | Add approved values backed by standards, function, process, stack, and inspection | Eligible for release |

## Dependency rules

- `GD&T` requires `datums`.
- `fits` requires dimensional tolerance and mating-interface evidence.
- `production_verified` requires a confirmed standards profile, complete design basis, process capability, and inspection plan.
- `backlash/endplay/preload` requires an assembly and tolerance stack.
- `BOM balloons` requires assembly occurrence IDs and a BOM.
- `cost` requires quantity, process route, currency, and date.
- `lead time` requires dated supplier evidence.
- `source_faithful` forbids engineering-suggested or production-added annotations on the same sheet.

## Presets

- `快速预览`: views, centerlines, outline dimensions, PDF/PNG.
- `原图复现`: source layout, source annotations, PDF/DXF, comparison.
- `工程审图`: existing drawing audit, missing-item report, no geometry change.
- `生产零件图`: datums, tolerances, GD&T, roughness, material/process, inspection.
- `装配发布`: functional sections, BOM, balloons, interfaces, adjustment, checks.
- `完整V6`: all applicable engineering and delivery gates.

Presets may initialize settings, but users must see and approve their final expanded configuration.
