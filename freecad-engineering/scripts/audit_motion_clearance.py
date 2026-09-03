import argparse
import json
import math
import os
import re
from pathlib import Path

import FreeCAD as App
import Import
import Part


CONTAINER_TYPES = {"App::Part", "App::DocumentObjectGroup", "App::LinkGroup", "PartDesign::Body"}


def parse_args():
    parser = argparse.ArgumentParser(description="Sample rotating component motion and audit real-solid clearance.")
    parser.add_argument("--input")
    parser.add_argument("--plan")
    parser.add_argument("--output")
    args, _ = parser.parse_known_args()
    args.input = args.input or os.environ.get("FREECAD_MOTION_INPUT")
    args.plan = args.plan or os.environ.get("FREECAD_MOTION_PLAN")
    args.output = args.output or os.environ.get("FREECAD_MOTION_OUTPUT")
    if not args.input or not args.plan:
        parser.error("--input and --plan are required")
    return args


def open_model(path):
    if path.suffix.lower() == ".fcstd":
        return App.openDocument(str(path))
    if path.suffix.lower() in {".step", ".stp"}:
        before = set(App.listDocuments())
        Import.open(str(path))
        names = [name for name in App.listDocuments() if name not in before]
        if not names:
            raise RuntimeError("STEP import did not create a document")
        return App.getDocument(names[-1])
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


def is_leaf(obj, linked_definitions):
    if obj.Name in linked_definitions:
        return False
    if obj.TypeId == "App::Link":
        return hasattr(obj, "Shape") and not obj.Shape.isNull() and bool(obj.Shape.Solids)
    if obj.TypeId in CONTAINER_TYPES:
        return False
    if not hasattr(obj, "Shape") or obj.Shape.isNull() or not obj.Shape.Solids:
        return False
    children = [child for child in getattr(obj, "OutList", []) if hasattr(child, "Shape") and not child.Shape.isNull() and child.Shape.Solids]
    return not children


def global_shape(obj):
    shape = obj.Shape.copy()
    try:
        parent = obj.getGlobalPlacement().multiply(obj.Placement.inverse())
        shape.Placement = parent.multiply(shape.Placement)
    except Exception:
        pass
    return shape


def flatten_objects(doc):
    records = []
    linked_definitions = linked_definition_names(doc)
    for obj in doc.Objects:
        if not is_leaf(obj, linked_definitions):
            continue
        shape = global_shape(obj)
        records.append(
            {
                "name": obj.Name,
                "label": obj.Label,
                "display": f"{obj.Label} [{obj.Name}]",
                "shape": Part.makeCompound([solid.copy() for solid in shape.Solids]),
                "valid": shape.isValid(),
            }
        )
    return records


def find_unique(records, value):
    matches = [record for record in records if record["name"] == value or record["label"] == value]
    if len(matches) != 1:
        raise ValueError(f"Object {value!r} matched {len(matches)} physical records")
    return matches[0]


def rotate_shape(shape, origin, direction, angle_deg):
    axis = App.Vector(*direction)
    if axis.Length == 0:
        raise ValueError("Rotation axis direction cannot be zero")
    rotation = App.Rotation(axis, angle_deg)
    placement = App.Placement(App.Vector(0, 0, 0), rotation, App.Vector(*origin))
    result = shape.copy()
    result.Placement = placement.multiply(result.Placement)
    return result


def axis_gap(a_min, a_max, b_min, b_max):
    return max(0.0, b_min - a_max, a_min - b_max)


