from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path


SHAPE_TYPES = {
    "Part::Feature",
    "PartDesign::Feature",
    "PartDesign::Body",
    "Part::FeaturePython",
}


def camera_values(settings: str) -> dict:
    def match_float(name: str):
        match = re.search(rf"\b{name}\s+([-+0-9.eE]+)", settings)
        return float(match.group(1)) if match else None

    def match_vector(name: str, count: int):
        match = re.search(
            rf"\b{name}\s+" + r"\s+".join([r"([-+0-9.eE]+)"] * count),
            settings,
        )
        return [float(value) for value in match.groups()] if match else None

    return {
        "height": match_float("height"),
        "focal_distance": match_float("focalDistance"),
        "position": match_vector("position", 3),
        "orientation": match_vector("orientation", 4),
        "raw": settings,
    }


def parse_document(xml_bytes: bytes) -> tuple[dict[str, str], Counter]:
    root = ET.fromstring(xml_bytes)
    objects = root.find("Objects")
    object_types = {}
    if objects is not None:
        for node in objects.findall("Object"):
            object_types[node.get("name", "")] = node.get("type", "")
    return object_types, Counter(object_types.values())


def visibility_value(view_provider: ET.Element) -> bool | None:
    properties = view_provider.find("Properties")
    if properties is None:
        return None
    for prop in properties.findall("Property"):
        if prop.get("name") != "Visibility":
            continue
        value = prop.find("Bool")
        if value is not None:
            return value.get("value", "false").lower() == "true"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit saved FreeCAD FCStd GUI visibility and camera state without opening FreeCAD."
    )
    parser.add_argument("fcstd", type=Path)
    parser.add_argument("--expected-occurrences", type=int)
    parser.add_argument("--min-camera-height", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()

    path = args.fcstd.resolve()
    if not path.is_file():
        parser.error(f"FCStd not found: {path}")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "Document.xml" not in names:
            raise ValueError("Document.xml is missing; file is not a valid FCStd archive")
        object_types, type_counts = parse_document(archive.read("Document.xml"))
        has_gui = "GuiDocument.xml" in names
        gui_size = 0
        view_providers = []
        camera = {"height": None, "raw": ""}
        if has_gui:
            gui_bytes = archive.read("GuiDocument.xml")
            gui_size = len(gui_bytes)
            gui_root = ET.fromstring(gui_bytes)
            data = gui_root.find("ViewProviderData")
            if data is not None:
                for node in data.findall("ViewProvider"):
                    view_providers.append(
                        {
                            "name": node.get("name", ""),
                            "visible": visibility_value(node),
                        }
                    )
            camera_node = gui_root.find("Camera")
            camera = camera_values(camera_node.get("settings", "")) if camera_node is not None else camera

    visibility = {row["name"]: row["visible"] for row in view_providers}
    shape_names = {name for name, type_id in object_types.items() if type_id in SHAPE_TYPES}
    visible_shape_names = sorted(
        name for name in shape_names if visibility.get(name) is True
    )
    hidden_shape_names = sorted(
        name for name in shape_names if visibility.get(name) is False
    )
    expected_ok = (
        True
        if args.expected_occurrences is None
        else len(visible_shape_names) == args.expected_occurrences
    )
    camera_ok = (
        camera.get("height") is not None
        and camera["height"] >= args.min_camera_height
    )
    checks = {
        "gui_document_present": has_gui,
        "view_providers_present": bool(view_providers),
        "at_least_one_visible_shape": bool(visible_shape_names),
        "expected_visible_occurrences": expected_ok,
        "camera_height_valid": camera_ok,
    }
    report = {
        "schema_version": "v7.0",
        "fcstd": str(path),
        "archive_members": len(names),
        "gui_document_present": has_gui,
        "gui_document_size_bytes": gui_size,
        "object_type_counts": dict(sorted(type_counts.items())),
        "view_provider_count": len(view_providers),
        "visible_view_provider_count": sum(row["visible"] is True for row in view_providers),
        "hidden_view_provider_count": sum(row["visible"] is False for row in view_providers),
        "shape_object_count": len(shape_names),
        "visible_shape_count": len(visible_shape_names),
        "hidden_shape_count": len(hidden_shape_names),
        "visible_shape_names": visible_shape_names,
        "hidden_shape_names": hidden_shape_names,
        "camera": camera,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }
    output = args.output.resolve() if args.output else path.with_suffix(".gui-audit.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" or args.no_fail else 1


if __name__ == "__main__":
    sys.exit(main())
