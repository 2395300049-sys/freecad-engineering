import argparse
import json
import re
from pathlib import Path


ROOT_PATTERN = re.compile(r"^\d{2}_.+_v5\.\d+$")
PART_PATTERN = re.compile(r"^\d{3}_.+_v5\.\d+$")
PART_SUBFOLDERS = {
    "01_三维模型",
    "02_原始工程图",
    "03_FreeCAD生成图",
    "04_参数化源码",
    "05_工艺与成本",
    "06_公差与检验",
    "07_验证记录",
}


def main():
    parser = argparse.ArgumentParser(description="Audit the V5 engineering delivery layout.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-parts", type=int)
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    issues = []
    root_folders = sorted(path for path in root.iterdir() if path.is_dir())
    numbered = [path for path in root_folders if ROOT_PATTERN.match(path.name)]
    if len(numbered) != 12:
        issues.append(f"Expected 12 numbered root folders, found {len(numbered)}")

    parts_roots = [path for path in root_folders if path.name.startswith("04_零件模型_")]
    if len(parts_roots) != 1:
        issues.append(f"Expected one parts root, found {len(parts_roots)}")
        parts = []
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

    quick_fcstd = list(root.glob("00_先看说明_*/*原生装配体*.FCStd"))
    quick_step = list(root.glob("00_先看说明_*/*装配_STEP*.step"))
    quick_drawing = list(root.glob("00_先看说明_*/*装配工程图*.pdf"))
    validation_matrix = list(root.glob("00_先看说明_*/*验证总表*.json"))
    quick_preview = list(root.glob("00_先看说明_*/*预览*.png"))
    quick_index = list(root.glob("00_先看说明_*/*索引*.md"))
    native_fcstd = list(root.glob("05_原生装配体_*/01_FreeCAD原生Assembly/*.FCStd"))
    canonical_step = list(root.glob("05_原生装配体_*/02_STEP格式/*.step"))
    design_inputs = list(root.glob("01_设计输入与标准_*/*design*input*.json")) + list(root.glob("01_设计输入与标准_*/*设计输入*.json"))
    standards = list(root.glob("01_设计输入与标准_*/*standard*.json")) + list(root.glob("01_设计输入与标准_*/*标准*.json"))
    motion_json = list(root.glob("06_运动与干涉验证_*/*.json"))
    concept_json = list(root.glob("03_方案与计算_*/*option*.json")) + list(root.glob("03_方案与计算_*/*方案*.json"))
    engineering_checks = list(root.glob("03_方案与计算_*/*check*.json")) + list(root.glob("03_方案与计算_*/*计算*.json"))
    manufacturing_json = list(root.glob("07_工艺公差与装配_*/*manufactur*.json")) + list(root.glob("07_工艺公差与装配_*/*工艺*.json"))
    tolerance_json = list(root.glob("07_工艺公差与装配_*/*tolerance*.json")) + list(root.glob("07_工艺公差与装配_*/*公差*.json"))
    sequence_json = list(root.glob("07_工艺公差与装配_*/*sequence*.json")) + list(root.glob("07_工艺公差与装配_*/*装配顺序*.json"))
    relationship_json = list(root.glob("05_原生装配体_*/03_装配关系与自由度/*.json"))
    drawings_pdf = list(root.glob("08_全部工程图_*/*.pdf"))
    cost_json = list(root.glob("09_BOM成本与供应链_*/*cost*.json")) + list(root.glob("09_BOM成本与供应链_*/*成本*.json"))
    bom_csv = list(root.glob("09_BOM成本与供应链_*/*.csv"))
    supply_json = list(root.glob("09_BOM成本与供应链_*/*supply*.json")) + list(root.glob("09_BOM成本与供应链_*/*供应*.json"))
    manifests = list(root.glob("*_交付清单_v5.*.json"))

    expected_single = {
        "quick native FCStd": quick_fcstd,
        "quick STEP": quick_step,
        "quick assembly drawing": quick_drawing,
        "quick validation matrix": validation_matrix,
        "quick preview": quick_preview,
        "quick index": quick_index,
        "canonical native FCStd": native_fcstd,
        "canonical STEP": canonical_step,
        "delivery manifest": manifests,
    }
    for label, matches in expected_single.items():
        if len(matches) != 1:
            issues.append(f"Expected one {label}, found {len(matches)}")
    if not design_inputs:
        issues.append("Design-input JSON is missing")
    if not standards:
        issues.append("Standards-profile JSON is missing")
    if len(motion_json) < 3:
        issues.append("Motion/interference folder must contain at least three JSON reports")
    if not concept_json:
        issues.append("Concept/option decision JSON is missing")
    if not engineering_checks:
        issues.append("Engineering calculation/check JSON is missing")
    if not manufacturing_json:
        issues.append("Manufacturing plan/audit JSON is missing")
    if not tolerance_json:
        issues.append("Tolerance-stack JSON is missing")
    if not sequence_json:
        issues.append("Assembly-sequence JSON is missing")
    if not relationship_json:
        issues.append("Native assembly relationship/DOF JSON is missing")
    if not drawings_pdf:
        issues.append("Released engineering drawing PDF is missing")
    if not cost_json:
        issues.append("Cost report JSON is missing")
    if not bom_csv:
        issues.append("BOM CSV is missing")
    if not supply_json:
        issues.append("Supply audit JSON is missing")

    report = {
        "root": str(root),
        "numbered_root_folders": len(numbered),
        "part_folders": len(parts),
        "motion_json_count": len(motion_json),
        "issues": issues,
        "pass": not issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["pass"] else 2)


if __name__ == "__main__":
    main()
