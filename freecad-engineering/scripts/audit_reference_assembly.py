import argparse
import json
import os
import sys
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--expected-occurrences", type=int)
    parser.add_argument("--output")
    args, _ = parser.parse_known_args()
    args.input = args.input or os.environ.get("FREECAD_AUDIT_INPUT")
    if args.expected_occurrences is None and os.environ.get("FREECAD_AUDIT_EXPECTED"):
        args.expected_occurrences = int(os.environ["FREECAD_AUDIT_EXPECTED"])
    args.output = args.output or os.environ.get("FREECAD_AUDIT_OUTPUT")
    if not args.input:
        parser.error("--input or FREECAD_AUDIT_INPUT is required")
    return args


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
    if not hasattr(obj, "Shape") or obj.Shape.isNull():
        return False
    if not obj.Shape.Solids:
        return False
    shape_children = [
        child
        for child in getattr(obj, "OutList", [])
        if hasattr(child, "Shape") and not child.Shape.isNull()
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


def shape_record(obj):
    shape = globally_placed_shape(obj)
    box = shape.BoundBox
    return {
        "name": obj.Name,
        "label": obj.Label,
        "type_id": obj.TypeId,
        "linked_target_type": getattr(getattr(obj, "LinkedObject", None), "TypeId", None),
        "solid_count": len(shape.Solids),
        "valid": bool(shape.isValid()),
        "volume_mm3": round(shape.Volume, 6),
        "bounds": {
            "min": [round(box.XMin, 6), round(box.YMin, 6), round(box.ZMin, 6)],
            "size": [round(box.XLength, 6), round(box.YLength, 6), round(box.ZLength, 6)],
        },
    }


def main():
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    doc = open_model(input_path)
    linked_definitions = linked_definition_names(doc)
    leaves = [obj for obj in doc.Objects if is_physical_leaf(obj, linked_definitions)]
    records = [shape_record(obj) for obj in leaves]
    occurrence_count = len(records)
    solid_count = sum(record["solid_count"] for record in records)
    passed = args.expected_occurrences is None or occurrence_count == args.expected_occurrences
    report = {
        "input": str(input_path),
        "freecad_version": ".".join(App.Version()[:3]),
        "physical_occurrence_count": occurrence_count,
        "physical_solid_count": solid_count,
        "expected_occurrences": args.expected_occurrences,
        "passed": passed,
        "objects": records,
    }

    output = Path(args.output).resolve() if args.output else input_path.with_name(
        input_path.stem + "_audit.json"
    )
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "physical_occurrence_count", "physical_solid_count", "expected_occurrences", "passed"
    )}, ensure_ascii=False))
    print(output)
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
