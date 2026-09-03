# Case Study: Trusted STEP Calibration of an Inductive Dividing Head

## Contents

1. Initial state
2. Trusted-reference inventory
3. Major errors
4. Corrected model and assembly tree
5. Drawing improvements
6. STEP and portability results
7. GUI blank-view failure
8. Reusable lessons

## 1. Initial state

An early assembly was reconstructed from a competition drawing. It was useful as a workflow prototype but contained approximate housing, shaft, worm, gear, flange, and fastener geometry. The user later provided a trusted STEP model and requested calibration plus a more complete assembly drawing.

## 2. Trusted-reference inventory

The trusted model established:

- 28 BOM families;
- 42 physical solid occurrences;
- 28 unique geometry families;
- all shapes valid;
- total envelope approximately 316 × 275 × 245.00012 mm;
- main shaft length 275 mm;
- worm length 265 mm;
- base envelope 250 × 230 mm;
- main axis height 140 mm;
- main-shaft/worm-axis center distance 57±0.05 mm.

The source drawing remained authoritative for BOM names, source quantities, explicit fits, notes, and tolerances.

## 3. Major errors

### Wrong center-distance interpretation

A local housing dimension `64` was interpreted as the shaft center distance. Source extension lines and trusted axes showed the correct value was `57±0.05`.

### Approximate geometry retained too long

Per-family comparison showed most BOM families required replacement or calibration against trusted B-Rep geometry.

### Nested placement risk

Leaf shapes had to be recovered with global placement, not copied with local placement alone.

### Quantity conflict

The source BOM specified ten M8×25 socket-head screws for one item, while the trusted STEP contained four occurrences. The model retained the four trusted placements, while drawings and reports preserved the source quantity conflict and blocked release.

### Drawing incompleteness

The first drawing was too simple and lacked key dimensions, fits, datum relationships, gear data, and explicit unresolved items.

### Blank FCStd

The final geometry was initially saved by headless FreeCAD Python. It contained complete B-Rep data but no `GuiDocument.xml`, so the user could open the file and see an empty viewport.

## 4. Corrected model and assembly tree

The calibrated FCStd contained:

- 28 BOM item groups;
- 42 independent `Part::Feature` occurrences;
- four functional system groups;
- three functional datum records;
- six assembly relation records.

The relation records documented grounding, shaft revolute intentions, worm-gear ratio, sensor gear relation, and eccentric adjustment. They were explicitly labeled as relation evidence rather than proof of backlash or tooth contact.

## 5. Drawing improvements

Two A2 sheets were produced:

1. General assembly section, end view, isometric reference, BOM, balloons, envelope and major dimensions.
2. Critical dimensions, fits, A/B/C datum relationships, gear parameters, source locators, and open engineering issues.

Explicit fit examples included:

- diameter 155 H8/f7;
- diameter 55 H8/f7;
- diameter 27 H8/f7;
- diameter 40 H8/f7;
- diameter 75 H8/s7;
- diameter 30 H8/f7.

The first layout round had dimension/balloon proximity and table/view crowding. The second round moved and rotated vertical dimensions, separated datum frames, and reduced the secondary view scale.

## 6. STEP and portability results

The rebuilt STEP contained 42 valid solids with identical global bounds. Its volume differed by about 6.66 mm³ from the trusted import, approximately 0.85 ppm on a roughly 7.8 million mm³ assembly. This was accepted as B-Rep serialization drift because all structural metrics matched.

A byte-identical trusted copy retained the original SHA-256. A clean-room rebuild from only the trusted STEP, BOM source, and portable script regenerated the same solid count, envelope, and volume.

## 7. GUI blank-view failure

The headless FCStd archive lacked `GuiDocument.xml`. The repair process:

1. initialized FreeCADGui;
2. enabled 42 physical occurrences and their containers;
3. hid hundreds of origin, axis, plane, point, and metadata ViewProviders;
4. selected axonometric view;
5. ran `fitAll()` after visibility was enabled;
6. saved and reopened the FCStd;
7. captured a real Windows OpenGL viewport screenshot;
8. verified a nonblank pixel ratio above 20 percent.

This demonstrated that geometry validity and user-visible delivery are separate quality gates.

## 8. Reusable lessons

- Establish authority by data class.
- Confirm functional dimensions through extension lines, chains, and axes.
- Separate geometry families from physical occurrences.
- Recover global placement through the entire hierarchy.
- Keep motion relations separate from contact evidence.
- Preserve source/reference quantity conflicts visibly.
- Validate rebuilt STEP geometrically, not by hash.
- Issue multi-sheet assembly drawings when one sheet becomes overloaded.
- Perform clean-room rebuilds.
- Require FCStd GUI state and a real viewport screenshot before delivery.
