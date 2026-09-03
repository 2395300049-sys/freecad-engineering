# V6 Delivery Layout

## Root structure

```text
PROJECT_NAME_v6.0/
|-- 00_先看说明_v6.0/
|-- 01_任务配置与输入_v6.0/
|-- 02_原始资料与证据_v6.0/
|-- 03_识图与特征语义_v6.0/
|-- 04_零件模型_v6.0/
|-- 05_原生装配体_v6.0/
|-- 06_二维工程图_原图复现_v6.0/
|-- 07_二维工程图_工程增强_v6.0/
|-- 08_对比与验证_v6.0/
|-- 09_工艺公差与检验_v6.0/
|-- 10_BOM成本与供应链_v6.0/
|-- 11_便携源码与导出_v6.0/
|-- 12_错误经验与版本记录_v6.0/
`-- PROJECT_交付清单_v6.0.json
```

Create only the drawing-release folder required by the selected intent, or create both when requested. Do not place rejected iterations in the accepted release folders.

## Part folder

Name each part `NNN_PART-NUMBER_PART-NAME_v6.X` with:

```text
01_输入与证据/
02_参数化三维模型/
03_原图复现工程图/
04_工程增强工程图/
05_源码与格式导出/
06_公差工艺与检验/
07_验证与迭代记录/
```

## Quick-access folder

Place only accepted current artifacts in `00_先看说明_v6.X`:

- file index and limitations;
- accepted FCStd and STEP;
- accepted assembly drawing;
- drawing-profile summary;
- validation matrix;
- preview image.

## Revision policy

- Never overwrite an accepted release.
- Increment revision for geometry, datum, tolerance, joint, BOM, process, or standards changes.
- Keep source-faithful and engineering-enhanced revision histories separate.
- Store a machine-readable manifest with hashes, origin, status, and acceptance evidence.
