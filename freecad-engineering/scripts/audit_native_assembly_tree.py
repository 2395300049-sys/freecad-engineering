import argparse
import json
import os
from collections import defaultdict, deque
from pathlib import Path

import FreeCAD as App


def parse_args():
    parser = argparse.ArgumentParser(description="Audit native FreeCAD Assembly objects, links, joints, grounding, and expected relationships.")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--relationships")
    parser.add_argument("--expected-components", type=int)
    args, _ = parser.parse_known_args()
    args.input = args.input or os.environ.get("FREECAD_ASSEMBLY_INPUT")
    args.output = args.output or os.environ.get("FREECAD_ASSEMBLY_OUTPUT")
    if not args.input:
        parser.error("--input or FREECAD_ASSEMBLY_INPUT is required")
    return args


def object_name(value):
    if value is None:
        return None
    if hasattr(value, "Name"):
        return value.Name
    if isinstance(value, (list, tuple)) and value:
        first = value[0]
        if hasattr(first, "Name"):
            return first.Name
        if isinstance(first, str):
            return first.split(".")[0]
    if isinstance(value, str):
        return value.split(".")[0]
    return None


def ref_record(joint, property_name):
    if not hasattr(joint, property_name):
        return {"present": False, "object": None, "raw": None}
    value = getattr(joint, property_name)
    raw = str(value)
    return {"present": value is not None, "object": object_name(value), "raw": raw}


def descendants(root):
    result = []
    queue = deque(getattr(root, "OutList", []))
    seen = set()
    while queue:
        obj = queue.popleft()
        if obj.Name in seen:
            continue
        seen.add(obj.Name)
        result.append(obj)
        queue.extend(getattr(obj, "OutList", []))
    return result


def find_by_name_or_label(doc, value):
    matches = [obj for obj in doc.Objects if obj.Name == value or obj.Label == value]
    return matches


