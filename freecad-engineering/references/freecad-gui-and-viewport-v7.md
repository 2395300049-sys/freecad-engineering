# FreeCAD GUI and Viewport Delivery V7

## Contents

1. Why headless FCStd can open blank
2. FCStd archive anatomy
3. Required visibility policy
4. Camera and fit sequence
5. Repair workflow
6. Real viewport validation
7. Compatibility and process handling

## 1. Why headless FCStd can open blank

FreeCAD core Python can save geometry without initializing the GUI layer. The resulting FCStd may contain `Document.xml` and B-Rep files but no `GuiDocument.xml`. Headless geometry validators can pass because shapes exist, while the user opens the file and sees an empty viewport.

Other blank-view causes include:

- all shape ViewProviders saved with `Visibility=false`;
- a hidden parent `App::Part` masking visible children;
- camera positioned far from the model;
- camera height near zero or extremely large;
- `fitAll()` executed before shapes become visible;
- the user viewing an old in-memory document after the file was repaired externally.

## 2. FCStd archive anatomy

FCStd is ZIP-based. Relevant members include:

- `Document.xml`: model objects, properties, placements, and shape links;
- `*.Shape.brp`: B-Rep payloads;
- `GuiDocument.xml`: ViewProviders, visibility, display modes, tree state, and camera.

Absence of `GuiDocument.xml` is a blocking issue for an FCStd advertised as directly viewable by the user.

Use `scripts/audit_fcstd_gui_state.py` for a non-FreeCAD ZIP audit.

## 3. Required visibility policy

Default visible:

- accepted physical shape occurrences;
- required `App::Part`/assembly containers so parent visibility does not mask children;
- intentionally visible reference geometry requested by the user.

Default hidden:

- `App::Origin`;
- origin axes, planes, and points;
- non-geometric datum metadata;
- joint/relation metadata nodes;
- rejected or alternate geometry;
- construction helpers not needed for opening inspection.

Do not turn every ViewProvider on. A document with 30 nested `App::Part` containers can create hundreds of origin axes and planes.

## 4. Camera and fit sequence

Use this order:

1. Initialize FreeCADGui.
2. Open the FCStd.
3. Apply type-aware visibility.
4. Recompute the document.
5. Select axonometric or task-appropriate view.
6. Execute `fitAll()`.
7. Process GUI events.
8. Read and record the camera.
9. Save the document.
10. Close and reopen for verification.

Calling `fitAll()` before visibility is set can save an empty camera with a very small height, even if visibility is corrected later.

## 5. Repair workflow

Use FreeCAD's bundled Python and `scripts/fix_fcstd_gui_visibility.py`.

Typical command:

```bat
set QT_QPA_PLATFORM=offscreen
"%FREECAD_PYTHON%" scripts\fix_fcstd_gui_visibility.py model.FCStd --expected-occurrences 42
set QT_QPA_PLATFORM=
```

The offscreen platform can write ViewProvider and camera state without interactive control. It may print OpenGL warnings; these warnings do not replace the real viewport gate.

Always back up the pre-repair file and re-run geometry validation after saving GUI state.

## 6. Real viewport validation

XML checks are necessary but not sufficient. Run FreeCAD with a normal Windows GUI/OpenGL context and:

1. reopen the repaired file;
2. export `activeView().saveImage(...)`;
3. verify image dimensions and nonblank pixel ratio;
4. visually inspect the model framing, clipping, colors, and helper visibility;
5. save the screenshot and report.

Use `scripts/capture_freecad_viewport_v7.py` for the real viewport capture. Do not set `QT_QPA_PLATFORM=offscreen` for this script.

Recommended nonblank check:

- resize the screenshot to a smaller audit image;
- count pixels below a near-white threshold;
- require a meaningful ratio such as greater than 5 percent;
- record the content bounding box;
- still perform human visual inspection.

## 7. Compatibility and process handling

- `FreeCADGui.setupWithoutGUI()` loads types but may not create a usable GUI document.
- `FreeCADGui.showMainWindow()` can initialize full GUI services from FreeCAD's Python.
- ViewProvider APIs vary by FreeCAD version; set display modes inside compatibility guards.
- Offscreen runs may lack a valid framebuffer and cannot prove real rendering.
- Normal GUI verification scripts may emit Qt cleanup warnings after a successful screenshot; capture the screenshot/result before evaluating shutdown noise.
- Do not kill unrelated FreeCAD sessions. Track only processes started by the current task.
- If the user already has the old FCStd open, instruct them to close the tab and reopen the repaired file.

The final manifest should record GUI document presence, visible/hidden ViewProvider counts, camera data, real viewport screenshot, nonblank metric, and FreeCAD version.
