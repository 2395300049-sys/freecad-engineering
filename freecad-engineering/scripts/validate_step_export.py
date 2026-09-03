import argparse
import json
from pathlib import Path

import FreeCAD as App
import Import
import Part


def parse_args():
    parser = argparse.ArgumentParser(description="Validate a delivered STEP by re-importing it in FreeCAD.")
    parser.add_argument("step", type=Path)
    parser.add_argument("--expected-objects", type=int)
    parser.add_argument("--expected-solids", type=int)
    parser.add_argument("--expected-bounds", nargs=3, type=float)
    parser.add_argument("--expected-volume", type=float)
    parser.add_argument("--tolerance", type=float, default=1e-5)
    parser.add_argument("--relative-volume-tolerance", type=float, default=1e-6)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    step_path = args.step.resolve()
    if not step_path.exists():
        raise FileNotFoundError(step_path)

    doc = App.newDocument("step_export_validation")
    Import.insert(str(step_path), doc.Name)
    doc.recompute()
    objects = [
        obj for obj in doc.Objects
        if hasattr(obj, "Shape") and not obj.Shape.isNull()
        and len(getattr(obj, "OutList", [])) == 0 and len(obj.Shape.Solids) > 0
    ]
    compound = Part.makeCompound([obj.Shape for obj in objects])
    bounds = [compound.BoundBox.XLength, compound.BoundBox.YLength, compound.BoundBox.ZLength]
    report = {
        "step": str(step_path),
        "freecad_version": App.Version(),
        "leaf_object_count": len(objects),
        "solid_count": sum(len(obj.Shape.Solids) for obj in objects),
        "invalid_object_count": sum(not obj.Shape.isValid() for obj in objects),
        "bounds_mm": bounds,
        "volume_sum_mm3": sum(obj.Shape.Volume for obj in objects),
        "checks": {},
    }
    if args.expected_objects is not None:
        report["checks"]["objects"] = len(objects) == args.expected_objects
    if args.expected_solids is not None:
        report["checks"]["solids"] = report["solid_count"] == args.expected_solids
    if args.expected_bounds is not None:
        report["checks"]["bounds"] = all(
            abs(bounds[index] - args.expected_bounds[index]) <= args.tolerance
            for index in range(3)
        )
    if args.expected_volume is not None:
        denominator = max(abs(args.expected_volume), 1.0)
        relative_error = abs(report["volume_sum_mm3"] - args.expected_volume) / denominator
        report["relative_volume_error"] = relative_error
        report["checks"]["volume"] = relative_error <= args.relative_volume_tolerance
    report["checks"]["valid"] = report["invalid_object_count"] == 0
    report["pass"] = all(report["checks"].values())
    if args.report:
        report_path = args.report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    App.closeDocument(doc.Name)
    raise SystemExit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
