import argparse
import json
import re
from pathlib import Path


ROOT_PATTERN = re.compile(r"^\d{2}_.+_v6\.\d+$")
PART_PATTERN = re.compile(r"^\d{3}_.+_v6\.\d+$")
REQUIRED_ROOT_PREFIXES = {
    "00_先看说明_",
    "01_任务配置与输入_",
    "02_原始资料与证据_",
    "03_识图与特征语义_",
    "04_零件模型_",
    "05_原生装配体_",
    "06_二维工程图_原图复现_",
    "07_二维工程图_工程增强_",
    "08_对比与验证_",
    "09_工艺公差与检验_",
    "10_BOM成本与供应链_",
    "11_便携源码与导出_",
    "12_错误经验与版本记录_",
}
PART_SUBFOLDERS = {
    "01_输入与证据",
    "02_参数化三维模型",
    "03_原图复现工程图",
    "04_工程增强工程图",
    "05_源码与格式导出",
    "06_公差工艺与检验",
    "07_验证与迭代记录",
}


def main():
    parser = argparse.ArgumentParser(description="Audit the V6 engineering delivery layout.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-parts", type=int)
    parser.add_argument("--intent", choices=("source_faithful", "engineering_enhanced", "both"), default="both")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)

    issues = []
    root_folders = sorted(path for path in root.iterdir() if path.is_dir())
    numbered = [path for path in root_folders if ROOT_PATTERN.match(path.name)]
    prefixes_found = {prefix for prefix in REQUIRED_ROOT_PREFIXES if any(path.name.startswith(prefix) for path in numbered)}
    missing_prefixes = REQUIRED_ROOT_PREFIXES - prefixes_found
    if missing_prefixes:
        issues.append(f"Missing required root folders: {sorted(missing_prefixes)}")

    parts_roots = [path for path in root_folders if path.name.startswith("04_零件模型_")]
    parts = []
    if len(parts_roots) != 1:
        issues.append(f"Expected one parts root, found {len(parts_roots)}")
    else:
        parts = sorted(path for path in parts_roots[0].iterdir() if path.is_dir())
        for part in parts:
            if not PART_PATTERN.match(part.name):
                issues.append(f"Invalid part folder name: {part.name}")
            subfolders = {path.name for path in part.iterdir() if path.is_dir()}
            if subfolders != PART_SUBFOLDERS:
                issues.append(f"Unexpected subfolders in {part.name}: {sorted(subfolders)}")

    if args.expected_parts is not None and len(parts) != args.expected_parts:
        issues.append(f"Expected {args.expected_parts} part folders, found {len(parts)}")

    job_configs = list(root.glob("01_任务配置与输入_*/*job*.json")) + list(root.glob("01_任务配置与输入_*/*任务*.json"))
    profiles = list(root.glob("01_任务配置与输入_*/*profile*.json")) + list(root.glob("01_任务配置与输入_*/*配置*.json"))
    annotation_traces = list(root.glob("03_识图与特征语义_*/*annotation*.json")) + list(root.glob("03_识图与特征语义_*/*标注*.json"))
    comparisons = list(root.glob("08_对比与验证_*/*.json"))
    manifests = list(root.glob("*_交付清单_v6.*.json"))

    if not job_configs:
        issues.append("V6 job configuration is missing")
    if not profiles:
        issues.append("Drawing profile is missing")
    if not annotation_traces:
        issues.append("Annotation trace file is missing")
    if not comparisons:
        issues.append("Comparison/validation JSON is missing")
    if len(manifests) != 1:
        issues.append(f"Expected one V6 delivery manifest, found {len(manifests)}")

    source_pdfs = list(root.glob("06_二维工程图_原图复现_*/*.pdf"))
    enhanced_pdfs = list(root.glob("07_二维工程图_工程增强_*/*.pdf"))
    if args.intent in {"source_faithful", "both"} and not source_pdfs:
        issues.append("Source-faithful drawing PDF is missing")
    if args.intent in {"engineering_enhanced", "both"} and not enhanced_pdfs:
        issues.append("Engineering-enhanced drawing PDF is missing")

    report = {
        "root": str(root),
        "numbered_root_folders": len(numbered),
        "part_folders": len(parts),
        "intent": args.intent,
        "issues": issues,
        "pass": not issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
