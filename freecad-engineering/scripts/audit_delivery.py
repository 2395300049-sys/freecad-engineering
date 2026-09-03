#!/usr/bin/env python3
"""Audit a numbered FreeCAD Python delivery and optionally execute each model."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path


SERIAL_RE = re.compile(r"^\d+(?:-\d+)*$")
BAD_TOKENS = ("**file**", "**name**", "[TO" + "DO")


def issue(level: str, code: str, path: Path, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "path": str(path), "message": message}


def read_utf8(path: Path, findings: list[dict[str, str]]) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        findings.append(issue("error", "encoding", path, f"not valid UTF-8: {exc}"))
        return None


def check_python(path: Path, findings: list[dict[str, str]]) -> None:
    text = read_utf8(path, findings)
    if text is None:
        return
    try:
        compile(text, str(path), "exec")
    except SyntaxError as exc:
        findings.append(issue("error", "syntax", path, f"line {exc.lineno}: {exc.msg}"))
    for token in BAD_TOKENS:
        if token in text:
            findings.append(issue("error", "corrupt-token", path, f"contains {token!r}"))
    if "Path(__file__)" in text and "'__file__' in globals()" not in text and '"__file__" in globals()' not in text:
        findings.append(issue("warning", "console-file", path, "uses __file__ without a console fallback"))
    if "except Exception" in text and "pass" in text:
        findings.append(issue("warning", "silent-exception", path, "contains a broad exception path that may hide a failed feature"))


def check_text_paths(path: Path, root: Path, findings: list[dict[str, str]]) -> None:
    text = read_utf8(path, findings)
    if text is None:
        return
    for match in re.finditer(r"[A-Za-z]:\\[^\r\n`\"']+", text):
        raw = match.group(0).rstrip(" .,:;)")
        candidate = Path(raw)
        if not candidate.exists():
            findings.append(issue("warning", "stale-path", path, f"referenced path does not exist: {raw}"))
    if "锛" in text or "鈥" in text or "楠" in text:
        findings.append(issue("warning", "mojibake", path, "text appears to contain encoding corruption"))
    if str(root.parent) in text and str(root) not in text:
        findings.append(issue("info", "external-root", path, "contains an absolute path outside the delivery root"))


def run_model(freecad_cmd: Path, model: Path, findings: list[dict[str, str]], timeout: int) -> dict[str, object]:
    started = time.time()
    before = {p: p.stat().st_mtime for p in model.parent.glob("*.FCStd")}
    try:
        proc = subprocess.run(
            [str(freecad_cmd), str(model)],
            cwd=str(model.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        findings.append(issue("error", "timeout", model, f"FreeCADCmd exceeded {timeout}s"))
        return {"exit_code": None, "duration_s": round(time.time() - started, 3), "regenerated_fcstd": []}

    if proc.returncode != 0:
        tail = (proc.stdout + "\n" + proc.stderr)[-2000:].strip()
        findings.append(issue("error", "freecad-exit", model, f"exit {proc.returncode}: {tail}"))
    regenerated = []
    for output in model.parent.glob("*.FCStd"):
        previous = before.get(output)
        if output.stat().st_mtime >= started - 1 or previous is None:
            regenerated.append(str(output))
    if proc.returncode == 0 and not regenerated:
        findings.append(issue("warning", "stale-output", model, "run succeeded but no FCStd timestamp changed"))
    return {
        "exit_code": proc.returncode,
        "duration_s": round(time.time() - started, 3),
        "regenerated_fcstd": regenerated,
        "output_tail": (proc.stdout + "\n" + proc.stderr)[-2000:].strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="delivery root containing numbered serial folders")
    parser.add_argument("--freecad-cmd", type=Path)
    parser.add_argument("--run", action="store_true", help="execute every model.py with FreeCADCmd")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--report", type=Path, help="report path; defaults to ROOT/audit-report.json")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    report_path = (args.report or root / "audit-report.json").resolve()
    findings: list[dict[str, str]] = []
    runs: dict[str, object] = {}

    if not root.is_dir():
        print(f"delivery root not found: {root}", file=sys.stderr)
        return 2
    if args.run and (not args.freecad_cmd or not args.freecad_cmd.is_file()):
        print("--run requires an existing --freecad-cmd", file=sys.stderr)
        return 2

    serial_dirs = sorted(
        (p for p in root.iterdir() if p.is_dir() and SERIAL_RE.fullmatch(p.name)),
        key=lambda p: [int(part) for part in p.name.split("-")],
    )
    if not serial_dirs:
        findings.append(issue("error", "no-serials", root, "no numbered serial folders found"))

    for serial_dir in serial_dirs:
        model = serial_dir / "model.py"
        if not model.is_file():
            findings.append(issue("error", "missing-model", serial_dir, "model.py is missing"))
            continue
        check_python(model, findings)
        macros = list(serial_dir.glob("*.FCMacro"))
        if not macros:
            findings.append(issue("warning", "missing-macro", serial_dir, "no GUI macro wrapper found"))
        for macro in macros:
            check_python(macro, findings)
            check_text_paths(macro, root, findings)
        if args.run:
            runs[serial_dir.name] = run_model(args.freecad_cmd.resolve(), model, findings, args.timeout)

    for pattern in ("*.md", "*.ps1", "*.json"):
        for path in root.rglob(pattern):
            if path.resolve() == report_path:
                continue
            check_text_paths(path, root, findings)

    counts = {level: sum(1 for item in findings if item["level"] == level) for level in ("error", "warning", "info")}
    report = {
        "root": str(root),
        "serials": [p.name for p in serial_dirs],
        "run_enabled": args.run,
        "counts": counts,
        "findings": findings,
        "runs": runs,
        "limitations": [
            "Static audit cannot prove geometric correctness.",
            "A zero FreeCADCmd exit code cannot prove GUI visibility or engineering drawing quality.",
            "Perform dimensional, projection, TechDraw, and GUI screenshot gates separately.",
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), "serials": len(serial_dirs), **counts}, ensure_ascii=False))
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
