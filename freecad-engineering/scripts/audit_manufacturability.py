import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Audit manufacturing route, setup, access, capability, and reviewed exceptions.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    part_reports = []
    for index, part in enumerate(data.get("parts", [])):
        issues = []
        part_number = part.get("part_number", f"part-{index + 1}")
        for field in ("part_number", "revision", "material", "blank", "annual_quantity", "batch_quantity", "primary_datums", "process_route", "heat_treatment", "surface_treatment", "deburr_and_edge_requirements", "inspection_plan"):
            if part.get(field) in (None, "", []):
                issues.append({"severity": "blocking", "field": field, "message": "Required manufacturing field is missing"})
        if float(part.get("batch_quantity", 0) or 0) <= 0:
            issues.append({"severity": "blocking", "field": "batch_quantity", "message": "Batch quantity must be positive"})
        sequences = []
        for operation in part.get("process_route", []):
            sequence = operation.get("sequence")
            sequences.append(sequence)
            for field in ("sequence", "operation", "machine_or_process", "setup_datum", "inspection"):
                if operation.get(field) in (None, ""):
                    issues.append({"severity": "blocking", "field": f"process_route.{field}", "message": "Operation field is missing"})
            if not operation.get("tool_access_reviewed"):
                issues.append({"severity": "blocking", "field": "process_route.tool_access_reviewed", "message": f"Tool access not reviewed for operation {sequence}"})
            if not operation.get("process_capability_reviewed"):
                issues.append({"severity": "blocking", "field": "process_route.process_capability_reviewed", "message": f"Process capability not reviewed for operation {sequence}"})
        valid_sequences = [value for value in sequences if isinstance(value, (int, float))]
        if len(valid_sequences) != len(sequences):
            issues.append({"severity": "blocking", "field": "process_route.sequence", "message": "Operation sequences must be numeric"})
        if len(valid_sequences) != len(set(valid_sequences)):
            issues.append({"severity": "blocking", "field": "process_route.sequence", "message": "Operation sequence values must be unique"})
        if valid_sequences != sorted(valid_sequences):
            issues.append({"severity": "major", "field": "process_route.sequence", "message": "Process route is not stored in sequence order"})

        for feature in part.get("feature_reviews", []):
            actual = float(feature.get("actual", 0))
            limit = float(feature.get("recommended_limit", 0))
            if limit > 0 and actual > limit:
                if not feature.get("approved_exception"):
                    issues.append({"severity": "blocking", "field": "feature_reviews", "message": f"{feature.get('feature')} exceeds reviewed limit without approval"})
                elif not feature.get("exception_reason"):
                    issues.append({"severity": "blocking", "field": "feature_reviews.exception_reason", "message": "Approved exception requires a reason"})
        if not part.get("distortion_allowance_reviewed"):
            issues.append({"severity": "major", "field": "distortion_allowance_reviewed", "message": "Heat/process distortion allowance has not been reviewed"})

        part_reports.append(
            {
                "part_number": part_number,
                "operation_count": len(part.get("process_route", [])),
                "issues": issues,
                "pass": not any(item["severity"] == "blocking" for item in issues),
            }
        )

    report = {
        "input": str(input_path),
        "part_count": len(part_reports),
        "parts": part_reports,
        "pass": bool(part_reports) and all(item["pass"] for item in part_reports),
        "limitations": ["Metadata review does not replace supplier/process-engineer confirmation, machine simulation, or first-article inspection."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_audit.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "parts": len(part_reports)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
