import argparse
import json
from datetime import date, datetime
from pathlib import Path


def parse_date(value, issues, path):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        issues.append({"severity": "blocking", "path": path, "message": "Date must use YYYY-MM-DD"})
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate a controlled engineering standards profile.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--max-review-age-days", type=int, default=365)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    issues = []
    for field in ("profile_id", "governing_family", "units_system", "conflict_hierarchy", "standards"):
        if data.get(field) in (None, "", []):
            issues.append({"severity": "blocking", "path": field, "message": "Required profile field is missing"})
    if len(data.get("conflict_hierarchy", [])) < 2:
        issues.append({"severity": "major", "path": "conflict_hierarchy", "message": "Conflict hierarchy should contain at least two authority levels"})

    records = []
    seen = set()
    for index, standard in enumerate(data.get("standards", [])):
        path = f"standards[{index}]"
        local_issues = []
        for field in ("category", "identifier", "title", "edition", "source", "access_date", "status"):
            value = standard.get(field)
            if value in (None, "") or "TO-BE-CONFIRMED" in str(value):
                local_issues.append({"severity": "blocking", "path": f"{path}.{field}", "message": "Controlled standard field is missing or placeholder"})
        identifier = standard.get("identifier")
        if identifier in seen:
            local_issues.append({"severity": "blocking", "path": f"{path}.identifier", "message": "Duplicate standard identifier"})
        seen.add(identifier)
        status = standard.get("status")
        if status == "unknown":
            local_issues.append({"severity": "blocking", "path": f"{path}.status", "message": "Unknown standard blocks release"})
        elif status == "assumed":
            local_issues.append({"severity": "major", "path": f"{path}.status", "message": "Assumed standard requires approval"})
        elif status not in {"confirmed", "assumed", "unknown", "not_applicable"}:
            local_issues.append({"severity": "blocking", "path": f"{path}.status", "message": "Invalid status"})
        access_date = parse_date(standard.get("access_date"), local_issues, f"{path}.access_date")
        age = (as_of - access_date).days if access_date else None
        if age is not None and age < 0:
            local_issues.append({"severity": "blocking", "path": f"{path}.access_date", "message": "Standards access date is later than the audit date"})
        elif age is not None and age > args.max_review_age_days:
            local_issues.append({"severity": "major", "path": f"{path}.access_date", "message": f"Standards review is {age} days old"})
        issues.extend(local_issues)
        records.append({"identifier": identifier, "category": standard.get("category"), "status": status, "review_age_days": age, "issues": local_issues})

    blocking = sum(item["severity"] == "blocking" for item in issues)
    major = sum(item["severity"] == "major" for item in issues)
    report = {
        "input": str(input_path),
        "as_of": as_of.isoformat(),
        "profile_id": data.get("profile_id"),
        "standards": records,
        "issues": issues,
        "summary": {"blocking": blocking, "major": major, "pass": blocking == 0, "conditional": blocking == 0 and major > 0},
        "limitations": ["This audit validates the controlled record and does not confirm legal applicability or reproduce standard content."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_validation.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
