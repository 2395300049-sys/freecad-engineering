# V7 CAD Failure Catalog

## Contents

1. Source recognition and evidence
2. FreeCAD Python and execution
3. Geometry and topology
4. Placement, occurrences, and assemblies
5. Gears, motion, and interference
6. Engineering drawings
7. STEP and exchange validation
8. GUI visibility and user opening
9. Portability, organization, and release
10. Production engineering and productization

Use this catalog before retrying a failed task. Record the applicable failure ID in the project iteration log.

## 1. Source recognition and evidence

### F01: PDF text extraction is treated as the drawing

- **Symptom:** dimensions, section letters, fits, and Chinese notes are missing or assigned to the wrong view.
- **Root cause:** relying on extracted text without rendering and visually inspecting every page.
- **Detection:** compare extracted tokens with page images; inspect symbols and spatial relationships.
- **Correction:** render all pages, crop regions, index views and title blocks, then rebuild the semantic record.
- **Prevention gate:** no modeling until every relevant sheet has a visual index.

### F02: OCR confuses engineering symbols

- **Symptom:** `Ø` becomes `0`, `±` disappears, `H8/f7` is split, or subscripts become unrelated digits.
- **Root cause:** low-resolution rasterization, compression, font ambiguity, or generic OCR.
- **Detection:** inspect the original pixels near every critical dimension and fit.
- **Correction:** re-render at higher DPI and transcribe critical annotations manually with source locators.
- **Prevention gate:** all critical values require image evidence, not OCR-only evidence.

### F03: A nearby dimension is assigned to the wrong feature

- **Symptom:** model looks plausible but an axis, bore, shoulder, or center distance is wrong.
- **Root cause:** reading by visual proximity instead of extension lines, centerlines, section context, and dimension chains.
- **Detection:** trace both extension lines and recompute the dimension chain across views.
- **Correction:** update the feature graph and every dependent placement or drawing annotation.
- **Prevention gate:** critical dimensions require at least two independent view/chain confirmations.

### F04: Center distance is confused with a local housing dimension

- **Symptom:** gears or shafts are displaced and the total assembly envelope changes.
- **Root cause:** a local wall/seat dimension is interpreted as an axis-to-axis value.
- **Detection:** derive both axis coordinates from centerlines; compare with the gear formula and trusted 3D axes.
- **Correction:** establish explicit axis datum records and rebuild dependent placements.
- **Prevention gate:** center distances must be stored as named functional dimensions.

### F05: Raster scale is used as a manufacturing dimension

- **Symptom:** dimensions inferred from pixels disagree with explicit annotations.
- **Root cause:** scanned paper distortion, viewport scaling, perspective, or screenshot cropping.
- **Detection:** compare several known dimensions against measured pixel ratios.
- **Correction:** use raster measurements only as low-confidence diagnostics.
- **Prevention gate:** pixel measurements cannot override explicit dimensions or trusted geometry.

### F06: Source and trusted 3D evidence are merged without an authority contract

- **Symptom:** BOM quantities, geometry, tolerances, or notes silently change.
- **Root cause:** treating one file as authoritative for every data class.
- **Detection:** compare source BOM, dimensions, and notes against reference occurrences and geometry.
- **Correction:** assign separate authorities and publish a conflict ledger.
- **Prevention gate:** `authority-contract.json` must exist before reference calibration.

### F07: Source defects are silently corrected

- **Symptom:** the generated “same” drawing no longer matches the training source.
- **Root cause:** mixing source-faithful reproduction with engineering improvement.
- **Detection:** compare annotation sets and revision intent.
- **Correction:** issue separate source-faithful and engineering-enhanced drawing sets.
- **Prevention gate:** one release intent per acceptance result.

## 2. FreeCAD Python and execution

### F08: Generated Python contains a syntax error

- **Symptom:** FreeCAD console reports `SyntaxError` near a valid-looking assignment.
- **Root cause:** an unclosed parenthesis, malformed previous line, pasted prompt marker, or truncated statement.
- **Detection:** run `py_compile` where possible and inspect lines before the reported location.
- **Correction:** repair the complete statement block, not only the highlighted line.
- **Prevention gate:** execute every delivered script in a clean process before delivery.

### F09: Markdown corrupts Python identifiers

- **Symptom:** `NameError: name '**file**' is not defined`.
- **Root cause:** `__file__` or `__name__` passed through Markdown emphasis and copied incorrectly.
- **Detection:** search delivered scripts for `**file**`, `**name**`, smart quotes, or prompt prefixes.
- **Correction:** restore Python identifiers and avoid formatting code as prose.
- **Prevention gate:** script source must be stored as a file and clean-room executed.

