# Fits, Tolerances, GD&T, and Surface Requirements

## Start from function

For each interface, define the required behavior:

- Free running, accurate rotation, sliding, location, transition, press fit, sealing, preload, backlash, alignment, interchangeability, or adjustment.
- Assembly temperature and operating temperature.
- Load direction, torque transfer, wear, lubrication, contamination, and service frequency.

Do not assign a fit designation before defining the function and process capability.

## Datum strategy

- Select datums from functional mounting and locating surfaces.
- Use a stable primary-secondary-tertiary scheme that reflects assembly and inspection.
- Avoid datums that are inaccessible, flexible, unfinished, or unrelated to function.
- Keep CAD coordinate systems, assembly joints, drawing datums, fixtures, and inspection alignment consistent.

## Dimensional tolerances

- Use general tolerances only for noncritical dimensions covered by the selected standard.
- Assign explicit limits to functional interfaces, adjustment ranges, and critical clearances.
- Avoid duplicate, closed-loop, and contradictory dimensions.
- Distinguish size, location, orientation, form, runout, profile, and depth requirements.

## Geometrical tolerancing

Use form, orientation, location, profile, and runout controls when they communicate function more clearly than coordinate tolerances. Define:

- Controlled feature.
- Tolerance value and zone.
- Material condition modifier where permitted and intended.
- Datum references and order.
- Projected zone, tangent plane, common zone, or other modifiers where applicable.
- Verification method and accessibility.

Do not use a geometric tolerance symbol without the selected standard's interpretation.

## Surface and process indications

- Specify surface texture only where sealing, fatigue, friction, wear, appearance, coating, or fitting requires it.
- State machining allowance, lay, treatment, hardness, coating, edge break, burr removal, and cleanliness when functionally required.
- Avoid globally applying fine roughness that forces unnecessary grinding or polishing.

## Tolerance stacks

Build stacks for:

- Assembly closure and gap.
- Bearing preload/endplay.
- Gear backlash and apex/center alignment.
- Seal compression.
- Shaft and bore alignment.
- Fastener engagement and clamp stack.
- Moving-part clearance across temperature.

Use signed contributors and preserve units. Run worst-case for guaranteed limits and a justified statistical method only when process distributions and independence assumptions are defensible.

## Inspection planning

- Identify critical-to-quality characteristics.
- Define instrument, gauge, CMM strategy, fixture datum, sampling, and acceptance rule.
- Confirm measurability before releasing the drawing.

Use `assets/templates/tolerance-stack.template.json` and `scripts/tolerance_stack.py`.