def main():
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    doc = App.openDocument(str(input_path))

    assemblies = [obj for obj in doc.Objects if obj.TypeId == "Assembly::AssemblyObject" or obj.TypeId.startswith("Assembly::AssemblyObject")]
    joint_groups = [obj for obj in doc.Objects if obj.TypeId == "Assembly::JointGroup"]
    links = [obj for obj in doc.Objects if obj.TypeId == "App::Link"]
    all_joint_candidates = [obj for obj in doc.Objects if hasattr(obj, "JointType") or hasattr(obj, "ObjectToGround")]
    grounded = [obj for obj in all_joint_candidates if hasattr(obj, "ObjectToGround") and getattr(obj, "ObjectToGround", None) is not None]

    joint_records = []
    incomplete_joints = []
    graph = defaultdict(set)
    for joint in all_joint_candidates:
        is_grounded = hasattr(joint, "ObjectToGround")
        ref1 = ref_record(joint, "Reference1")
        ref2 = ref_record(joint, "Reference2")
        joint_type = "Grounded" if is_grounded else str(getattr(joint, "JointType", "Unknown"))
        valid_refs = bool(getattr(joint, "ObjectToGround", None)) if is_grounded else ref1["present"] and ref2["present"]
        if not valid_refs:
            incomplete_joints.append(joint.Name)
        if not is_grounded and ref1["object"] and ref2["object"]:
            graph[ref1["object"]].add(ref2["object"])
            graph[ref2["object"]].add(ref1["object"])
        joint_records.append(
            {
                "name": joint.Name,
                "label": joint.Label,
                "type_id": joint.TypeId,
                "joint_type": joint_type,
                "reference1": ref1,
                "reference2": ref2,
                "grounded_object": object_name(getattr(joint, "ObjectToGround", None)),
                "references_complete": valid_refs,
            }
        )

    assembly_records = []
    for assembly in assemblies:
        children = descendants(assembly)
        assembly_records.append(
            {
                "name": assembly.Name,
                "label": assembly.Label,
                "linked_occurrences": [obj.Name for obj in children if obj.TypeId == "App::Link"],
                "joint_groups": [obj.Name for obj in children if obj.TypeId == "Assembly::JointGroup"],
                "child_count": len(children),
            }
        )

    expected_issues = []
    relationship_data = None
    if args.relationships:
        relationship_path = Path(args.relationships).expanduser().resolve()
        relationship_data = json.loads(relationship_path.read_text(encoding="utf-8-sig"))
        root_name = relationship_data.get("root_assembly")
        if root_name and not find_by_name_or_label(doc, root_name):
            expected_issues.append(f"Expected root assembly not found: {root_name}")
        grounded_name = relationship_data.get("grounded_component")
        actual_grounded = {record["grounded_object"] for record in joint_records if record["grounded_object"]}
        grounded_matches = find_by_name_or_label(doc, grounded_name) if grounded_name else []
        if grounded_name and not any(obj.Name in actual_grounded for obj in grounded_matches):
            expected_issues.append(f"Expected grounded component not found in grounded relations: {grounded_name}")
        for component in relationship_data.get("components", []):
            occurrence = component.get("occurrence")
            matches = find_by_name_or_label(doc, occurrence)
            if len(matches) != 1:
                expected_issues.append(f"Expected component {occurrence} matched {len(matches)} objects")
            elif matches[0].TypeId != "App::Link":
                expected_issues.append(f"Expected component {occurrence} is {matches[0].TypeId}, not App::Link")
        for expected_joint in relationship_data.get("joints", []):
            matches = [record for record in joint_records if record["name"] == expected_joint.get("name") or record["label"] == expected_joint.get("name")]
            if len(matches) != 1:
                expected_issues.append(f"Expected joint {expected_joint.get('name')} matched {len(matches)} records")
                continue
            if matches[0]["joint_type"] != expected_joint.get("type"):
                expected_issues.append(f"Joint {expected_joint.get('name')} type is {matches[0]['joint_type']}, expected {expected_joint.get('type')}")

    graph_nodes = set(graph)
    for neighbors in graph.values():
        graph_nodes.update(neighbors)
    connected_groups = []
    remaining = set(graph_nodes)
    while remaining:
        start = next(iter(remaining))
        group = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node in group:
                continue
            group.add(node)
            queue.extend(graph.get(node, []))
        remaining -= group
        connected_groups.append(sorted(group))

    issues = []
    if not assemblies:
        issues.append("No Assembly::AssemblyObject found; document is not a native assembly")
    if not joint_groups:
        issues.append("No Assembly::JointGroup found")
    if not links:
        issues.append("No App::Link component occurrences found")
    if not grounded:
        issues.append("No grounded component relation found")
    if incomplete_joints:
        issues.append(f"Joints with incomplete references: {incomplete_joints}")
    if args.expected_components is not None and len(links) != args.expected_components:
        issues.append(f"Expected {args.expected_components} App::Link occurrences, found {len(links)}")
    issues.extend(expected_issues)

    report = {
        "input": str(input_path),
        "freecad_version": ".".join(App.Version()[:3]),
        "summary": {
            "native_assembly_objects": len(assemblies),
            "app_link_occurrences": len(links),
            "joint_groups": len(joint_groups),
            "joint_records": len(joint_records),
            "grounded_relations": len(grounded),
            "incomplete_joints": len(incomplete_joints),
            "connected_joint_graph_groups": len(connected_groups),
            "pass": not issues,
        },
        "assemblies": assembly_records,
        "joints": joint_records,
        "connected_joint_graph_groups": connected_groups,
        "issues": issues,
        "limitations": ["Graph connectivity is based on exposed Joint references and may require project relationship metadata for deeply nested subelements.", "Global mechanism DOF is not inferred by summing joint types."],
    }
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path.with_name(input_path.stem + "_native_assembly_audit.json")
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(output_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
