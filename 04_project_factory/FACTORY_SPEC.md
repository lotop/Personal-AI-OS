# Project Factory Specification

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 用途与层级

- 用途：以一致、可追溯、可回滚的方式创建独立项目。
- 层级：Personal AI OS Control Plane。
- 维护者：总控任务；实现可由 Factory Owner 提交，总控评审。
- Source of Truth：本规范批准后可成为 Factory 规则来源；生成出的业务项目自行拥有其项目文件。

## 输入

- `project_id`、名称、Slug 和 Owner。
- 项目边界、目标和 Non-goals。
- 一个 Primary Type。
- 零个或多个 Capability Overlay。
- 已批准的 Template Pack 版本。
- 目标路径和 Git 初始化策略。

## 项目类型候选

- `BUSINESS_VENTURE`
- `SOFTWARE_PRODUCT`
- `RESEARCH_DECISION`
- `OPERATIONS_PROGRAM`
- `CONTENT_BRAND`

复杂项目仍选择一个主要类型，再叠加 `software`、`data`、`ai`、`security`、`compliance`、`content`、`finance` 或 `vendor` Overlay。

## 输出

- 独立项目目录和 Git Repository。
- 项目级 `AGENTS.md`、`PROJECT.md`、`project.toml` 和 Decisions 入口。
- Working、Source、Knowledge、Archive 与 Temp 边界。
- Project Registry Candidate Record。
- 首张 Task Card。
- 初始化验证报告和回滚说明。

## 不变量

- 不把业务项目创建在 Personal AI OS 仓库内部。
- 不覆盖已存在的非空目录。
- 不把未批准模板用于正式创建。
- 不写入真实 Secret。
- 不自动批准项目或执行 Canonical Promotion。
- 模板实例化后，业务项目拥有生成文件；OS 只提供升级建议和 Migration。

## 模板关系

`01_templates/` 保存批准后的模板；`07_working/candidates/` 保存待审模板；Factory 只能正式读取前者。Candidate 演练必须显式使用 Dry Run，并标记 `PROVISIONAL`。
