# Portable Delivery and File Layout V7

## Contents

1. Versioned root layout
2. Quick-access rules
3. Portable source rules
4. Clean-room rebuild
5. Runtime efficiency
6. Release manifest and privacy

## 1. Versioned root layout

Use the inherited V6 root layout, adding V7 validation artifacts where relevant:

```text
PROJECT_v7.0_rNN/
|-- 00_先看说明_v7.0/
|-- 01_任务配置与输入_v7.0/
|-- 02_原始资料与证据_v7.0/
|-- 03_识图与特征语义_v7.0/
|-- 04_零件模型_v7.0/
|-- 05_原生装配体_v7.0/
|-- 06_二维工程图_原图复现_v7.0/
|-- 07_二维工程图_工程增强_v7.0/
|-- 08_对比与验证_v7.0/
|-- 09_工艺公差与检验_v7.0/
|-- 10_BOM成本与供应链_v7.0/
|-- 11_便携源码与导出_v7.0/
|-- 12_错误经验与版本记录_v7.0/
`-- PROJECT_交付清单_v7.0.json
```

Never overwrite an accepted revision. Use a new revision for geometry, placement, BOM, tolerance, drawing, joint, GUI-display, or packaging changes.

## 2. Quick-access rules

Place only the accepted current artifacts in `00_先看说明`:

- README/limitations;
- accepted FCStd and rebuilt STEP;
- immutable trusted copy when permitted;
- accepted drawing PDF and previews;
- real FreeCAD viewport screenshot;
- final geometry/STEP/GUI/drawing/clean-room reports;
- delivery manifest.

Move approximate, rejected, superseded, or ambiguous files into `12_错误经验与版本记录`. Never leave generic filenames that can be confused with accepted calibrated files.

## 3. Portable source rules

- derive project root from `__file__` or accept `--project-root`;
- accept `--reference-step`, output root, and FreeCAD path explicitly;
- use UTF-8 and `pathlib`;
- avoid shell-built unquoted paths;
- avoid hidden dependency on already-open documents, temp caches, or accepted output files;
- print final paths, counts, bounds, and conflicts;
- provide a launcher for Windows where useful;
- document which scripts require FreeCAD core, FreeCADGui, or external Python packages.

## 4. Clean-room rebuild

Create a new empty directory and include only advertised inputs:

- source drawing or trusted reference;
- BOM/authority configuration;
- portable source and launcher;
- required templates or local workbench package.

Then:

1. rebuild FCStd/STEP/STL;
2. validate occurrence and solid counts;
3. compare geometry and ppm drift;
4. write GUI visibility and camera;
5. reopen and capture a real viewport;
6. regenerate drawings where advertised;
7. rerun manifest and quick-access audit.

The clean-room report must list all available inputs so prior outputs cannot contaminate the result.

## 5. Runtime efficiency

Avoid multi-hour opaque runs:

- inventory once and cache immutable metrics;
- cache expensive projections by view direction and model revision;
- broad-phase filter interference pairs;
- use specialized gear checks instead of all-pairs exact booleans;
- separate model, drawing, rendering, and packaging stages;
- write checkpoints and resumable reports;
- fail early on missing authority, invalid shape, or quantity conflict;
- display progress by stage and artifact, not only elapsed time.

Do not trade away validation integrity for speed. Optimize repeated computation and irrelevant pair checks first.

## 6. Release manifest and privacy

The manifest should contain:

- file role, relative path, size, SHA-256, revision, and authority;
- geometry, STEP, drawing, GUI, viewport, and clean-room gate statuses;
- known blockers and unreleased suggestions;
- software versions and commands;
- repository visibility and upload authorization where applicable.

Use `scripts/build_delivery_manifest_v7.py`.

Never upload proprietary drawings, trusted CAD, quotations, or credentials unless the user explicitly authorizes the upload and the remote repository is verified private.