### F10: `__file__` is unavailable in the FreeCAD console

- **Symptom:** a script works as a file but fails when pasted into the Python console.
- **Root cause:** console execution does not define `__file__`.
- **Detection:** inspect the intended execution method.
- **Correction:** use explicit project-root parameters or a fallback based on the current document/path.
- **Prevention gate:** document whether the source is a script, macro, console snippet, or launcher.

### F11: A Python file is passed to FreeCAD but not executed

- **Symptom:** FreeCAD starts and exits or opens a blank document without running the code.
- **Root cause:** positional `.py` or `.FCMacro` behavior is assumed incorrectly.
- **Detection:** require a sentinel output or expected artifact.
- **Correction:** use FreeCAD Python directly, a documented console pipeline, or an explicit launcher.
- **Prevention gate:** launch commands are part of the clean-room test.

### F12: Paths with spaces or Chinese characters fail

- **Symptom:** files cannot be imported, copied, or launched despite existing.
- **Root cause:** missing quotes, shell encoding, mixed separators, or string-built commands.
- **Detection:** test the actual non-ASCII path and inspect resolved absolute paths.
- **Correction:** use `pathlib`, literal paths, quoted arguments, and UTF-8 files.
- **Prevention gate:** portability tests must use a path containing spaces and non-ASCII characters.

### F13: FreeCADCmd and FreeCAD Python environments are confused

- **Symptom:** `ModuleNotFoundError: Part` or GUI APIs are missing.
- **Root cause:** importing `Part` before `FreeCAD`, using ordinary Python, or assuming GUI functions exist in console mode.
- **Detection:** record executable, `App.GuiUp`, FreeCAD version, and available modules.
- **Correction:** use FreeCAD's bundled Python and import `FreeCAD` before workbench modules; use GUI initialization only when required.
- **Prevention gate:** every script declares whether it needs core FreeCAD or FreeCADGui.

### F14: Long-running processes are abandoned

- **Symptom:** duplicate FreeCADCmd processes, locked files, repeated exports, or unexplained CPU usage.
- **Root cause:** background sessions are not polled to completion or terminated after failure.
- **Detection:** inspect running sessions and process IDs after each stage.
- **Correction:** wait, capture exit codes, and terminate only processes started by the current task when necessary.
- **Prevention gate:** no final response while required execution sessions remain active.

## 3. Geometry and topology

### F15: Approximate geometry is accepted after a trusted reference arrives

- **Symptom:** overall appearance is similar but holes, gear teeth, seats, wall profiles, or local surfaces differ.
- **Root cause:** the early parametric approximation remains the hidden geometry authority.
- **Detection:** compare every BOM family by bounds, volume, topology, and section projection.
- **Correction:** replace approximations or clearly retain them only as rejected history.
- **Prevention gate:** trusted-reference calibration produces a per-family difference table.

### F16: Shape validity is assumed

- **Symptom:** export succeeds but later booleans, meshing, drawing, or STEP import fails.
- **Root cause:** null, invalid, open, or multi-solid shapes were not checked.
- **Detection:** verify `isNull`, `isValid`, `Solids`, and expected topology.
- **Correction:** repair feature order, tolerances, refinement, or boolean construction.
- **Prevention gate:** geometry validity is a blocking gate before assembly and drawing.

### F17: `removeSplitter` or refinement is applied blindly

- **Symptom:** topology changes unexpectedly, references break, or a shape operation fails.
- **Root cause:** refinement is treated as cosmetic rather than topology-changing.
- **Detection:** compare topology and dependent references before and after refinement.
- **Correction:** refine only after stable geometry is complete and no fragile references depend on split edges.
- **Prevention gate:** topology-changing cleanup must have a regression check.

### F18: One visible object contains several physical solids

- **Symptom:** BOM/balloon counts do not match geometry.
- **Root cause:** a compound or fused object is mistaken for one part.
- **Detection:** count `Shape.Solids` and inspect connectivity.
- **Correction:** split physical occurrences or document an inseparable purchased assembly.
- **Prevention gate:** each occurrence record includes expected solid count.

### F19: Mirroring or coordinate handedness is wrong

