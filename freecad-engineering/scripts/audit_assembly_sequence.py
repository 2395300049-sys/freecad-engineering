import argparse
import json
from collections import defaultdict, deque
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Audit assembly-sequence completeness and precedence.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    steps = data.get("steps", [])
    all_components = set(data.get("all_components", []))
    preinstalled = set(data.get("preinstalled_components", []))
    issues = []

    step_by_id = {}
    installed_components = []
    graph = defaultdict(list)
    indegree = {}
    for index, step in enumerate(steps):
        step_id = step.get("id")
        if not step_id:
            issues.append({"severity": "blocking", "step": index, "message": "Step ID is missing"})
            continue
        if step_id in step_by_id:
            issues.append({"severity": "blocking", "step": step_id, "message": "Duplicate step ID"})
        step_by_id[step_id] = step
        indegree.setdefault(step_id, 0)
        if step.get("action") == "install":
            installed_components.append(step.get("component"))
        if not step.get("component"):
            issues.append({"severity": "blocking", "step": step_id, "message": "Component is missing"})
        if step.get("insertion_direction") is None or step.get("travel_mm") is None:
            issues.append({"severity": "major", "step": step_id, "message": "Insertion direction/travel is not documented"})
        if not step.get("tool"):
            issues.append({"severity": "major", "step": step_id, "message": "Tool or handling method is missing"})
        if not step.get("inspection"):
            issues.append({"severity": "major", "step": step_id, "message": "Inspection/acceptance point is missing"})

    for step_id, step in step_by_id.items():
        for prerequisite in step.get("prerequisites", []):
            if prerequisite not in step_by_id:
                issues.append({"severity": "blocking", "step": step_id, "message": f"Unknown prerequisite {prerequisite}"})
                continue
            graph[prerequisite].append(step_id)
            indegree[step_id] = indegree.get(step_id, 0) + 1

    queue = deque(sorted(step_id for step_id, degree in indegree.items() if degree == 0))
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for target in graph[current]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(step_by_id):
        issues.append({"severity": "blocking", "step": None, "message": "Assembly prerequisite graph contains a cycle"})

    duplicates = sorted({component for component in installed_components if installed_components.count(component) > 1 and component})
    for component in duplicates:
        issues.append({"severity": "blocking", "step": None, "message": f"Component installed more than once: {component}"})
    accounted = preinstalled | {component for component in installed_components if component}
    missing = sorted(all_components - accounted)
    unexpected = sorted(accounted - all_components)
    if missing:
        issues.append({"severity": "blocking", "step": None, "message": f"Components not installed or preinstalled: {missing}"})
    if unexpected:
        issues.append({"severity": "blocking", "step": None, "message": f"Unexpected components in sequence: {unexpected}"})

    blocking = sum(item["severity"] == "blocking" for item in issues)
    major = sum(item["severity"] == "major" for item in issues)
    report = {
        "input": str(input_path),
        "assembly": data.get("assembly"),
        "component_count": len(all_components),
        "step_count": len(steps),
        "topological_order": order,
        "issues": issues,
        "summary": {"blocking": blocking, "major": major, "pass": blocking == 0, "conditional": blocking == 0 and major > 0},
        "limitations": ["Sequence structure validation does not prove geometric path or tool-envelope clearance."],
    }
    report_path = (args.report or input_path.with_name(input_path.stem + "_audit.json")).resolve()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(report_path)
    raise SystemExit(0 if report["summary"]["pass"] else 2)


if __name__ == "__main__":
    main()
