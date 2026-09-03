import argparse
import json
from pathlib import Path


VALID_STATUSES = {"confirmed", "assumed", "unknown", "not_applicable"}
VALID_MODES = {"reconstruction", "new-design", "redesign", "engineering-review"}


def add_issue(issues, severity, code, path, message):
    issues.append(
        {"severity": severity, "code": code, "path": path, "message": message}
    )


def require_value(container, key, path, issues):
    value = container.get(key) if isinstance(container, dict) else None
    if value is None or value == "" or value == []:
        add_issue(issues, "blocking", "missing-required", f"{path}.{key}", "Required value is missing")
    return value


def main():
    parser = argparse.ArgumentParser(description="Validate the V5 design-input contract.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    issues = []

    for section in (
        "project",
        "units",
        "requirements",
        "operating_conditions",
        "production",
        "standards",
        "safety",
        "deliverables",
        "input_register",
    ):
        if section not in data:
            add_issue(issues, "blocking", "missing-section", section, "Required section is missing")

    project = data.get("project", {})
    for key in ("id", "name", "revision", "task_mode", "confidentiality", "owner", "design_authority", "due_date"):
        require_value(project, key, "project", issues)
    if project.get("task_mode") and project["task_mode"] not in VALID_MODES:
        add_issue(issues, "blocking", "invalid-task-mode", "project.task_mode", f"Expected one of {sorted(VALID_MODES)}")
    if project.get("confidentiality") not in {"private", "public-approved", "restricted"}:
        add_issue(issues, "major", "confidentiality", "project.confidentiality", "Use private, restricted, or public-approved")

    units = data.get("units", {})
    for key in ("length", "mass", "force", "torque", "pressure", "temperature", "time", "angle"):
        require_value(units, key, "units", issues)

    requirements = data.get("requirements", {})
    require_value(requirements, "primary_function", "requirements", issues)
    require_value(requirements, "success_criteria", "requirements", issues)
    require_value(requirements, "fixed_interfaces", "requirements", issues)

    operating = data.get("operating_conditions", {})
    require_value(operating, "status", "operating_conditions", issues)
    require_value(operating, "load_cases_file", "operating_conditions", issues)
    if operating.get("status") == "unknown":
        add_issue(issues, "blocking", "unknown-operating-conditions", "operating_conditions.status", "Operating conditions block engineering verification")

    production = data.get("production", {})
    for key in ("prototype_quantity", "annual_quantity", "batch_quantity", "currency", "supplier_region", "required_delivery_date"):
        require_value(production, key, "production", issues)
    for key in ("prototype_quantity", "annual_quantity", "batch_quantity"):
        value = production.get(key)
        if value is not None and (not isinstance(value, (int, float)) or value < 0):
            add_issue(issues, "blocking", "invalid-quantity", f"production.{key}", "Quantity must be non-negative")
    if not production.get("batch_quantity"):
        add_issue(issues, "blocking", "zero-batch", "production.batch_quantity", "Batch quantity must be greater than zero for costing")

    standards = data.get("standards", {})
    require_value(standards, "status", "standards", issues)
    require_value(standards, "profile_file", "standards", issues)
    if standards.get("status") == "unknown":
        add_issue(issues, "blocking", "unknown-standards", "standards.status", "Standards profile blocks drawing and tolerance release")

    safety = data.get("safety", {})
    for key in ("classification", "consequence_of_failure", "required_review"):
        require_value(safety, key, "safety", issues)

    deliverables = data.get("deliverables", [])
    if not isinstance(deliverables, list) or not deliverables:
        add_issue(issues, "blocking", "missing-deliverables", "deliverables", "At least one deliverable is required")

    register = data.get("input_register", [])
    if not isinstance(register, list) or not register:
        add_issue(issues, "blocking", "missing-input-register", "input_register", "Input register is required")
        register = []

    seen_ids = set()
    status_counts = {status: 0 for status in VALID_STATUSES}
    blocking_unknowns = []
    blocking_assumptions = []
    for index, item in enumerate(register):
        path = f"input_register[{index}]"
        if not isinstance(item, dict):
            add_issue(issues, "blocking", "invalid-register-item", path, "Input record must be an object")
            continue
        record_id = require_value(item, "id", path, issues)
        require_value(item, "field", path, issues)
        status = require_value(item, "status", path, issues)
        if record_id in seen_ids:
            add_issue(issues, "blocking", "duplicate-id", f"{path}.id", f"Duplicate input ID {record_id}")
        seen_ids.add(record_id)
        if status not in VALID_STATUSES:
            add_issue(issues, "blocking", "invalid-status", f"{path}.status", f"Expected one of {sorted(VALID_STATUSES)}")
            continue
        status_counts[status] += 1
        blocking = bool(item.get("blocking", False))
        if status == "confirmed":
            require_value(item, "source", path, issues)
            require_value(item, "source_date", path, issues)
        elif status == "assumed":
            require_value(item, "owner", path, issues)
            require_value(item, "rationale", path, issues)
            if blocking:
                blocking_assumptions.append(record_id)
                add_issue(issues, "major", "blocking-assumption", path, "Blocking input is still an assumption and requires approval")
        elif status == "unknown" and blocking:
            blocking_unknowns.append(record_id)
            add_issue(issues, "blocking", "blocking-unknown", path, "Blocking input is unknown")

    blocking_count = sum(issue["severity"] == "blocking" for issue in issues)
    major_count = sum(issue["severity"] == "major" for issue in issues)
    report = {
        "input": str(input_path),
        "project_id": project.get("id"),
        "task_mode": project.get("task_mode"),
        "status_counts": status_counts,
        "blocking_unknowns": blocking_unknowns,
        "blocking_assumptions": blocking_assumptions,
        "issues": issues,
        "summary": {
            "blocking": blocking_count,
            "major": major_count,
            "pass": blocking_count == 0,
            "conditional": blocking_count == 0 and major_count > 0,
        },
    }

    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