- **Symptom:** the model aligns in one view but not in another, or shafts/gears appear on the wrong side.
- **Root cause:** Y-up/Z-up conversion, handedness, or view direction was assumed.
- **Detection:** compare three non-collinear datums and a known asymmetric feature.
- **Correction:** define one verified transform matrix and apply it consistently.
- **Prevention gate:** coordinate-system evidence is stored with the reference inventory.

## 4. Placement, occurrences, and assemblies

### F20: Local Placement is copied as global Placement

- **Symptom:** correct part shapes appear at the origin or in wrong assembly positions.
- **Root cause:** parent transforms in nested STEP/FCStd containers are lost.
- **Detection:** compare local and global placements and transformed bounding boxes.
- **Correction:** compose the entire parent transform chain before creating the occurrence.
- **Prevention gate:** each occurrence ledger stores source object, local placement, global placement, and final bounds.

### F21: Definition geometry is selected instead of an assembly occurrence

- **Symptom:** a matched part has correct volume but incorrect position.
- **Root cause:** deduplication selected the first or numerically closest definition shape.
- **Detection:** match placement and neighboring interfaces as well as geometry signature.
- **Correction:** separate geometry-family matching from occurrence placement matching.
- **Prevention gate:** never select an occurrence by volume error alone.

### F22: Containers, compounds, and occurrences are counted together

- **Symptom:** reports claim 48 parts when the assembly physically contains 42, or vice versa.
- **Root cause:** object-tree node count is used as the quantity.
- **Detection:** classify every node by role and count leaf physical solids independently.
- **Correction:** publish separate counts for BOM rows, definitions, containers, occurrences, and solids.
- **Prevention gate:** use the physical-occurrence ledger template.

### F23: Static groups are called a native assembly

- **Symptom:** the tree looks organized but contains no solver-backed components or joints.
- **Root cause:** visual hierarchy is confused with assembly semantics.
- **Detection:** inspect object types, links, joint groups, grounding, and solver state.
- **Correction:** label it an evidence-based static assembly or rebuild with the native Assembly workbench.
- **Prevention gate:** assembly type must be declared in the manifest.

### F24: A native joint is treated as proof of geometric clearance

- **Symptom:** motion solves while parts still penetrate or have zero required clearance.
- **Root cause:** kinematic constraints and entity contact are conflated.
- **Detection:** run geometric checks at representative and worst-case positions.
- **Correction:** add separate contact, backlash, and full-travel validations.
- **Prevention gate:** every motion relation links to an independent geometry requirement.

### F25: BOM quantity and trusted occurrence quantity conflict

- **Symptom:** the source requests more fasteners than the trusted assembly contains.
- **Root cause:** incomplete reference assembly, source error, suppressed items, or configuration mismatch.
- **Detection:** compare source quantity with occurrence ledger for every BOM row.
- **Correction:** preserve both values, do not invent missing placements, and block release.
- **Prevention gate:** quantity conflicts must appear in model properties, drawings, and validation reports.

### F26: Assembly hierarchy is correct but cannot be assembled

- **Symptom:** final pose is valid but insertion, tightening, adjustment, or removal is impossible.
- **Root cause:** only final-position interference was checked.
- **Detection:** simulate or reason through assembly sequence, tool envelopes, and service paths.
- **Correction:** change sequence, split parts, add access, or revise interfaces.
- **Prevention gate:** sequence and service checks are required for production release.

## 5. Gears, motion, and interference

### F27: Gear phase or center distance is wrong

- **Symptom:** teeth visibly penetrate or the gear pair misses engagement.
- **Root cause:** wrong axis coordinates, tooth phase, module, helix hand, mounting distance, or reference transform.
- **Detection:** verify axes and center distance before tooth-level booleans.
- **Correction:** correct datums and mounting geometry, then re-evaluate phase and backlash.
- **Prevention gate:** gear data and axis datums are validated independently.

### F28: Gear collision is actually with a neighboring component

- **Symptom:** the screenshot appears to show tooth interference, but the real overlap is with a flange, shaft, seat, or housing.
- **Root cause:** visual diagnosis is made without isolating pairwise geometry.
- **Detection:** hide unrelated components and compute targeted distances/common volumes.
- **Correction:** repair the actual interface rather than changing tooth geometry blindly.
- **Prevention gate:** interference reports identify both component IDs and contact region.

### F29: Generic all-pairs boolean checking is too slow

- **Symptom:** assembly validation runs for hours.
- **Root cause:** O(n²) exact booleans on complex gears, threads, and repeated fasteners.
- **Detection:** profile pair counts and boolean time.
- **Correction:** broad-phase bounding boxes, interface filters, minimum-distance checks, and specialized gear analysis.
- **Prevention gate:** validation plan defines which pairs require exact booleans.

