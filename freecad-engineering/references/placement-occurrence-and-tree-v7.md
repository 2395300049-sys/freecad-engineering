# Placement, Occurrence, and Assembly Tree V7

## Contents

1. Node classes
2. Global placement recovery
3. Geometry-family matching
4. Physical occurrence ledger
5. Assembly tree classification
6. Validation rules

## 1. Node classes

Classify imported nodes before counting or copying:

- geometry definition;
- physical occurrence;
- compound or aggregate;
- assembly/subassembly container;
- origin/axis/plane/point helper;
- datum or relation node;
- drawing-only object;
- suppressed or empty node.

One visible tree row is not necessarily one physical part. One `Part::Feature` can contain several solids, and one part definition can appear in many placements.

## 2. Global placement recovery

For a nested occurrence with local transforms `T0...Tn`, compute:

```text
T_global = T0 * T1 * ... * Tn
```

Use the host application's multiplication order and verify it numerically; do not infer order from notation alone.

Validation procedure:

1. Transform the leaf bounding box to global space.
2. Compare its center and extents with the trusted assembly.
3. Check at least one neighboring interface or axis.
4. Store both local and global placement in the ledger.
5. When creating an independent shape occurrence, bake or assign the complete global placement exactly once.

Common failure: copying `obj.Shape.copy()` while ignoring parent `App::Part` placements. The resulting part has correct geometry but appears at the origin.

## 3. Geometry-family matching

Match geometry families using multiple attributes:

- part labels and BOM mapping;
- volume and area;
- bounding-box lengths;
- topology counts;
- axial/radial dimensions;
- optional shape hash;
- known material or role.

Then match occurrences using:

- global center and orientation;
- interface location;
- neighboring accepted components;
- expected quantity and occurrence index.

Do not select the smallest volume difference without placement evidence.

## 4. Physical occurrence ledger

Each record should contain:

```json
{
  "occurrence_id": "ASM-ITEM-01-03",
  "bom_item": 1,
  "part_number": "PART-001",
  "definition_id": "GEOM-FAMILY-001",
  "source_object": "OpenCascadeNode42",
  "local_placement": {},
  "global_placement": {},
  "solid_count": 1,
  "bounds_mm": {},
  "quantity_source": 4,
  "quantity_reference": 3,
  "quantity_status": "conflict"
}
```

Use `assets/templates/physical-occurrence-ledger.template.json`.

## 5. Assembly tree classification

Declare one of these honestly:

- `native_solver_assembly`: supported components/links and solver-backed joints.
- `evidence_based_static_assembly`: independent occurrences with exact placements and relation metadata but no solver.
- `compound_only`: one or more aggregate shapes with no occurrence semantics.
- `drawing_grouping_only`: tree organization for drawing without assembly meaning.

For a native assembly, validate grounding, connectedness, reference stability, expected freedoms, motion limits, and solver state.

For an evidence-based static assembly, validate occurrence IDs, BOM mapping, exact placement, hierarchy, and clearly labeled relation metadata. Do not claim solver behavior.

## 6. Validation rules

Report separate counts for:

- BOM rows;
- unique geometry families;
- part definitions;
- assembly containers;
- physical occurrences;
- solids;
- native components/links;
- joint and relation nodes.

Check that:

- every occurrence belongs to exactly one BOM item or an explicit non-BOM category;
- every expected occurrence has one valid placement;
- group quantity equals occurrence quantity, while source quantity conflicts remain visible;
- all nonfree native components connect to the grounded component;
- static placement does not masquerade as a joint solution;
- relation nodes do not masquerade as contact or interference proof.
