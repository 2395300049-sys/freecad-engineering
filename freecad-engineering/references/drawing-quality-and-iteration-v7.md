# Drawing Quality and Iteration V7

## Contents

1. Two drawing products
2. Feature coverage
3. Annotation provenance
4. Assembly drawing requirements
5. Layout iteration
6. Format validation
7. Acceptance evidence

## 1. Two drawing products

### Source-faithful

Preserve source paper, projection, scale, view placement, sections, dimensions, notes, BOM, title block, omissions, and defects. Do not add engineering proposals into this acceptance result.

### Engineering-enhanced

Preserve accepted geometry while adding justified:

- functional datums;
- functional/assembly/manufacturing/inspection dimensions;
- fits and explicit tolerances;
- GD&T with inspection meaning;
- roughness, material, treatment, process, and inspection notes;
- assembly endplay, preload, backlash, torque, lubrication, and adjustment requirements;
- BOM, balloons, revision and release controls.

Mark proposals as unreleased until approved.

## 2. Feature coverage

Build a matrix linking each functional feature to at least one defining view:

| Feature | Preferred view |
|---|---|
| Housing cavity and bearing seats | full/offset section |
| Local counterbore or blind passage | local section/detail |
| Shaft keyway and grooves | removed section |
| Inclined face true shape | auxiliary view |
| Gear/shaft transmission path | functional assembly section |
| Mounting pattern | normal end/top view |
| Adjustment and service interface | detail or assembly view |

Reject views that add no unique information.

## 3. Annotation provenance

Every annotation record should include:

- stable ID;
- type: dimension, fit, tolerance, GD&T, roughness, note, BOM, datum, or suggestion;
- value and units;
- controlled feature/interface;
- source file and page/region;
- evidence class;
- release status;
- approval owner;
- drawing sheet and view location.

Use `assets/templates/annotation-trace.template.json` and validate with `scripts/audit_annotation_trace_v7.py`.

## 4. Assembly drawing requirements

Include as applicable:

- functional section through shafts, gears, bearings, retainers, and seals;
- end or side view for mounting and external interfaces;
- isometric reference view that does not replace orthographic definition;
- BOM and linked balloons;
- main envelope and installation dimensions;
- shaft/gear center distances and axis relationships;
- key fits and interface tolerances;
- adjustment, lubrication, assembly, and inspection notes;
- explicit unresolved conflicts and release blockers.

Do not overload one sheet. Use a second sheet for critical dimensions, fits, datum relationships, gear data, and open issues when necessary.

## 5. Layout iteration

At each round record:

1. detected collision or semantic omission;
2. root cause;
3. changed view/annotation/table;
4. rendered result;
5. remaining risk.

Typical corrections:

- rotate and move vertical dimension text away from balloons;
- move datum frames outside crowded leader fields;
- reduce a secondary view scale;
- split BOM and engineering tables;
- move long notes to a dedicated band;
- maintain stable title-block dimensions;
- preserve readable line weights and hatch spacing.

Archive rejected rounds outside accepted drawing folders.

## 6. Format validation

### PDF

- page count and exact paper size;
- nonblank render;
- required text and symbols;
- readable print scale;
- no clipping or overlap.

### PNG preview

- correct page framing;
- sufficient resolution;
- meaningful nonwhite pixel ratio;
- human visual inspection.

### DXF/DWG

- layers, line types, text, dimensions, hatches, and tables opened in a compatible CAD viewer;
- any lost custom annotations documented;
- annotation master format identified.

### FCStd TechDraw

- page/view objects exist;
- references resolve;
- GUI visibility is usable;
- exported result matches the accepted PDF/SVG master.

## 7. Acceptance evidence

Save:

- drawing profile;
- annotation trace;
- feature-coverage matrix;
- rendered pages;
- comparison images;
- collision/semantic audit;
- iteration log;
- revision and model-link report;
- unresolved engineering requirements.

Do not call the drawing production-ready while general tolerances, inspection methods, gear acceptance, material/process, or responsible-engineer approval remain missing.