### F30: Expected contact is reported as forbidden interference

- **Symptom:** bearing fits, seals, threads, or theoretical gear contact fail the same test as gross penetration.
- **Root cause:** no contact-state classification.
- **Detection:** compare interface intent and fit/tolerance data.
- **Correction:** classify clearance, transition, interference fit, theoretical contact, and forbidden penetration separately.
- **Prevention gate:** every audited pair has an expected contact class.

### F31: Only one mechanism position is checked

- **Symptom:** assembly is clear at home position but collides during travel.
- **Root cause:** no motion sampling or extrema search.
- **Detection:** evaluate full required travel and refine near minimum-clearance positions.
- **Correction:** update geometry, limits, or sequence.
- **Prevention gate:** full-travel clearance is a separate pass/fail gate.

## 6. Engineering drawings

### F32: Generated drawing is only a projection sheet

- **Symptom:** lines exist but critical dimensions, fits, sections, BOM, or technical notes are missing.
- **Root cause:** 3D-to-2D is implemented as fixed orthographic projection.
- **Detection:** run feature-coverage and annotation-completeness matrices.
- **Correction:** add functional views, sections, details, dimensions, and traceable engineering annotations.
- **Prevention gate:** a drawing cannot pass on geometry projection alone.

### F33: Fixed view templates hide functional features

- **Symptom:** internal bores, oil passages, keyways, gear engagement, or bearing seats are unreadable.
- **Root cause:** always generating front/top/side/isometric views.
- **Detection:** map every functional feature to a defining view.
- **Correction:** use offset sections, local sections, removed sections, details, or auxiliary views.
- **Prevention gate:** every included view must contribute unique feature coverage.

### F34: Only overall envelope dimensions are added

- **Symptom:** drawing has width/height/depth but cannot guide manufacturing, assembly, or inspection.
- **Root cause:** dimensions are derived from the model bounding box instead of the feature graph.
- **Detection:** classify dimensions as functional, assembly, manufacturing, inspection, or reference.
- **Correction:** dimension interfaces, axes, seats, hole patterns, shoulders, and adjustment ranges.
- **Prevention gate:** envelope dimensions are supplementary only.

### F35: Tolerances are invented to make the drawing look professional

- **Symptom:** precise fits/GD&T appear without functional, process, or inspection basis.
- **Root cause:** visual completeness is prioritized over engineering truth.
- **Detection:** require a source, standard interpretation, stack-up, and inspection method.
- **Correction:** mark proposals as engineering suggestions or remove them from released drawings.
- **Prevention gate:** every released tolerance has provenance and approval.

### F36: Existing source tolerances are described as absent

- **Symptom:** valid H7, h6, plus/minus, or gear tolerances are ignored.
- **Root cause:** incomplete annotation indexing.
- **Detection:** audit all pages and tables for explicit tolerances and fits.
- **Correction:** state that the source has selected tolerances but may lack a complete system.
- **Prevention gate:** annotation inventory precedes critique.

### F37: Source-faithful and enhanced annotations are mixed

- **Symptom:** comparison cannot distinguish original content from added engineering requirements.
- **Root cause:** one sheet is used for both training reproduction and production improvement.
- **Detection:** inspect annotation provenance and release intent.
- **Correction:** issue separate named drawing sets or clearly separated sheets.
- **Prevention gate:** annotation trace records source and release status.

### F38: Text, dimensions, balloons, and tables overlap

- **Symptom:** values are technically present but unreadable.
- **Root cause:** layout is accepted without rendered visual review.
- **Detection:** render at target paper size and inspect at print scale.
- **Correction:** move/rotate dimensions, resize views, separate tables, and repeat the visual check.
- **Prevention gate:** preserve iteration screenshots and collision results.

### F39: TechDraw export success is treated as drawing acceptance

- **Symptom:** PDF exists but is blank, clipped, illegible, or semantically incomplete.
- **Root cause:** export is the only test.
- **Detection:** open/render PDF and PNG, verify pages, sizes, required text, and nonblank pixels.
- **Correction:** repair projection, template, scale, view positions, fonts, and annotations.
- **Prevention gate:** drawing render and semantic audits are mandatory.

### F40: DXF/DWG is assumed equivalent to PDF

