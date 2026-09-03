from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


COLLECTION_KEYS = (
    "annotations",
    "dimensions",
    "fits",
    "datums",
    "gdt",
    "roughness",
    "notes",
)
RELEASED_STATUSES = {"released", "production_verified", "production_released"}
SUGGESTED_STATUSES = {
    "suggested",
    "engineering_suggested",
    "unreleased",
    "pending_approval",
    "pending_confirmation",
}


def records_from_payload(payload) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    records = []
    for key in COLLECTION_KEYS:
        value = payload.get(key, [])
        if isinstance(value, list):
            for row in value:
                if isinstance(row, dict):
                    records.append({"collection": key, **row})
    return records


def first_value(record: dict, keys: tuple[str, ...]):
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit annotation provenance, locators and release states for V7 drawings."
    )
    parser.add_argument("trace", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()

    path = args.trace.resolve()
    if not path.is_file():
        parser.error(f"Trace file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = records_from_payload(payload)
    errors = []
    warnings = []
    seen_ids = set()

    for index, record in enumerate(records, 1):
        record_id = first_value(record, ("id", "annotation_id"))
        authority = first_value(
            record, ("authority", "source", "source_type", "evidence_authority")
        )
        locator = first_value(record, ("locator", "source_locator", "page", "region"))
        status = str(first_value(record, ("status", "release_status", "approval_status")) or "").lower()
        label = record_id or f"record-{index}"

        if not record_id:
            errors.append(f"{label}: missing stable id")
        elif record_id in seen_ids:
            errors.append(f"{label}: duplicate id")
        else:
            seen_ids.add(record_id)

        if not authority:
            errors.append(f"{label}: missing authority/source")
        if not locator and str(authority).lower() not in {"trusted step", "trusted_step", "engineering review"}:
            errors.append(f"{label}: missing source locator")
        if not status:
            errors.append(f"{label}: missing release status")

        authority_text = str(authority or "").lower()
        if status in RELEASED_STATUSES and (
            "suggest" in authority_text or "proposal" in authority_text or "unreleased" in authority_text
        ):
            errors.append(f"{label}: engineering suggestion is marked released")
        if status in SUGGESTED_STATUSES and record.get("production_release") is True:
            errors.append(f"{label}: suggested annotation has production_release=true")
        if status not in RELEASED_STATUSES | SUGGESTED_STATUSES | {"source_explicit", "reference_measured", "conflicting"}:
            warnings.append(f"{label}: nonstandard status '{status}'")

    checks = {
        "records_present": bool(records),
        "no_errors": not errors,
        "unique_ids": len(seen_ids) == len(records),
    }
    report = {
        "schema_version": "v7.0",
        "trace": str(path),
        "record_count": len(records),
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }
    output = args.output.resolve() if args.output else path.with_suffix(".annotation-audit.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" or args.no_fail else 1


if __name__ == "__main__":
    sys.exit(main())
