#!/usr/bin/env python3
"""Validate measured invariants for an imported-shape repair."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def vector(value: Any, length: int, name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{name} must be a list of {length} numbers")
    result = [float(item) for item in value]
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{name} contains a non-finite value")
    return result


def maximum_delta(a: list[float], b: list[float]) -> float:
    return max(abs(left - right) for left, right in zip(a, b))


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if data.get("schema") != "freecad.repair-evidence/v8":
        errors.append("schema must equal freecad.repair-evidence/v8")

    thresholds = data.get("thresholds") or {}
    before = data.get("before") or {}
    after = data.get("after") or {}
    metrics: dict[str, float] = {}

    try:
        bounds_limit = float(thresholds["bounds_abs_mm"])
        volume_limit = float(thresholds["volume_drift_ppm"])
        center_limit = float(thresholds["center_abs_mm"])
        if min(bounds_limit, volume_limit, center_limit) < 0:
            raise ValueError("thresholds must be non-negative")

        before_bounds = vector(before.get("bounds_mm"), 6, "before.bounds_mm")
        after_bounds = vector(after.get("bounds_mm"), 6, "after.bounds_mm")
        before_center = vector(before.get("center_mm"), 3, "before.center_mm")
        after_center = vector(after.get("center_mm"), 3, "after.center_mm")
        before_placement = vector(before.get("placement"), len(before.get("placement") or []), "before.placement")
        after_placement = vector(after.get("placement"), len(after.get("placement") or []), "after.placement")
        if len(before_placement) not in {12, 16} or len(before_placement) != len(after_placement):
            raise ValueError("placements must have equal length of 12 or 16")

        before_volume = float(before["volume_mm3"])
        after_volume = float(after["volume_mm3"])
        if not math.isfinite(before_volume) or not math.isfinite(after_volume) or before_volume <= 0:
            raise ValueError("volumes must be finite and before volume must be positive")

        metrics["bounds_max_abs_mm"] = maximum_delta(before_bounds, after_bounds)
        metrics["center_max_abs_mm"] = maximum_delta(before_center, after_center)
        metrics["placement_max_abs"] = maximum_delta(before_placement, after_placement)
        metrics["volume_drift_ppm"] = abs(after_volume - before_volume) / before_volume * 1_000_000.0

        if after.get("valid") is not True:
            errors.append("after.valid must be true")
        if thresholds.get("require_same_solid_count", True):
            if int(before["solid_count"]) != int(after["solid_count"]):
                errors.append("solid count changed")
        if metrics["bounds_max_abs_mm"] > bounds_limit:
            errors.append("bounds drift exceeds threshold")
        if metrics["center_max_abs_mm"] > center_limit:
            errors.append("center drift exceeds threshold")
        if metrics["volume_drift_ppm"] > volume_limit:
            errors.append("volume drift exceeds threshold")
        if thresholds.get("require_same_placement", True) and metrics["placement_max_abs"] > 1e-12:
            errors.append("placement changed")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    approval = data.get("approval") or {}
    if approval.get("required") is True and approval.get("approved") is not True:
        errors.append("required engineering approval is missing")

    return {
        "schema": "freecad.repair-validation/v8",
        "repair_id": data.get("repair_id"),
        "metrics": metrics,
        "errors": errors,
        "pass": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.evidence.read_text(encoding="utf-8-sig"))
        report = validate(data)
    except Exception as exc:
        report = {"schema": "freecad.repair-validation/v8", "pass": False, "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("pass") else 2


if __name__ == "__main__":
    sys.exit(main())
