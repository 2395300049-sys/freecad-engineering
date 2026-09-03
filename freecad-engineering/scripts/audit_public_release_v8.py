#!/usr/bin/env python3
"""Block common secrets, machine paths, task artifacts, and cache files before publication."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "venv", "node_modules"}
CACHE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".DS_Store"}
BLOCKED_SUFFIXES = {
    ".fcstd", ".step", ".stp", ".iges", ".igs", ".sldprt", ".sldasm",
    ".dwg", ".dxf", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp",
    ".tif", ".tiff", ".zip", ".7z", ".rar", ".db", ".sqlite", ".log",
}
SECRET_PATTERNS = {
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
PATH_PATTERNS = {
    "windows_absolute_path": re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/](?:[^\s`\"'<>|]+[\\/]?)+"),
    "windows_user_profile": re.compile(r"(?i)\b[A-Za-z]:[\\/]Users[\\/][^\\/\s]+"),
    "posix_user_home": re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/[^/\s]+/"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Repository root to audit")
    parser.add_argument("--allow", action="append", default=[], help="Reviewed relative glob to allow")
    parser.add_argument("--json-report", type=Path, help="Optional report output path")
    return parser.parse_args()


def allowed(relative: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def add(findings: list[dict[str, object]], kind: str, path: str, detail: str, line: int | None = None) -> None:
    item: dict[str, object] = {"kind": kind, "path": path, "detail": detail}
    if line is not None:
        item["line"] = line
    findings.append(item)


def audit(root: Path, allow_patterns: list[str]) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository root is not a directory: {root}")

    findings: list[dict[str, object]] = []
    scanned_files = 0
    skill_dirs: set[Path] = set()

    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if any(part in SKIP_DIRS for part in relative_path.parts):
            continue
        if allowed(relative, allow_patterns):
            continue
        if any(part in CACHE_NAMES for part in relative_path.parts):
            add(findings, "cache_or_temporary", relative, "Cache or temporary path is not publishable")
            continue
        if path.is_dir():
            continue
        scanned_files += 1
        if path.name == "SKILL.md":
            skill_dirs.add(path.parent)
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            add(findings, "task_or_binary_artifact", relative, f"Blocked extension: {path.suffix.lower()}")

        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            add(findings, "unreviewed_binary", relative, "File is not UTF-8 text")
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    add(findings, name, relative, "High-confidence secret pattern", line_number)
            for name, pattern in PATH_PATTERNS.items():
                match = pattern.search(line)
                if match:
                    add(findings, name, relative, match.group(0), line_number)

    for skill_dir in sorted(skill_dirs):
        nested_readme = skill_dir / "README.md"
        if nested_readme.exists():
            add(
                findings,
                "skill_package_clutter",
                nested_readme.relative_to(root).as_posix(),
                "Place public documentation at repository root, outside the Skill folder",
            )

    report: dict[str, object] = {
        "schema": "freecad.public-release-audit/v8",
        "root": str(root),
        "scanned_files": scanned_files,
        "allow_patterns": allow_patterns,
        "findings": findings,
        "pass": not findings,
    }
    return report


def main() -> int:
    args = parse_args()
    try:
        report = audit(args.root, args.allow)
    except Exception as exc:
        report = {"schema": "freecad.public-release-audit/v8", "pass": False, "error": str(exc)}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("pass") else 2


if __name__ == "__main__":
    sys.exit(main())
