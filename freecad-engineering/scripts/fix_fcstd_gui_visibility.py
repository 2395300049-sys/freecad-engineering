from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def camera_height(camera: str) -> float | None:
    match = re.search(r"\bheight\s+([-+0-9.eE]+)", camera)
    return float(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write type-aware visibility and a fitted default camera into a FreeCAD FCStd."
    )
    parser.add_argument("fcstd", type=Path)
    parser.add_argument("--expected-occurrences", type=int)
    parser.add_argument(
        "--occurrence-property",
        help="When set, show only solid shape objects containing this property.",
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument("--quick-copy", type=Path)
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    path = args.fcstd.resolve()
    if not path.is_file():
        parser.error(f"FCStd not found: {path}")

    if args.backup:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = path.with_name(f"{path.stem}.pre-gui-{timestamp}{path.suffix}")
        shutil.copy2(path, backup)

    import FreeCAD as App
    import FreeCADGui as Gui

    Gui.showMainWindow()
    document = App.openDocument(str(path))
    visible_occurrences = 0
    visible_containers = 0
    hidden_helpers = 0
    try:
        for obj in document.Objects:
            has_solid_shape = (
                hasattr(obj, "Shape")
                and not obj.Shape.isNull()
                and len(obj.Shape.Solids) > 0
            )
            property_ok = (
                args.occurrence_property is None
                or args.occurrence_property in obj.PropertiesList
            )
            is_occurrence = has_solid_shape and property_ok
            is_container = obj.TypeId in {
                "App::Part",
                "App::DocumentObjectGroup",
                "Assembly::AssemblyObject",
            }
            should_show = is_occurrence or is_container
            try:
                obj.ViewObject.Visibility = should_show
                if is_occurrence:
                    visible_occurrences += 1
                    obj.ViewObject.Transparency = 0
                    obj.ViewObject.LineColor = (0.16, 0.18, 0.20)
                    obj.ViewObject.LineWidth = 1.0
                    if not args.no_color:
                        obj.ViewObject.ShapeColor = (0.66, 0.69, 0.72)
                    try:
                        obj.ViewObject.DisplayMode = "Flat Lines"
                    except Exception:
                        pass
                elif is_container:
                    visible_containers += 1
                else:
                    hidden_helpers += 1
            except Exception:
                hidden_helpers += 1

        if (
            args.expected_occurrences is not None
            and visible_occurrences != args.expected_occurrences
        ):
            raise RuntimeError(
                f"Expected {args.expected_occurrences} visible occurrences, found {visible_occurrences}"
            )

        document.recompute()
        view = Gui.activeDocument().activeView()
        view.viewAxonometric()
        view.fitAll()
        Gui.updateGui()
        camera = view.getCamera()
        document.save()
    finally:
        App.closeDocument(document.Name)

    if args.quick_copy:
        quick_copy = args.quick_copy.resolve()
        quick_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, quick_copy)
    else:
        quick_copy = None

    with zipfile.ZipFile(path) as archive:
        has_gui = "GuiDocument.xml" in archive.namelist()
        gui_size = len(archive.read("GuiDocument.xml")) if has_gui else 0

    height = camera_height(camera)
    checks = {
        "gui_document_present": has_gui,
        "visible_occurrences_nonzero": visible_occurrences > 0,
        "expected_occurrences": (
            True
            if args.expected_occurrences is None
            else visible_occurrences == args.expected_occurrences
        ),
        "camera_height_valid": height is not None and height > 1.0,
    }
    report = {
        "schema_version": "v7.0",
        "freecad_version": ".".join(App.Version()[:3]),
        "fcstd": str(path),
        "quick_copy": str(quick_copy) if quick_copy else None,
        "visible_occurrences": visible_occurrences,
        "visible_containers": visible_containers,
        "hidden_helpers": hidden_helpers,
        "gui_document_present": has_gui,
        "gui_document_size_bytes": gui_size,
        "camera_height": height,
        "camera": camera,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
        "qt_platform": os.environ.get("QT_QPA_PLATFORM", "default"),
    }
    report_path = args.report.resolve() if args.report else path.with_suffix(".gui-fix.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(report_path)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
