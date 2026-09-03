from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Open an FCStd in the real FreeCAD GUI, capture the viewport, and audit nonwhite pixels."
    )
    parser.add_argument("fcstd", type=Path)
    parser.add_argument("output_png", type=Path)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--nonwhite-threshold", type=float, default=0.05)
    parser.add_argument("--wait-seconds", type=float, default=3.0)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--keep-saved-camera", action="store_true")
    args = parser.parse_args()

    if os.environ.get("QT_QPA_PLATFORM", "").lower() == "offscreen":
        parser.error("Real viewport capture must not run with QT_QPA_PLATFORM=offscreen")
    fcstd = args.fcstd.resolve()
    output = args.output_png.resolve()
    if not fcstd.is_file():
        parser.error(f"FCStd not found: {fcstd}")
    output.parent.mkdir(parents=True, exist_ok=True)

    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtGui, QtWidgets

    Gui.showMainWindow()
    document = App.openDocument(str(fcstd))
    view = Gui.activeDocument().activeView()
    if not args.keep_saved_camera:
        view.viewAxonometric()
        view.fitAll()
    Gui.updateGui()

    application = QtWidgets.QApplication.instance()
    deadline = time.time() + max(args.wait_seconds, 0.5)
    while time.time() < deadline:
        application.processEvents()
        time.sleep(0.05)

    view.saveImage(str(output), args.width, args.height, "White")
    for _ in range(10):
        application.processEvents()
        time.sleep(0.05)

    image = QtGui.QImage(str(output))
    sample_step_x = max(1, image.width() // 400)
    sample_step_y = max(1, image.height() // 250)
    sampled = 0
    nonwhite = 0
    min_x = image.width()
    min_y = image.height()
    max_x = -1
    max_y = -1
    for y in range(0, image.height(), sample_step_y):
        for x in range(0, image.width(), sample_step_x):
            color = image.pixelColor(x, y)
            sampled += 1
            if min(color.red(), color.green(), color.blue()) < 245:
                nonwhite += 1
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    ratio = nonwhite / sampled if sampled else 0.0
    bbox = [min_x, min_y, max_x, max_y] if max_x >= 0 else None
    status = "pass" if output.is_file() and output.stat().st_size > 0 and ratio >= args.nonwhite_threshold else "fail"
    report = {
        "schema_version": "v7.0",
        "freecad_version": ".".join(App.Version()[:3]),
        "fcstd": str(fcstd),
        "image": str(output),
        "width_px": image.width(),
        "height_px": image.height(),
        "file_size_bytes": output.stat().st_size if output.exists() else 0,
        "sampled_pixels": sampled,
        "nonwhite_pixel_ratio": round(ratio, 6),
        "content_bbox_sampled_px": bbox,
        "nonwhite_threshold": args.nonwhite_threshold,
        "status": status,
    }
    report_path = args.report.resolve() if args.report else output.with_suffix(".viewport.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "report": str(report_path)}, ensure_ascii=False))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if status == "pass" else 1)


if __name__ == "__main__":
    main()
