import argparse
import json
from pathlib import Path


OPERATIONS = {
    "2d_to_3d",
    "3d_to_2d",
    "assembly",
    "drawing_audit",
    "comparison",
    "new_design",
    "redesign",
    "engineering_review",
}
RELEASE_INTENTS = {"source_faithful", "engineering_enhanced", "both", "not_applicable"}
PRIVACY_MODES = {"offline", "local_model", "optional_cloud"}
TWO_D_FORMATS = {"pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "dxf", "dwg", "svg"}
THREE_D_FORMATS = {"fcstd", "step", "stp", "iges", "igs", "brep", "sldprt", "sldasm", "stl"}


def add_issue(issues, severity, field, message):
    issues.append({"severity": severity, "field": field, "message": message})


def validate(data, source_path):
    issues = []
    for field in ("schema_version", "job_id", "project_name", "operation", "release_intent", "privacy_mode"):
        if data.get(field) in (None, ""):
            add_issue(issues, "blocking", field, "Required job field is missing")

    operation = data.get("operation")
    if operation not in OPERATIONS:
        add_issue(issues, "blocking", "operation", f"Expected one of {sorted(OPERATIONS)}")
    intent = data.get("release_intent")
    if intent not in RELEASE_INTENTS:
        add_issue(issues, "blocking", "release_intent", f"Expected one of {sorted(RELEASE_INTENTS)}")
    if data.get("privacy_mode") not in PRIVACY_MODES:
        add_issue(issues, "blocking", "privacy_mode", f"Expected one of {sorted(PRIVACY_MODES)}")

    inputs = data.get("inputs") or []
    formats = {str(item.get("format", "")).lower() for item in inputs}
    if not inputs:
        add_issue(issues, "blocking", "inputs", "At least one input is required")
    if operation == "2d_to_3d" and not formats.intersection(TWO_D_FORMATS):
        add_issue(issues, "blocking", "inputs", "2d_to_3d requires at least one supported 2D input")
    if operation == "3d_to_2d" and not formats.intersection(THREE_D_FORMATS):
        add_issue(issues, "blocking", "inputs", "3d_to_2d requires at least one supported 3D input")
    if operation == "assembly" and not formats.intersection(THREE_D_FORMATS):
        add_issue(issues, "blocking", "inputs", "assembly requires part or assembly geometry")
    if operation == "comparison" and len(inputs) < 2:
        add_issue(issues, "blocking", "inputs", "comparison requires at least two inputs")

    if operation == "2d_to_3d" and data.get("ambiguity_policy") != "human_review":
        add_issue(
            issues,
            "blocking",
            "ambiguity_policy",
            "2D-to-3D reconstruction must route non-unique geometry to human review",
        )

    profile_value = data.get("drawing_profile")
    if operation in {"3d_to_2d", "drawing_audit"} and not profile_value:
        add_issue(issues, "blocking", "drawing_profile", "Drawing work requires a drawing profile")
    if profile_value:
        profile_path = Path(profile_value)
        if not profile_path.is_absolute():
            profile_path = source_path.parent / profile_path
        if not profile_path.is_file():
            add_issue(issues, "blocking", "drawing_profile", f"Profile file does not exist: {profile_path}")
        else:
            profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
            profile_intent = profile.get("release_intent")
            if intent not in {"both", "not_applicable"} and profile_intent != intent:
                add_issue(
                    issues,
                    "blocking",
                    "release_intent",
                    f"Job intent {intent!r} does not match profile intent {profile_intent!r}",
                )

    outputs = data.get("outputs") or []
    if not outputs:
        add_issue(issues, "blocking", "outputs", "At least one output is required")
    if not data.get("output_root"):
        add_issue(issues, "blocking", "output_root", "Output root is required")

    approval = data.get("approval") or {}
    if approval.get("release_approved") and not approval.get("responsible_engineer"):
        add_issue(issues, "blocking", "approval.responsible_engineer", "Released work requires an approver")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate a V6 CAD job configuration.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    issues = validate(data, input_path)
    report = {
        "input": str(input_path),
        "job_id": data.get("job_id"),
        "operation": data.get("operation"),
        "issues": issues,
        "pass": not any(item["severity"] == "blocking" for item in issues),
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "issues": len(issues)}, ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
