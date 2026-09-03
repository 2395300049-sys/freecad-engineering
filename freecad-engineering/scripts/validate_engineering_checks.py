import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = (
    "id",
    "component",
    "failure_mode",
    "load_case",
    "method",
    "standard_or_reference",
    "demand",
    "allowable",
    "unit",
    "required_safety_factor",
    "calculated_safety_factor",
    "evidence",
    "reviewer",
    "status",
)


def main():
    parser = argparse.ArgumentParser(description="Audit engineering-check evidence and safety-factor consistency.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--relative-tolerance", type=float, default=0.01)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    reports = []
    for index, check in enumerate(data.get("checks", [])):
        issues = []
        for field in REQUIRED_FIELDS:
            if check.get(field) in (None, ""):
                issues.append({"severity": "blocking", "field": field, "message": "Required field is missing"})
        try:
            demand = float(check.get("demand"))
            allowable = float(check.get("allowable"))
            required_factor = float(check.get("required_safety_factor"))
            supplied_factor = float(check.get("calculated_safety_factor"))
            if demand <= 0 or allowable <= 0:
                raise ValueError("Demand and allowable must be positive")
            calculated = allowable / demand
            relative_error = abs(calculated - supplied_factor) / max(abs(calculated), 1.0)
            if relative_error > args.relative_tolerance:
                issues.append({"severity": "blocking", "field": "calculated_safety_factor", "message": f"Supplied factor {supplied_factor} does not match allowable/demand {calculated}"})
            if supplied_factor < required_factor:
                issues.append({"severity": "blocking", "field": "calculated_safety_factor", "message": "Calculated safety factor is below required"})
            if check.get("status") != "pass":
                issues.append({"severity": "blocking", "field": "status", "message": "Engineering check is not marked pass"})
        except (TypeError, ValueError) as exc:
            calculated = None
            issues.append({"severity": "blocking", "field": "numeric", "message": str(exc)})
        reports.append(
            {
                "id": check.get("id", f"check-{index + 1}"),
                "component": check.get("component"),
                "failure_mode": check.get("failure_mode"),
                "recalculated_safety_factor": calculated,
                "issues": issues,
                "pass": not any(item["severity"] == "blocking" for item in issues),
            }
        )

    report = {
        "input": str(input_path),
        "check_count": len(reports),
        "checks": reports,
        "pass": bool(reports) and all(item["pass"] for item in reports),
        "limitations": ["This audit checks declared evidence consistency and does not perform the governing engineering calculation."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "checks": len(reports)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
