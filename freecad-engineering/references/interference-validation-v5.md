# Assembly Interference Validation V5

## Definitions

For physical solids `S_i` and `S_j`, compute:

- Penetration volume: `V_ij = Volume(S_i common S_j)`
- Minimum distance: `d_ij = distToShape(S_i, S_j)` when penetration is below tolerance

Classify with explicit project tolerances:

- `interference`: `V_ij > volume_tolerance`
- `contact`: `V_ij <= volume_tolerance` and `d_ij <= distance_tolerance`
- `clearance`: `V_ij <= volume_tolerance` and `d_ij > distance_tolerance`

Do not classify from screenshots, bounding boxes, or zero distance alone.

## Audit scope

Run two complementary audits:

1. Full assembly audit: all physical leaf-solid pairs after AABB broad-phase filtering.
2. Focused motion audit: every gear, shaft, bearing, piston, slider, cam, crank, and fastener against all other leaves.

Record approved contacts separately. Typical approved contacts include seated fasteners, coaxial fits, and intentionally touching faces. A gear pair may be an intended near-contact pair, while either gear touching the housing is forbidden.

Do not approve a pair only to make the report pass. Each exception must name both objects, restrict the permitted classification, and state an engineering reason. Simplified threads or intentionally modeled press-fit overlap may be recorded as approved interference when the project representation requires it; an unexplained housing collision may not.

Use this JSON schema with `--approved-pairs`:

```json
{
  "approved_pairs": [
    {
      "left": "bolt label regex",
      "right": "threaded hole label regex",
      "classifications": ["contact", "interference"],
      "reason": "Simplified threaded engagement; verified against drawing and BOM"
    }
  ]
}
```

Matching is symmetric. Keep the regular expressions narrow enough to identify the intended occurrences.

## Flattening an assembly

- Exclude `App::Part`, document groups, and shape-bearing containers that own shape-bearing children.
- Expand multi-solid physical objects into individual solid records.
- Apply full global occurrence placement before comparison.
- Keep object name, label, BOM item, occurrence index, solid index, source file, and bounds in every record.
- Detect duplicate physical occurrences independently from reusable geometry families.

## Broad and narrow phases

1. Use axis-aligned bounding-box gap as a conservative broad phase.
2. Run exact Boolean `common()` for boxes that overlap or lie within the clearance reporting limit.
3. Run `distToShape()` for non-penetrating candidates.
4. Treat Boolean failures as validation failures, not as zero interference.
5. Save the tolerance values in the report.

## Diagnosis order

When a collision is found, check:

1. Unit scaling and axis conversion.
2. Parent transforms and `getGlobalPlacement()`.
3. Duplicate container compounds or duplicated occurrences.
4. Extra source bodies, missing cuts, failed feature scope, or wrong configuration.
5. Drawing dimensions and section views around the collision.
6. Kinematic position, gear phase, or backlash only after placement and geometry are proven.

This order prevents a local visual hypothesis from moving a correctly placed mechanism.

## Repair rules

- Freeze all unrelated part shapes and placements with hashes or shape metrics.
- Modify the smallest implicated component.
- Prefer drawing-defined bores, pockets, and reliefs.
- For rotating parts, use a swept or rotational envelope plus the required engineering clearance.
- Preserve mating datums, fastening holes, bearing seats, and installation dimensions.
- Require the repaired part to remain valid and connected.
- Document any removed disconnected sliver and its volume.

## Reference-source conflicts

A supplied SLDASM, STEP, or STP can contain modeling defects even when it is the best available reference. Examples include:

- Multiple visible bodies intended to represent one manufactured part.
- A bore omitted from one body because of feature-scope settings.
- Suppressed or configuration-specific cuts.
- Assembly placements that are correct while one part definition is not.

When the drawing and 3D source conflict, preserve both observations, identify the chosen authority, and avoid claiming source identity.

## Required evidence

For every repaired collision, deliver:

- Original object pair and labels.
- Original common volume.
- Corrected common volume.
- Corrected minimum distance.
- Tolerances and FreeCAD version.
- Before image with the common solid highlighted.
- After image from the same camera.
- Full post-repair assembly audit.
- STEP re-import audit.
- List of intentionally unchanged parts and placements.

## Learned bevel-gear case

An apparent bevel-gear error was initially interpreted as tooth phase. Exact Boolean auditing showed that the actual penetration was between the small bevel gear and a neighboring bearing-seat/flange part. The source part contained multiple visible bodies and did not provide the required through-bore/rotational relief across the complete flange region.

The correct response was to keep the accepted gear and shaft placements, correct the implicated seat geometry, preserve side fastener holes, and re-run the complete gear-versus-all-parts audit. The decisive evidence was common volume before and after repair, not visual similarity.

General rule: when a gear appears wrong, audit the gear against every surrounding solid before changing tooth phase or center distance.

## Native-joint boundary

A solved native Assembly joint proves only that the solver accepted the declared relation. It does not prove:

- Real tooth or cam geometry has clearance.
- A shaft clears the housing over full travel.
- Backlash remains valid at tolerance limits.
- Assembly insertion and removal are possible.
- Tooling and service envelopes are clear.

Run Boolean and minimum-distance checks on actual globally placed solids independently from the Joint solver.

## Motion sampling

- Define the required travel or full cycle, not an arbitrary screenshot range.
- Sample coarse positions first and refine around small-clearance or topology-changing regions.
- Include startup, adjustment extremes, tolerance extremes, and critical phase positions.
- Record driver and follower angle/position at every sample.
- Preserve the maximum forbidden common volume and minimum required clearance with the responsible object pair.
- Do not treat an unsampled interval as verified.
