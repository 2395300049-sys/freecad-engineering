from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate V7 physical occurrence ledger counts, identifiers and quantity conflicts."
    )
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()

    path = args.ledger.resolve()
    if not path.is_file():
        parser.error(f"Ledger not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    occurrences = payload.get("occurrences", [])
    counts = payload.get("counts", {})
    errors = []
    warnings = []
    ids = []
    solid_sum = 0
    item_counts = Counter()
    conflicts = []

    for index, row in enumerate(occurrences, 1):
        occurrence_id = row.get("occurrence_id")
        if not occurrence_id:
            errors.append(f"row {index}: missing occurrence_id")
        else:
            ids.append(occurrence_id)
        for field in ("bom_item", "definition_id", "source_object", "global_placement"):
            if row.get(field) in (None, ""):
                errors.append(f"{occurrence_id or index}: missing {field}")
        solid_count = int(row.get("solid_count", 0))
        solid_sum += solid_count
        if solid_count <= 0:
            errors.append(f"{occurrence_id or index}: solid_count must be positive")
        item_counts[str(row.get("bom_item"))] += 1
        source_quantity = row.get("source_quantity")
        reference_quantity = row.get("reference_quantity")
        status = row.get("quantity_status")
        if source_quantity is not None and reference_quantity is not None:
            expected_status = "match" if source_quantity == reference_quantity else "conflict"
            if status != expected_status:
                errors.append(
                    f"{occurrence_id or index}: quantity_status '{status}' should be '{expected_status}'"
                )
            if expected_status == "conflict":
                conflicts.append(occurrence_id or str(index))

    duplicate_ids = sorted([item for item, count in Counter(ids).items() if count > 1])
    if duplicate_ids:
        errors.append("duplicate occurrence IDs: " + ", ".join(duplicate_ids))
    if counts.get("physical_occurrences") not in (None, len(occurrences)):
        errors.append(
            f"counts.physical_occurrences={counts.get('physical_occurrences')} but ledger has {len(occurrences)} rows"
        )
    if counts.get("solids") not in (None, solid_sum):
        errors.append(f"counts.solids={counts.get('solids')} but rows sum to {solid_sum}")
    if conflicts:
        warnings.append(f"visible quantity conflicts: {len(conflicts)}")

    checks = {
        "occurrences_present": bool(occurrences),
        "unique_occurrence_ids": not duplicate_ids and len(ids) == len(occurrences),
        "required_fields_present": not errors,
    }
    report = {
        "schema_version": "v7.0",
        "ledger": str(path),
        "occurrence_count": len(occurrences),
        "solid_count": solid_sum,
        "bom_item_occurrence_counts": dict(sorted(item_counts.items())),
        "quantity_conflict_occurrences": conflicts,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }
    output = args.output.resolve() if args.output else path.with_suffix(".occurrence-audit.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" or args.no_fail else 1


if __name__ == "__main__":
    sys.exit(main())
