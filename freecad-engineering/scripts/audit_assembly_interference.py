import argparse
import json
import math
import os
import re
from pathlib import Path

import FreeCAD as App
import Import


CONTAINER_TYPES = {
    "App::Part",
    "App::DocumentObjectGroup",
    "App::LinkGroup",
    "PartDesign::Body",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit physical leaf solids for Boolean interference and clearance."
    )
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--focus", action="append", default=[])
    parser.add_argument("--approved-pairs")
    parser.add_argument("--volume-tolerance-mm3", type=float, default=1.0e-5)
    parser.add_argument("--distance-tolerance-mm", type=float, default=1.0e-4)
    parser.add_argument("--report-clearance-mm", type=float, default=0.0)
    parser.add_argument("--fail-on-contact", action="store_true")
    args, _ = parser.parse_known_args()
    args.input = args.input or os.environ.get("FREECAD_INTERFERENCE_INPUT")
    args.output = args.output or os.environ.get("FREECAD_INTERFERENCE_OUTPUT")
    if not args.input:
        parser.error("--input or FREECAD_INTERFERENCE_INPUT is required")
    if args.volume_tolerance_mm3 < 0 or args.distance_tolerance_mm < 0:
        parser.error("tolerances must be non-negative")
    if args.report_clearance_mm < 0:
        parser.error("--report-clearance-mm must be non-negative")
    return args


def load_approval_rules(path_value):
    if not path_value:
        return []
    path = Path(path_value).expanduser().resolve()
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    raw_rules = payload.get("approved_pairs", []) if isinstance(payload, dict) else payload
    rules = []
    for index, rule in enumerate(raw_rules, start=1):
        if not isinstance(rule, dict) or "left" not in rule or "right" not in rule:
            raise ValueError(f"Invalid approval rule {index}: left and right are required")
        classifications = rule.get("classifications", ["contact"])
        rules.append(
            {
                "left": re.compile(rule["left"], re.IGNORECASE),
                "right": re.compile(rule["right"], re.IGNORECASE),
                "classifications": set(classifications),
                "reason": rule.get("reason", "No reason supplied"),
                "source_index": index,
            }
        )
    return rules


def open_model(path):
    suffix = path.suffix.lower()
    if suffix == ".fcstd":
        return App.openDocument(str(path))
    if suffix in {".step", ".stp"}:
        before = set(App.listDocuments())
        Import.open(str(path))
        created = [name for name in App.listDocuments() if name not in before]
        if not created:
            raise RuntimeError("STEP import did not create a document")
        return App.getDocument(created[-1])
    raise ValueError(f"Unsupported input: {path.suffix}")


def linked_definition_names(doc):
    names = set()
    for link in doc.Objects:
        if link.TypeId != "App::Link" or getattr(link, "LinkedObject", None) is None:
            continue
        queue = [link.LinkedObject]
        while queue:
            obj = queue.pop()
            if obj.Name in names:
                continue
            names.add(obj.Name)
            queue.extend(getattr(obj, "OutList", []))
    return names


def is_physical_leaf(obj, linked_definitions):
    if obj.Name in linked_definitions:
        return False
    if obj.TypeId == "App::Link":
        return hasattr(obj, "Shape") and not obj.Shape.isNull() and bool(obj.Shape.Solids)
    if obj.TypeId in CONTAINER_TYPES:
        return False
    if not hasattr(obj, "Shape") or obj.Shape.isNull() or not obj.Shape.Solids:
        return False
    shape_children = [
        child
        for child in getattr(obj, "OutList", [])
        if hasattr(child, "Shape") and not child.Shape.isNull() and child.Shape.Solids
    ]
    return not shape_children


def globally_placed_shape(obj):
    shape = obj.Shape.copy()
    try:
        local_placement = obj.Placement
        global_placement = obj.getGlobalPlacement()
        parent_placement = global_placement.multiply(local_placement.inverse())
        shape.Placement = parent_placement.multiply(shape.Placement)
    except Exception:
        pass
    return shape


def bounds_record(box):
    return {
        "min": [box.XMin, box.YMin, box.ZMin],
        "max": [box.XMax, box.YMax, box.ZMax],
        "size": [box.XLength, box.YLength, box.ZLength],
    }


def flatten_solids(doc):
    records = []
    linked_definitions = linked_definition_names(doc)
    for obj in doc.Objects:
        if not is_physical_leaf(obj, linked_definitions):
            continue
        shape = globally_placed_shape(obj)
        solids = list(shape.Solids)
        audit_internal_pairs = (
            obj.TypeId == "App::Link"
            and getattr(getattr(obj, "LinkedObject", None), "TypeId", None)
            == "Assembly::AssemblyObject"
        )
        for index, solid in enumerate(solids, start=1):
            records.append(
                {
                    "id": f"{obj.Name}::solid_{index}",
                    "object_name": obj.Name,
                    "label": obj.Label,
                    "type_id": obj.TypeId,
                    "solid_index": index,
                    "source_solid_count": len(solids),
                    "audit_internal_pairs": audit_internal_pairs,
                    "shape": solid.copy(),
                    "valid": bool(solid.isValid()),
                    "volume_mm3": float(solid.Volume),
                    "bounds": bounds_record(solid.BoundBox),
                }
            )
    return records


def axis_gap(a_min, a_max, b_min, b_max):
    return max(0.0, b_min - a_max, a_min - b_max)


