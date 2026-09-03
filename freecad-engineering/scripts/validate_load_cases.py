import argparse
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Validate operating-condition and load-case completeness.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-abnormal", action="store_true")
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    issues = []
    life = data.get("life_target", {})
    if not life:
        issues.append({"severity": "blocking", "path": "life_target", "message": "Life target is missing"})
    elif not any(float(life.get(key, 0) or 0) > 0 for key in ("operating_hours", "starts", "cycles", "revolutions")):
        issues.append({"severity": "blocking", "path": "life_target", "message": "No positive life measure is defined"})

    records = []
    seen = set()
    categories = set()
    for index, load_case in enumerate(data.get("load_cases", [])):
        path = f"load_cases[{index}]"
        local = []
        case_id = load_case.get("id")
        if not case_id:
            local.append({"severity": "blocking", "path": f"{path}.id", "message": "Load-case ID is missing"})
        elif case_id in seen:
            local.append({"severity": "blocking", "path": f"{path}.id", "message": "Duplicate load-case ID"})
        seen.add(case_id)
        for field in ("description", "category", "frequency", "required_checks"):
            if load_case.get(field) in (None, "", []):
                local.append({"severity": "blocking", "path": f"{path}.{field}", "message": "Required load-case field is missing"})
        categories.add(load_case.get("category"))
        duration = load_case.get("duration_s")
        if duration is None or float(duration) <= 0:
            local.append({"severity": "blocking", "path": f"{path}.duration_s", "message": "Duration must be positive"})
        loads = load_case.get("loads", [])
        if not loads:
            local.append({"severity": "blocking", "path": f"{path}.loads", "message": "No loads are defined"})
        for load_index, load in enumerate(loads):
            load_path = f"{path}.loads[{load_index}]"
            for field in ("type", "value", "unit", "application", "source"):
                if load.get(field) in (None, ""):
                    local.append({"severity": "blocking", "path": f"{load_path}.{field}", "message": "Required load field is missing"})
            if load.get("type") in {"force", "moment", "torque", "acceleration"} and load.get("direction") is None:
                local.append({"severity": "major", "path": f"{load_path}.direction", "message": "Vector load direction is not documented"})
            try:
                value = float(load.get("value"))
                if not math.isfinite(value):
                    raise ValueError
            except (TypeError, ValueError):
                local.append({"severity": "blocking", "path": f"{load_path}.value", "message": "Load value must be finite"})
            uncertainty = load.get("uncertainty_fraction")
            if uncertainty is None:
                local.append({"severity": "major", "path": f"{load_path}.uncertainty_fraction", "message": "Load uncertainty is not documented"})
            elif float(uncertainty) < 0:
                local.append({"severity": "blocking", "path": f"{load_path}.uncertainty_fraction", "message": "Uncertainty cannot be negative"})
        issues.extend(local)
        records.append({"id": case_id, "category": load_case.get("category"), "load_count": len(loads), "issues": local})

    if not records:
        issues.append({"severity": "blocking", "path": "load_cases", "message": "At least one load case is required"})
    if args.require_abnormal and "abnormal" not in categories:
        issues.append({"severity": "blocking", "path": "load_cases", "message": "An abnormal/jam/overload case is required"})

    blocking = sum(item["severity"] == "blocking" for item in issues)
    major = sum(item["severity"] == "major" for item in issues)
    report = {
        "input": str(input_path),
        "coordinate_system": data.get("coordinate_system"),
        "load_case_count": len(records),
        "load_cases": records,
        "issues": issues,
        "summary": {"blocking": blocking, "major": major, "pass": blocking == 0, "conditional": blocking == 0 and major > 0},
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