def bbox_gap(a, b):
    box_a = a.BoundBox
    box_b = b.BoundBox
    dx = axis_gap(box_a.XMin, box_a.XMax, box_b.XMin, box_b.XMax)
    dy = axis_gap(box_a.YMin, box_a.YMax, box_b.YMin, box_b.YMax)
    dz = axis_gap(box_a.ZMin, box_a.ZMax, box_b.ZMin, box_b.ZMax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def pair_metrics(left, right, volume_tolerance):
    gap = bbox_gap(left, right)
    common_volume = 0.0
    if gap <= 1e-7:
        common_volume = float(left.common(right).Volume)
    if common_volume > volume_tolerance:
        return common_volume, 0.0
    return common_volume, float(left.distToShape(right)[0])


def matches_any(record, patterns):
    return any(pattern.search(record["display"]) for pattern in patterns)


def main():
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    doc = open_model(input_path)
    records = flatten_objects(doc)
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    motion_reports = []

    for motion in plan.get("motions", []):
        driver_spec = motion["driver"]
        driver = find_unique(records, driver_spec["object"])
        follower_specs = motion.get("followers", [])
        followers = [(spec, find_unique(records, spec["object"])) for spec in follower_specs]
        moving_names = {driver["name"], *(record["name"] for _, record in followers)}
        excluded_patterns = [re.compile(value, re.IGNORECASE) for value in motion.get("excluded_static_patterns", [])]
        static_records = [record for record in records if record["name"] not in moving_names and not matches_any(record, excluded_patterns)]
        allowed_pairs = set()
        for pair in motion.get("allowed_moving_pairs", []):
            if len(pair) != 2:
                raise ValueError(f"Motion {motion.get('id')} contains an invalid allowed pair")
            allowed_pairs.add(
                frozenset((find_unique(records, pair[0])["name"], find_unique(records, pair[1])["name"]))
            )
        samples = int(motion.get("samples", 0))
        if samples < 2:
            raise ValueError(f"Motion {motion.get('id')} requires at least two samples")
        start = float(driver_spec["start_deg"])
        end = float(driver_spec["end_deg"])
        volume_tolerance = float(motion.get("volume_tolerance_mm3", 1e-5))
        required_clearance = float(motion.get("minimum_required_clearance_mm", 0.0))
        complete_required_travel = bool(motion.get("complete_required_travel", False))
        sample_reports = []
        overall_max_common = 0.0
        overall_min_clearance = math.inf
        worst_common_pair = None
        worst_clearance_pair = None

        for sample_index in range(samples):
            fraction = sample_index / (samples - 1)
            driver_angle = start + (end - start) * fraction
            moving = [
                {
                    "name": driver["name"],
                    "label": driver["label"],
                    "shape": rotate_shape(driver["shape"], driver_spec["axis_origin_mm"], driver_spec["axis_direction"], driver_angle),
                    "angle_deg": driver_angle,
                }
            ]
            for spec, record in followers:
                angle = driver_angle * float(spec.get("angle_ratio", 1.0)) + float(spec.get("phase_deg", 0.0))
                moving.append(
                    {
                        "name": record["name"],
                        "label": record["label"],
                        "shape": rotate_shape(record["shape"], spec["axis_origin_mm"], spec["axis_direction"], angle),
                        "angle_deg": angle,
                    }
                )

            sample_max_common = 0.0
            sample_min_clearance = math.inf
            sample_common_pair = None
            sample_clearance_pair = None
            moving_pair_metrics = []

            for left_index, left in enumerate(moving):
                for right in moving[left_index + 1 :]:
                    common, distance = pair_metrics(left["shape"], right["shape"], volume_tolerance)
                    pair_key = frozenset((left["name"], right["name"]))
                    moving_pair_metrics.append(
                        {"left": left["label"], "right": right["label"], "allowed_pair": pair_key in allowed_pairs, "common_volume_mm3": common, "distance_mm": distance}
                    )
                    if common > sample_max_common:
                        sample_max_common = common
                        sample_common_pair = [left["label"], right["label"]]

                for static in static_records:
                    lower_bound = bbox_gap(left["shape"], static["shape"])
                    if lower_bound > sample_min_clearance and lower_bound > required_clearance:
                        continue
                    common, distance = pair_metrics(left["shape"], static["shape"], volume_tolerance)
                    if common > sample_max_common:
                        sample_max_common = common
                        sample_common_pair = [left["label"], static["label"]]
                    if common <= volume_tolerance and distance < sample_min_clearance:
                        sample_min_clearance = distance
                        sample_clearance_pair = [left["label"], static["label"]]

            if sample_max_common > overall_max_common:
                overall_max_common = sample_max_common
                worst_common_pair = sample_common_pair
            if sample_min_clearance < overall_min_clearance:
                overall_min_clearance = sample_min_clearance
                worst_clearance_pair = sample_clearance_pair
            sample_reports.append(
                {
                    "sample": sample_index,
                    "driver_angle_deg": driver_angle,
                    "moving_angles_deg": {item["label"]: item["angle_deg"] for item in moving},
                    "max_forbidden_common_volume_mm3": sample_max_common,
                    "worst_common_pair": sample_common_pair,
                    "minimum_static_clearance_mm": None if math.isinf(sample_min_clearance) else sample_min_clearance,
                    "minimum_clearance_pair": sample_clearance_pair,
                    "moving_pair_metrics": moving_pair_metrics,
                }
            )

        pass_common = overall_max_common <= volume_tolerance
        pass_clearance = math.isinf(overall_min_clearance) or overall_min_clearance >= required_clearance
        motion_reports.append(
            {
                "id": motion.get("id"),
                "driver": driver["label"],
                "samples": samples,
                "start_deg": start,
                "end_deg": end,
                "max_forbidden_common_volume_mm3": overall_max_common,
                "worst_common_pair": worst_common_pair,
                "minimum_static_clearance_mm": None if math.isinf(overall_min_clearance) else overall_min_clearance,
                "minimum_clearance_pair": worst_clearance_pair,
                "required_clearance_mm": required_clearance,
                "complete_required_travel": complete_required_travel,
                "pass_common": pass_common,
                "pass_clearance": pass_clearance,
                "pass": pass_common and pass_clearance and complete_required_travel,
                "sample_results": sample_reports,
            }
        )

    report = {
        "input": str(input_path),
        "plan": str(plan_path),
        "freecad_version": ".".join(App.Version()[:3]),
        "physical_objects": len(records),
        "motions": motion_reports,
        "pass": bool(motion_reports) and all(item["pass"] for item in motion_reports),
        "limitations": ["Rotations are applied to global shape copies and do not solve native joints or flexible-body motion.", "Sampling proves only evaluated positions; refine around critical clearance."],
    }
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path.with_name(input_path.stem + "_motion_clearance.json")
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "motions": len(motion_reports)}, ensure_ascii=False))
    print(output_path)
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
