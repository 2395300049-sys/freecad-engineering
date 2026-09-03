from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a V7 delivery manifest containing file roles, sizes and SHA-256 hashes."
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--roles", type=Path, help="Optional JSON object mapping relative path to role.")
    parser.add_argument("--required", action="append", default=[])
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--project", default="PROJECT_NAME")
    parser.add_argument("--revision", default="v7.0_r01")
    parser.add_argument("--release-state", default="engineering-review-required")
    args = parser.parse_args()

    directory = args.directory.resolve()
    if not directory.is_dir():
        parser.error(f"Directory not found: {directory}")
    output = (
        args.output.resolve()
        if args.output
        else directory / f"delivery-manifest-{args.revision}.json"
    )
    roles = {}
    if args.roles:
        roles = json.loads(args.roles.resolve().read_text(encoding="utf-8"))
        if not isinstance(roles, dict):
            parser.error("roles JSON must be an object mapping relative path to role")

    iterator = directory.rglob("*") if args.recursive else directory.iterdir()
    files = []
    for path in sorted(iterator, key=lambda item: str(item).lower()):
        if not path.is_file() or path.resolve() == output:
            continue
        relative = path.relative_to(directory).as_posix()
        files.append(
            {
                "path": relative,
                "role": roles.get(relative, "supporting artifact"),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    available = {row["path"] for row in files}
    missing_required = sorted(set(args.required) - available)
    report = {
        "schema_version": "v7.0",
        "project": args.project,
        "revision": args.revision,
        "release_state": args.release_state,
        "directory": str(directory),
        "file_count": len(files),
        "files": files,
        "required_files": args.required,
        "missing_required_files": missing_required,
        "status": "pass" if not missing_required else "fail",
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
