# V5 Validation Gates

## Gate behavior

Each gate returns `pass`, `conditional`, `fail`, or `not_applicable` with evidence, owner, date, and blocking issues. `conditional` requires an approved deviation and closure date.

## Gate matrix

| Gate | Minimum evidence | Blocking examples |
|---|---|---|
| Inputs | Valid design-input contract | Unknown governing load, interface, quantity, or standard |
| Standards | Controlled profile and revisions | Mixed symbol systems, missing governing edition |
| Concepts | Hard constraints and decision record | Selected option violates mandatory requirement |
| Geometry | Dimensions, topology, projections, rebuild | Invalid shape, wrong interface, disconnected solid |
| Native assembly | Assembly object, links, grounded base, joints | Static-only placement, missing reference, disconnected part |
| Motion | Full travel samples and pair reports | Unapproved penetration, insufficient clearance, wrong ratio |
| Manufacturing | Process route and capability review | Inaccessible feature, unsupported tolerance/process |
| Tolerance | Functional stack and inspection plan | Jamming, loss of preload, unmeasurable requirement |
| Assembly/service | Sequence, paths, tools, adjustment | Trapped part, inaccessible fastener, no disassembly path |
| Strength/life | Failure-mode calculations and review | Margin below requirement, undocumented boundary condition |
| Cost | Quantity/date/currency-based estimate | Missing setup, material, special process, or inspection basis |
| Supply | Current BOM sourcing and alternates | Critical item unavailable or lead time beyond need date |
| Drawings | Complete release metadata and visual QA | Missing tolerance, datum, BOM, revision, or unreadable PDF |
| STEP/portable | Re-import and clean rebuild | Solid-count drift, invalid shape, machine-specific path |
| Privacy | Remote API visibility audit | Public repository or proprietary source staged for upload |

## Severity

- `blocking`: unsafe, nonfunctional, nonmanufacturable, nonassemblable, unreproducible, or confidentiality failure.
- `major`: likely cost, quality, life, service, or schedule failure.
- `minor`: documentation or maintainability issue that does not invalidate current function.
- `observation`: improvement opportunity with no current nonconformance.

## Completion rule

Do not declare `complete` while any required gate is `fail`, any blocking input is unknown, any conditional deviation lacks approval, or any required report is missing.

Use `assets/templates/validation-matrix.template.json` as the final index.
