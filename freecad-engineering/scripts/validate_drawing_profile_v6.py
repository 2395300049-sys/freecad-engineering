import argparse
import json
from pathlib import Path


RELEASE_INTENTS = {"source_faithful", "engineering_enhanced"}
TOLERANCE_MODES = {"off", "source_only", "engineering_suggested", "production_verified"}
VIEW_STRATEGIES = {"functional_feature_coverage", "source_layout", "manual"}


def add_issue(issues, severity, field, message):
    issues.append({"severity": severity, "field": field, "message": message})


def validate(data):
    issues = []
    for field in ("schema_version", "profile_id", "display_name", "release_intent"):
        if data.get(field) in (None, ""):
            add_issue(issues, "blocking", field, "Required profile field is missing")

    intent = data.get("release_intent")
    if intent not in RELEASE_INTENTS:
        add_issue(issues, "blocking", "release_intent", f"Expected one of {sorted(RELEASE_INTENTS)}")

    views = data.get("views") or {}
    strategy = views.get("strategy")
    if strategy not in VIEW_STRATEGIES:
        add_issue(issues, "blocking", "views.strategy", f"Expected one of {sorted(VIEW_STRATEGIES)}")
    if strategy == "functional_feature_coverage" and not views.get("principal"):
        add_issue(issues, "blocking", "views.principal", "Functional view planning requires a principal view")

    annotations = data.get("annotations") or {}
    tolerance = data.get("tolerance") or {}
    mode = tolerance.get("mode", "off")
    if mode not in TOLERANCE_MODES:
        add_issue(issues, "blocking", "tolerance.mode", f"Expected one of {sorted(TOLERANCE_MODES)}")
    if tolerance.get("enabled") is False and mode != "off":
        add_issue(issues, "blocking", "tolerance", "Disabled tolerance module must use mode=off")
    if tolerance.get("enabled") and mode == "off":
        add_issue(issues, "blocking", "tolerance", "Enabled tolerance module cannot use mode=off")

    if annotations.get("gdt") and not annotations.get("datums"):
        add_issue(issues, "blocking", "annotations.gdt", "GD&T requires a datum scheme")
    if tolerance.get("fits") and not tolerance.get("enabled"):
        add_issue(issues, "blocking", "tolerance.fits", "Fits require the tolerance module")

    if intent == "source_faithful" and mode not in {"off", "source_only"}:
        add_issue(
            issues,
            "blocking",
            "tolerance.mode",
            "Source-faithful drawings cannot contain suggested or production-added tolerances",
        )

    if mode == "engineering_suggested":
        add_issue(
            issues,
            "warning",
            "tolerance.mode",
            "Suggested engineering values must remain visibly non-released until approved",
        )

    if mode == "production_verified":
        required = {
            "standards_profile_status": "confirmed",
            "design_basis_complete": True,
            "process_capability_confirmed": True,
            "inspection_plan_complete": True,
        }
        for field, expected in required.items():
            if tolerance.get(field) != expected:
                add_issue(
                    issues,
                    "blocking",
                    f"tolerance.{field}",
                    f"Production-verified mode requires {field}={expected!r}",
                )

    assembly = data.get("assembly") or {}
    if assembly.get("balloons") and not assembly.get("bom"):
        add_issue(issues, "blocking", "assembly.balloons", "Balloons require a BOM")
    if assembly.get("backlash_endplay_preload") and not assembly.get("enabled"):
        add_issue(
            issues,
            "warning",
            "assembly.backlash_endplay_preload",
            "Assembly tolerance options are ignored when assembly mode is disabled",
        )

    outputs = data.get("outputs") or []
    if not outputs:
        add_issue(issues, "blocking", "outputs", "At least one output format is required")

    validation = data.get("validation") or {}
    for field in ("visual_render_check", "feature_coverage_check", "semantic_annotation_check"):
        if not validation.get(field):
            add_issue(issues, "major", f"validation.{field}", "Recommended V6 drawing validation is disabled")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate a V6 configurable drawing profile.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    issues = validate(data)
    report = {
        "input": str(input_path),
        "profile_id": data.get("profile_id"),
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
