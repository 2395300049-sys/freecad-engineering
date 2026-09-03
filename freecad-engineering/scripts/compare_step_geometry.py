from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def rounded(value: float) -> float:
    return round(float(value), 6)


def shape_metrics(shape) -> dict:
    box = shape.BoundBox
    return {
        "solid_count": len(shape.Solids),
        "is_valid": bool(shape.isValid()),
        "volume_mm3": rounded(shape.Volume),
        "area_mm2": rounded(shape.Area),
        "bounds_mm": {
            "x_min": rounded(box.XMin),
            "x_max": rounded(box.XMax),
            "y_min": rounded(box.YMin),
            "y_max": rounded(box.YMax),
            "z_min": rounded(box.ZMin),
            "z_max": rounded(box.ZMax),
            "x_length": rounded(box.XLength),
            "y_length": rounded(box.YLength),
            "z_length": rounded(box.ZLength),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare trusted and rebuilt STEP geometry using solids, bounds and ppm volume drift."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--bound-tolerance-mm", type=float, default=1e-4)
    parser.add_argument("--volume-absolute-tolerance-mm3", type=float, default=1e-3)
    parser.add_argument("--volume-relative-tolerance-ppm", type=float, default=2.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()

    reference = args.reference.resolve()
    candidate = args.candidate.resolve()
    for path in (reference, candidate):
        if not path.is_file():
            parser.error(f"STEP file not found: {path}")

    import FreeCAD as App
    import Part

    reference_metrics = shape_metrics(Part.read(str(reference)))
    candidate_metrics = shape_metrics(Part.read(str(candidate)))
    bound_keys = tuple(reference_metrics["bounds_mm"].keys())
    bound_deltas = {
        key: rounded(candidate_metrics["bounds_mm"][key] - reference_metrics["bounds_mm"][key])
        for key in bound_keys
    }
    bounds_match = all(
        abs(delta) <= args.bound_tolerance_mm for delta in bound_deltas.values()
    )
    volume_delta = rounded(candidate_metrics["volume_mm3"] - reference_metrics["volume_mm3"])
    reference_volume = max(abs(reference_metrics["volume_mm3"]), 1.0)
    volume_delta_ppm = rounded(abs(volume_delta) / reference_volume * 1_000_000.0)
    volume_tolerance = max(
        args.volume_absolute_tolerance_mm3,
        reference_volume * args.volume_relative_tolerance_ppm / 1_000_000.0,
    )
    volume_match = abs(volume_delta) <= volume_tolerance
    checks = {
        "reference_valid": reference_metrics["is_valid"],
        "candidate_valid": candidate_metrics["is_valid"],
        "solid_count_match": reference_metrics["solid_count"] == candidate_metrics["solid_count"],
        "bounds_match": bounds_match,
        "volume_match": volume_match,
    }
    report = {
        "schema_version": "v7.0",
        "freecad_version": ".".join(App.Version()[:3]),
        "reference": {"path": str(reference), "sha256": sha256(reference), **reference_metrics},
        "candidate": {"path": str(candidate), "sha256": sha256(candidate), **candidate_metrics},
        "thresholds": {
            "bound_tolerance_mm": args.bound_tolerance_mm,
            "volume_absolute_tolerance_mm3": args.volume_absolute_tolerance_mm3,
            "volume_relative_tolerance_ppm": args.volume_relative_tolerance_ppm,
            "effective_volume_tolerance_mm3": rounded(volume_tolerance),
        },
        "comparison": {
            "bound_deltas_mm": bound_deltas,
            "volume_delta_mm3": volume_delta,
            "volume_delta_ppm": volume_delta_ppm,
            "hashes_match": sha256(reference) == sha256(candidate),
        },
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }
    output = args.output.resolve() if args.output else candidate.with_suffix(".step-compare.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" or args.no_fail else 1


if __name__ == "__main__":
    sys.exit(main())
