#!/usr/bin/env python3
"""Validate FreeCAD V8 geometry, engineering, and production release declarations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_GATE_STATES = {"pass", "fail", "blocked", "not_applicable"}
GEOMETRY_REQUIRED = {
    "source_evidence", "geometry", "critical_dimensions", "step_exchange",
    "gui_state", "viewport", "clean_room",
}
ENGINEERING_GATES = {
    "occurrence_placement", "assembly", "interference", "motion", "drawing",
    "manufacturing", "inspection", "service", "standards",
}


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if data.get("schema") != "freecad.release-status/v8":
        errors.append("schema must equal freecad.release-status/v8")

    gates = data.get("gates")
    states = data.get("declared_states")
    findings = data.get("blocking_findings")
    approval = data.get("production_approval")
    if not isinstance(gates, dict):
        gates = {}
        errors.append("gates must be an object")
    if not isinstance(states, dict):
        states = {}
        errors.append("declared_states must be an object")
    if not isinstance(findings, list):
        findings = []
        errors.append("blocking_findings must be a list")
    if not isinstance(approval, dict):
        approval = {}
        errors.append("production_approval must be an object")

    for name, value in gates.items():
        if value not in VALID_GATE_STATES:
            errors.append(f"gate {name!r} has invalid state {value!r}")
    missing = sorted(GEOMETRY_REQUIRED - set(gates))
    if missing:
        errors.append("missing geometry gates: " + ", ".join(missing))

    geometry_evidence_passes = all(gates.get(name) == "pass" for name in GEOMETRY_REQUIRED)
    optional_geometry = gates.get("occurrence_placement", "not_applicable")
    geometry_evidence_passes = geometry_evidence_passes and optional_geometry in {"pass", "not_applicable"}

    geometry_declared = states.get("geometry_review_ready") is True
    engineering_declared = states.get("engineering_review_ready") is True
    production_declared = states.get("production_release_ready") is True

    if geometry_declared and not geometry_evidence_passes:
        errors.append("geometry_review_ready is declared without passing geometry evidence")

    engineering_evidence_passes = geometry_declared and all(
        gates.get(name, "not_applicable") in {"pass", "not_applicable"} for name in ENGINEERING_GATES
    )
    if engineering_declared and not engineering_evidence_passes:
        errors.append("engineering_review_ready is declared without passing applicable engineering evidence")

    approval_complete = (
        approval.get("approved") is True
        and bool(approval.get("approver"))
        and bool(approval.get("date"))
        and bool(approval.get("scope"))
    )
    if production_declared:
        if not engineering_declared:
            errors.append("production_release_ready requires engineering_review_ready")
        if findings:
            errors.append("production_release_ready requires zero blocking findings")
        if not approval_complete:
            errors.append("production_release_ready requires a complete responsible-engineer approval")
        if any(value in {"fail", "blocked"} for value in gates.values()):
            errors.append("production_release_ready cannot contain failed or blocked gates")

    computed = {
        "geometry_evidence_passes": geometry_evidence_passes,
        "engineering_evidence_passes": engineering_evidence_passes,
        "approval_complete": approval_complete,
    }
    return {
        "schema": "freecad.release-status-validation/v8",
        "job_id": data.get("job_id"),
        "computed": computed,
        "errors": errors,
        "pass": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.status.read_text(encoding="utf-8-sig"))
        report = validate(data)
    except Exception as exc:
        report = {"schema": "freecad.release-status-validation/v8", "pass": False, "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("pass") else 2


if __name__ == "__main__":
    sys.exit(main())
