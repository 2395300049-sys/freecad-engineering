import argparse
import json
from pathlib import Path


COMMON_REQUIRED = (
    "drawing_number",
    "title",
    "revision",
    "drawing_type",
    "model_revision",
    "sheet_size",
    "sheet_count",
    "scale",
    "units",
    "projection",
    "standards_profile",
    "general_tolerance",
    "title_block_complete",
    "visual_pdf_checked",
    "model_drawing_revision_match",
    "approved_by",
)


def main():
    parser = argparse.ArgumentParser(description="Audit engineering drawing release metadata.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    drawing_reports = []
    for index, drawing in enumerate(data.get("drawings", [])):
        issues = []
        for field in COMMON_REQUIRED:
            if drawing.get(field) in (None, ""):
                issues.append({"severity": "blocking", "field": field, "message": "Required release field is missing"})
        drawing_type = drawing.get("drawing_type")
        if drawing_type not in {"part", "assembly"}:
            issues.append({"severity": "blocking", "field": "drawing_type", "message": "Expected part or assembly"})
        if drawing.get("model_revision") != drawing.get("revision") or not drawing.get("model_drawing_revision_match"):
            issues.append({"severity": "blocking", "field": "revision", "message": "Model and drawing revisions do not match"})
        for field in ("title_block_complete", "visual_pdf_checked"):
            if not drawing.get(field):
                issues.append({"severity": "blocking", "field": field, "message": "Release check must be true"})
        if int(drawing.get("functional_dimensions_count", 0)) <= 0:
            issues.append({"severity": "blocking", "field": "functional_dimensions_count", "message": "No functional dimensions recorded"})
        if int(drawing.get("explicit_tolerance_count", 0)) <= 0 and not drawing.get("general_tolerance"):
            issues.append({"severity": "blocking", "field": "explicit_tolerance_count", "message": "No explicit or general tolerance coverage"})
        if drawing_type == "part":
            if not drawing.get("material"):
                issues.append({"severity": "blocking", "field": "material", "message": "Part drawing requires material/condition"})
            if not drawing.get("datum_scheme"):
                issues.append({"severity": "major", "field": "datum_scheme", "message": "No datum scheme recorded"})
        if drawing_type == "assembly":
            if not drawing.get("bom_present"):
                issues.append({"severity": "blocking", "field": "bom_present", "message": "Assembly drawing requires BOM"})
            if not drawing.get("balloons_present"):
                issues.append({"severity": "blocking", "field": "balloons_present", "message": "Assembly drawing requires balloons"})
        if not drawing.get("critical_characteristics"):
            issues.append({"severity": "major", "field": "critical_characteristics", "message": "No critical characteristics recorded"})
        drawing_reports.append(
            {
                "drawing_number": drawing.get("drawing_number", f"drawing-{index + 1}"),
                "drawing_type": drawing_type,
                "issues": issues,
                "pass": not any(item["severity"] == "blocking" for item in issues),
            }
        )

    report = {
        "input": str(input_path),
        "drawing_count": len(drawing_reports),
        "drawings": drawing_reports,
        "pass": bool(drawing_reports) and all(item["pass"] for item in drawing_reports),
        "limitations": ["Metadata validation does not replace visual inspection of the rendered drawing or standards interpretation."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "drawings": len(drawing_reports)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
