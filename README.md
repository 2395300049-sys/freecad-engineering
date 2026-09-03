# FreeCAD Engineering Skill

一个面向 Codex 的专业 FreeCAD 机械工程 Skill，用于设计、重建、纠错、装配、工程图、验证、交付与发布。

它将原有 V2、V3、V4、V5 与 V8 的有效能力整合为统一入口 `$freecad-engineering`。主入口只保留任务路由、工程不变量和验收边界，具体方法按任务从参考资料加载，避免一次性占用过多上下文。

## 适用任务

- 二维工程图转 FreeCAD 零件或装配体。
- STEP/STP/IGES/FCStd/SLDPRT/SLDASM 参考模型校准。
- 用户标记区域的局部纠错和回归验证。
- 装配结构、干涉、运动、间隙和装配顺序审计。
- 面向制造的材料、载荷、强度、公差、GD&T、成本与供应审查。
- 零件图、装配图、STEP、FCStd GUI 状态和异机重建验收。
- 可复用 Skill 或工程项目的清理、打包与 GitHub 发布。

## 安装

```bash
git clone https://github.com/2395300049-sys/freecad-engineering.git
cp -R freecad-engineering/freecad-engineering "$HOME/.codex/skills/freecad-engineering"
```

重新打开 Codex 任务后，可直接说：

```text
使用 $freecad-engineering 根据这些二维工程图重建零件和装配体，并分别验证 STEP、FCStd GUI 状态和工程图。
```

## 运行环境

- Codex Skills 目录可读。
- 普通审计脚本使用 Python 3。
- 涉及真实 FCStd、STEP、B-Rep、视口或装配几何的脚本，需要 FreeCAD 及其 Python 模块；可以通过 `FreeCADCmd`、`freecadcmd` 或 FreeCAD GUI 运行。
- PowerShell 启动器主要用于 Windows；macOS/Linux 可直接调用相应 Python 脚本。

## 仓库结构

```text
freecad-engineering/
├── README.md
└── freecad-engineering/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── scripts/
    ├── references/
    └── assets/templates/
```

专业 Skill 包位于仓库中的 `freecad-engineering/` 文件夹，可以直接复制到个人 Skills 目录。

## 工程边界

脚本成功、模型可打开或 STEP 可导出，都不单独构成工程合格或可投产证明。Skill 分别报告 `geometry_review_ready`、`engineering_review_ready` 和 `production_release_ready`，并保留人工工程审批、实物测试、供应商确认及法规审查边界。

本仓库未附加开源许可证。仓库可见性不等同于授予复制、修改或再分发许可。
