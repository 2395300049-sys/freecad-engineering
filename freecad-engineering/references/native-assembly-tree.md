# Native FreeCAD Assembly Tree

## Required structure

A functional FreeCAD assembly should contain:

```text
Assembly::AssemblyObject
|-- linked component occurrence
|-- linked component occurrence
|-- nested subassembly
`-- Assembly::JointGroup
    |-- grounded relation
    |-- fixed joint
    |-- revolute/slider/etc. joint
    `-- coupled-motion joint
```

Do not claim a native assembly when the document contains only statically placed `Part::Feature` copies or ordinary groups.

## Component occurrences

- Keep one authoritative part definition per part number/revision.
- Insert occurrences as links or supported native components.
- Assign occurrence ID, BOM item, part number, revision, quantity index, make/buy status, and configuration.
- Preserve nested assembly structure and global placement.
- Avoid copying shape geometry when a link is appropriate.

## Grounding and joints

- Ground the intended installation reference, usually a frame, housing, or base.
- Create joints from named functional references or stable geometry.
- Name joints `TYPE_COMPONENT-A_COMPONENT-B_FUNCTION`.
- Store purpose, expected freedom, adjustment limits, and source requirement.
- Verify both references exist and remain stable after model changes.

Common joint intentions include:

- `Fixed`: no relative freedom.
- `Revolute`: one rotational freedom.
- `Slider`: one translational freedom.
- `Cylindrical`: rotation and translation on one axis.
- `Ball`: rotational freedom about a point.
- `Distance`, `Parallel`, `Perpendicular`, `Angle`: geometric relation controls.
- `RackPinion`, `Screw`, `Gears`, `Belt`: coupled motion based on already established basic freedoms.

## Relationship graph

- Represent components as nodes and joints as edges.
- Require every non-intentionally-free component to connect to the grounded component through the graph.
- Detect duplicate, contradictory, missing, and unexpected relations.
- Record intentionally free degrees of freedom and motion limits.
- Do not estimate global mechanism degrees of freedom by simply summing per-joint values; use solver behavior and engineering intent.

## Audit outputs

Deliver:

- Native assembly object count.
- Linked occurrence count.
- Joint groups and joint records.
- Grounded components.
- Reference completeness.
- Connected components and isolated nodes.
- Expected-versus-actual relationship matrix.
- Static-placement-only warning.

Use `assets/templates/assembly-relationships.template.json` and `scripts/audit_native_assembly_tree.py`.