- **Symptom:** custom tables, fonts, hatches, symbols, or annotations are lost in CAD exchange.
- **Root cause:** format capability differences are ignored.
- **Detection:** open the actual exported DXF/DWG and compare content classes.
- **Correction:** declare the annotation master format and document exchange limitations.
- **Prevention gate:** each requested output format has its own visual/semantic check.

## 7. STEP and exchange validation

### F41: Rebuilt STEP hash differs and is declared wrong

- **Symptom:** a geometrically equivalent export fails because bytes differ.
- **Root cause:** serialization order, metadata, tolerances, and entity numbering change.
- **Detection:** compare solids, bounds, volume, topology, and critical dimensions.
- **Correction:** use hashes only for unchanged trusted copies; use geometric metrics for rebuilt files.
- **Prevention gate:** exchange validation declares metric tolerances.

### F42: Volume comparison uses an unrealistic absolute tolerance

- **Symptom:** a multi-million mm³ assembly fails for a few mm³ of B-Rep drift.
- **Root cause:** fixed micron-scale tolerance is applied to a large assembly.
- **Detection:** calculate absolute delta and relative ppm.
- **Correction:** use a justified absolute-or-relative threshold and report both.
- **Prevention gate:** threshold is stored in the validation report, not hidden in code.

### F43: STEP round trip checks only total volume

- **Symptom:** missing or misplaced parts can be masked by equal aggregate volume.
- **Root cause:** no occurrence, bounds, or critical-dimension checks.
- **Detection:** compare solid count, global bounds, per-part metrics, axes, and placements.
- **Correction:** expand the validation matrix.
- **Prevention gate:** total volume alone can never pass the geometry gate.

### F44: Trusted input is overwritten by rebuilt output

- **Symptom:** original evidence can no longer be audited.
- **Root cause:** source and export use the same path/name.
- **Detection:** compare file history and hashes.
- **Correction:** preserve an immutable source copy and use distinct export names.
- **Prevention gate:** input and output directories are separate.

## 8. GUI visibility and user opening

### F45: FCStd has geometry but opens blank

- **Symptom:** headless validation passes, but the user sees an empty viewport.
- **Root cause:** the file lacks `GuiDocument.xml` or every shape ViewProvider is hidden.
- **Detection:** inspect the FCStd ZIP and reopen it in FreeCAD GUI.
- **Correction:** initialize FreeCADGui, show accepted occurrences/containers, save, and retest.
- **Prevention gate:** GUI document presence is mandatory for user-facing FCStd delivery.

### F46: Visibility is fixed but camera still shows empty space

- **Symptom:** model tree eye icons are on, but the viewport remains blank or extremely zoomed.
- **Root cause:** `fitAll()` ran before visibility was enabled or no camera was saved.
- **Detection:** inspect camera height/position and run a real viewport capture.
- **Correction:** set visibility first, recompute, select the view, then execute `fitAll()` and save.
- **Prevention gate:** camera and nonblank screenshot are separate checks.

### F47: Origins and planes obscure the model

- **Symptom:** dozens of axes/planes appear instead of a clean assembly.
- **Root cause:** all ViewProviders were made visible indiscriminately.
- **Detection:** classify ViewProviders by object type.
- **Correction:** hide `App::Origin`, lines, planes, points, helper datums, and relation nodes unless requested.
- **Prevention gate:** visibility policy is type-aware.

### F48: The user keeps seeing the old in-memory state

- **Symptom:** the repaired file is correct on disk, but an already-open tab remains blank.
- **Root cause:** FreeCAD does not reload external GUI-state changes into an open document.
- **Detection:** compare file timestamp and document tab state.
- **Correction:** close the old tab and reopen the repaired FCStd or start a new window.
- **Prevention gate:** delivery instructions state that externally repaired files must be reopened.

## 9. Portability, organization, and release

### F49: Portable scripts contain absolute local paths

- **Symptom:** the project works only on the original computer.
- **Root cause:** source, output, FreeCAD, or workbench paths are hard-coded.
- **Detection:** search scripts and run from a different root.
- **Correction:** derive project paths from `__file__`, CLI arguments, or environment variables.
- **Prevention gate:** clean-room rebuild uses a different directory.

### F50: Clean-room test still reads accepted outputs

- **Symptom:** rebuild passes only because old FCStd/STEP files are present.
- **Root cause:** scripts silently reuse caches or generated files.
- **Detection:** run with only documented inputs and source.
- **Correction:** fail on missing required inputs and generate into an empty output tree.
- **Prevention gate:** clean-room manifest lists the only available inputs.

