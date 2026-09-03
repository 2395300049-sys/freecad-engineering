# Reference Calibration

Use this procedure only when the user supplies a trusted STEP/STP or equivalent solid model.

## Import inventory

For every imported object, record:

- document hierarchy and label;
- shape type and solid count;
- volume and surface area;
- bounding-box minimum, maximum, and size;
- center of mass;
- object placement and global transformed placement.

STEP files may contain both reusable definitions and assembly occurrences. The same physical shape can appear several times at different placements.

## Deduplication

Create a shape signature from rounded volume, bounding-box size, surface area, topology counts, and optional shape hash. Use it to identify geometry families, not final occurrence positions.

Select the assembly occurrence with this priority:

1. part label or known source mapping;
2. volume within a strict tolerance;
3. expected global bounds or center;
4. topology and dimensions;
5. proximity to neighboring accepted occurrences.

Do not select by the smallest floating-point volume error alone. Definition solids can have identical geometry but incorrect assembly placement.

## Coordinate systems

Determine the up axis and handedness from the assembly, not file extension. Record one transform matrix and apply it consistently to all parts and occurrences.

Typical Inventor-to-FreeCAD correction for Y-up reference data is a +90 degree rotation about X, mapping source Y to FreeCAD Z and source Z to FreeCAD -Y. Verify this visually and numerically before adopting it.

## Conflict handling

When drawing text and reference geometry disagree:

- preserve both measurements in the report;
- determine whether the drawing value is rounded, nominal, sectional, or incorrectly read;
- avoid reshaping the model merely to satisfy a title-block mass;
- prioritize explicit functional dimensions over a rendered screenshot;
- state which authority controls the final accepted model.

Export a correction table with old value, reference value, absolute difference, percentage difference, cause, and fix.
