# V6 Workflow Router

## Choose one primary operation

| User intent | Operation | Required starting evidence | Principal output |
|---|---|---|---|
| Convert a PDF/image drawing into a model | `2d_to_3d` | Dimensioned 2D source | FCStd, STEP, Python, validation views |
| Produce drawings from an existing model | `3d_to_2d` | Valid 3D solid/assembly | PDF, DXF/DWG, TechDraw source |
| Build or repair an assembly | `assembly` | Parts or reference assembly | Native Assembly tree, joints, BOM, checks |
| Find omissions in a drawing | `drawing_audit` | Existing 2D drawing | Issue list and corrected release plan |
| Compare two representations | `comparison` | Two 2D or 3D references | Visual and semantic difference report |
| Design a new mechanism | `new_design` | Requirements and work conditions | Selected concept and engineering package |
| Improve an existing mechanism | `redesign` | Existing design and constraints | Revised package with preserved interfaces |
| Review without changing | `engineering_review` | Existing package | Findings and release status |

## Combine operations through dependent jobs

Do not hide a multi-stage project inside one operation. Create dependent jobs, for example:

```text
J01 2d_to_3d
 -> J02 assembly
 -> J03 3d_to_2d (source_faithful)
 -> J04 comparison
 -> J05 3d_to_2d (engineering_enhanced)
 -> J06 drawing_audit
```

This separation makes failures resumable and prevents source matching from being confused with engineering redesign.

## Input rules

- Treat PDF/image/DXF/DWG as 2D evidence.
- Treat FCStd/STEP/STP/IGES/BREP as 3D evidence.
- Treat STL as tessellated reference unless feature recovery is explicitly accepted.
- Treat SLDASM/SLDPRT as references that may require a compatible translator or neutral export.
- Preserve the original source unchanged and record its hash.

## Ambiguity rules for 2D to 3D

Place a question in the ambiguity queue when any of the following is not uniquely determined:

- depth or extrusion direction;
- hidden cavity shape;
- whether repeated lines represent steps, grooves, or separate parts;
- section alignment or omitted section symbols;
- inconsistent dimensions between views;
- missing thickness, radius, thread depth, or tooth data;
- assembly occurrence count or orientation.

Allow the job to continue with alternatives, but block final geometry acceptance until the selected alternative is recorded.