### F51: Quick-access folder contains rejected and accepted versions

- **Symptom:** the user opens an obsolete model and reports a repeated failure.
- **Root cause:** convenience copies are not curated after revisions.
- **Detection:** compare quick-access contents with the accepted manifest.
- **Correction:** move obsolete files into version/error archives and use explicit names.
- **Prevention gate:** quick-access directory is audited before delivery.

### F52: Revision folders and filenames are inconsistent

- **Symptom:** code, model, drawing, and report revisions cannot be matched.
- **Root cause:** overwriting or ad hoc naming during iteration.
- **Detection:** inspect revision fields, filenames, and hashes.
- **Correction:** use numbered revision roots and one manifest.
- **Prevention gate:** any geometry, tolerance, joint, BOM, or drawing change increments revision.

### F53: GitHub privacy is assumed

- **Symptom:** proprietary CAD is uploaded to a public repository.
- **Root cause:** repository creation is mistaken for privacy verification.
- **Detection:** query remote visibility after creation and push.
- **Correction:** change visibility, remove sensitive history where required, rotate exposed credentials, and re-audit.
- **Prevention gate:** no upload without explicit authorization and remote privacy verification.

## 10. Production engineering and productization

### F54: Geometry is treated as complete design

- **Symptom:** no load cases, materials, treatments, fits, inspection, cost, or lead time exist.
- **Root cause:** CAD completion is confused with engineering completion.
- **Detection:** run the inherited V5/V6 production-engineering gates.
- **Correction:** create design inputs, load cases, standards, manufacturing, tolerance, cost, BOM, and sourcing records.
- **Prevention gate:** release intent determines required engineering evidence.

### F55: Safety factor is chosen without a failure model

- **Symptom:** a large number is quoted without load path, fatigue, buckling, wear, or environment analysis.
- **Root cause:** safety factor is used as a substitute for engineering reasoning.
- **Detection:** require failure modes, loads, material allowables, and verification method.
- **Correction:** perform appropriate calculations and tests.
- **Prevention gate:** strength/safety report links every factor to a failure mode.

### F56: Tight tolerances and roughness are applied everywhere

- **Symptom:** manufacturing cost rises and requirements become contradictory or uninspectable.
- **Root cause:** professional appearance is mistaken for functional specification.
- **Detection:** map each tolerance/roughness to function, process capability, and inspection.
- **Correction:** relax nonfunctional requirements and preserve critical interfaces.
- **Prevention gate:** tolerance and roughness provenance is mandatory.

### F57: Cost and lead time are reported without context

- **Symptom:** numbers cannot be compared or become stale.
- **Root cause:** batch, region, currency date, process, quality, supplier, and stock assumptions are omitted.
- **Detection:** audit sourcing metadata.
- **Correction:** state assumptions, ranges, dates, alternatives, and confidence.
- **Prevention gate:** business estimates are time-stamped and nonbinding unless confirmed.

### F58: Deterministic software output is much worse than a one-off Codex task

- **Symptom:** the standalone application produces generic models/drawings while interactive work is much better.
- **Root cause:** the software pipeline lacks semantic reasoning, evidence routing, ambiguity handling, iterative review, and task-specific prompts.
- **Detection:** compare stage artifacts and identify where reasoning was replaced by a fixed template.
- **Correction:** expose staged jobs, evidence records, approval queues, configurable profiles, and optional Codex orchestration.
- **Prevention gate:** no opaque one-click claim; every stage is observable and resumable.

### F59: Runtime grows to hours without useful progress

- **Symptom:** six-hour runs repeat expensive projections, booleans, or exports.
- **Root cause:** no caching, broad-phase filtering, incremental validation, or stage checkpoints.
- **Detection:** profile each stage and count repeated operations.
- **Correction:** cache projections, filter pair checks, reuse inventories, parallelize safe reads, and stop early on blockers.
- **Prevention gate:** each stage has a runtime budget, progress artifact, and restart point.

### F60: The UI exposes options without engineering prerequisites

- **Symptom:** checking “add tolerances” creates unjustified values or contradictory drawings.
- **Root cause:** UI booleans bypass datum, function, standards, process, and inspection logic.
- **Detection:** inspect configuration-to-validation dependencies.
- **Correction:** implement stateful modes such as `source_only`, `engineering_suggested`, and `production_verified`.
- **Prevention gate:** the UI cannot mark a job complete while prerequisite gates fail.
