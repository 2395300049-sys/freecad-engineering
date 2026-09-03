# V5 Engineering Delivery Layout

## Required root structure

```text
PROJECT_NAME_v5.0/
|-- 00_先看说明_v5.0/
|-- 01_设计输入与标准_v5.0/
|-- 02_原始资料与参考_v5.0/
|-- 03_方案与计算_v5.0/
|-- 04_零件模型_v5.0/
|-- 05_原生装配体_v5.0/
|-- 06_运动与干涉验证_v5.0/
|-- 07_工艺公差与装配_v5.0/
|-- 08_全部工程图_v5.0/
|-- 09_BOM成本与供应链_v5.0/
|-- 10_验证与错误总结_v5.0/
|-- 11_便携源码_v5.0/
`-- PROJECT_交付清单_v5.0.json
```

Keep working files, rejected iterations, caches, temporary screenshots, and supplier credentials outside this root.

## Quick access

Place only current accepted artifacts in `00_先看说明_VERSION`:

1. `00_完整原生装配体_VERSION.FCStd`
2. `01_完整装配_STEP_VERSION.step`
3. `02_装配工程图_VERSION.pdf`
4. `03_设计验证总表_VERSION.json`
5. `04_装配与运动预览_VERSION.png`
6. `05_文件索引与限制说明_VERSION.md`

## Part folder contract

Name each part folder `NNN_PART-NUMBER_PART-NAME_VERSION` with exactly:

```text
01_三维模型/
02_原始工程图/
03_FreeCAD生成图/
04_参数化源码/
05_工艺与成本/
06_公差与检验/
07_验证记录/
```

## Native assembly folder

```text
05_原生装配体_VERSION/
|-- 01_FreeCAD原生Assembly/
|-- 02_STEP格式/
|-- 03_装配关系与自由度/
|-- 04_装配顺序与维修/
|-- 05_装配工程图/
`-- 06_预览与动画/
```

## Motion/interference folder

Include static full audit, focused audits, approved-pair rules, gear-pair records, motion samples, minimum-clearance report, before/after evidence, and limitations.

## Manufacturing/tolerance folder

Include process routes, setup/tooling notes, tolerance stacks, fit plan, datum plan, inspection plan, and assembly sequence.

## Cost/supply folder

Include dated cost basis, BOM, quotations or authorized source locators, lead-time audit, lifecycle risk, alternatives, and accepted deviations. Do not package supplier credentials.

## Revision policy

- Never overwrite an accepted version.
- Geometry, joint, tolerance, process, safety, BOM, or sourcing changes increment the revision.
- Keep a machine-readable manifest with hashes and acceptance status.
- Archive superseded releases outside the active delivery root.