def bbox_gap(a, b):
    a_box = a.BoundBox
    b_box = b.BoundBox
    dx = axis_gap(a_box.XMin, a_box.XMax, b_box.XMin, b_box.XMax)
    dy = axis_gap(a_box.YMin, a_box.YMax, b_box.YMin, b_box.YMax)
    dz = axis_gap(a_box.ZMin, a_box.ZMax, b_box.ZMin, b_box.ZMax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def display_name(record):
    return f"{record['label']} [{record['id']}]"


def matches_focus(record, patterns):
    if not patterns:
        return True
    value = f"{record['object_name']} {record['label']} {record['id']}"
    return any(pattern.search(value) for pattern in patterns)


def public_record(record):
    return {key: value for key, value in record.items() if key != "shape"}


def approval_for_pair(left, right, classification, rules):
    left_value = display_name(left)
    right_value = display_name(right)
    for rule in rules:
        if classification not in rule["classifications"]:
            continue
        forward = rule["left"].search(left_value) and rule["right"].search(right_value)
        reverse = rule["left"].search(right_value) and rule["right"].search(left_value)
        if forward or reverse:
            return rule
    return None


def audit_pairs(records, args, approval_rules):
    patterns = [re.compile(value, re.IGNORECASE) for value in args.focus]
    broad_limit = max(args.distance_tolerance_mm, args.report_clearance_mm)
    pairs = []
    boolean_errors = []
    total_pairs = 0
    candidate_pairs = 0

    for left_index, left in enumerate(records):
        for right in records[left_index + 1 :]:
            if (
                left["object_name"] == right["object_name"]
                and not (left["audit_internal_pairs"] and right["audit_internal_pairs"])
            ):
                continue
            if patterns and not (matches_focus(left, patterns) or matches_focus(right, patterns)):
                continue
            total_pairs += 1
            gap = bbox_gap(left["shape"], right["shape"])
            if gap > broad_limit:
                continue
            candidate_pairs += 1
            pair = {
                "left_id": left["id"],
                "left_label": left["label"],
                "right_id": right["id"],
                "right_label": right["label"],
                "bbox_gap_mm": gap,
            }
            try:
                common_volume = 0.0
                common_solid_count = 0
                if gap <= args.distance_tolerance_mm:
                    common = left["shape"].common(right["shape"])
                    common_volume = float(common.Volume)
                    common_solid_count = len(common.Solids)

                if common_volume > args.volume_tolerance_mm3:
                    raw_classification = "interference"
                    distance = 0.0
                else:
                    distance = float(left["shape"].distToShape(right["shape"])[0])
                    raw_classification = (
                        "contact"
                        if distance <= args.distance_tolerance_mm
                        else "clearance"
                    )

                approval = approval_for_pair(
                    left, right, raw_classification, approval_rules
                )
                classification = (
                    f"approved_{raw_classification}" if approval else raw_classification
                )

                pair.update(
                    {
                        "classification": classification,
                        "raw_classification": raw_classification,
                        "common_volume_mm3": common_volume,
                        "common_solid_count": common_solid_count,
                        "minimum_distance_mm": distance,
                        "approved": bool(approval),
                        "approval_rule": approval["source_index"] if approval else None,
                        "approval_reason": approval["reason"] if approval else None,
                    }
                )
                if (
                    raw_classification != "clearance"
                    or args.report_clearance_mm > 0
                    and distance <= args.report_clearance_mm
                ):
                    pairs.append(pair)
            except Exception as exc:
                error = {
                    **pair,
                    "classification": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
                pairs.append(error)
                boolean_errors.append(error)

    return total_pairs, candidate_pairs, pairs, boolean_errors


def main():
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    doc = open_model(input_path)
    records = flatten_solids(doc)
    approval_rules = load_approval_rules(args.approved_pairs)
    total_pairs, candidate_pairs, pairs, boolean_errors = audit_pairs(
        records, args, approval_rules
    )

    interference_count = sum(
        pair.get("classification") == "interference" for pair in pairs
    )
    contact_count = sum(pair.get("classification") == "contact" for pair in pairs)
    approved_interference_count = sum(
        pair.get("classification") == "approved_interference" for pair in pairs
    )
    approved_contact_count = sum(
        pair.get("classification") == "approved_contact" for pair in pairs
    )
    clearance_count = sum(pair.get("classification") == "clearance" for pair in pairs)
    invalid_count = sum(not record["valid"] for record in records)
    passed = (
        interference_count == 0
        and invalid_count == 0
        and not boolean_errors
        and (not args.fail_on_contact or contact_count == 0)
    )

    report = {
        "input": str(input_path),
        "freecad_version": ".".join(App.Version()[:3]),
        "scope": {
            "focus_patterns": args.focus or ["ALL"],
            "approved_pairs_file": str(Path(args.approved_pairs).resolve())
            if args.approved_pairs
            else None,
            "approval_rule_count": len(approval_rules),
        },
        "tolerances": {
            "volume_mm3": args.volume_tolerance_mm3,
            "distance_mm": args.distance_tolerance_mm,
            "reported_clearance_mm": args.report_clearance_mm,
        },
        "summary": {
            "physical_leaf_solids": len(records),
            "invalid_solids": invalid_count,
            "evaluated_pairs": total_pairs,
            "broad_phase_candidates": candidate_pairs,
            "interferences": interference_count,
            "contacts": contact_count,
            "approved_interferences": approved_interference_count,
            "approved_contacts": approved_contact_count,
            "reported_clearances": clearance_count,
            "boolean_errors": len(boolean_errors),
            "pass": passed,
        },
        "solids": [public_record(record) for record in records],
        "pairs": pairs,
    }

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(input_path.stem + "_interference_audit.json")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(output_path)
    raise SystemExit(0 if passed else 2)


if __name__ == "__main__":
    main()
