# Project Factory Provisional Acceptance

> 状态：`WORKING`
>
> 结论：`PASS_PROVISIONAL_ONLY`
>
> 日期：`2026-08-30`

## 范围

本验收只证明 Candidate Template Pack 可被 Project Factory 以 `--provisional` 安全实例化，不构成 Template Approval、正式项目验收或 Canonical Promotion。

## 被测对象

- Factory：`04_project_factory/create_project.py`
- Candidate Pack：`07_working/candidates/project-base-pack/template.toml`
- Pack Version：`0.1.0-candidate`
- Project Type：`SOFTWARE_PRODUCT`
- Overlay：`ai`

## 验收结果

- Dry Run 不创建目标目录：`PASS`
- 显式 `--provisional --apply --git` 创建成功：`PASS`
- Git 默认分支为 `main`：`PASS`
- 生成 7 个根级项目文档/配置：`PASS`
- 创建 5 个稳定生命周期目录：`PASS`
- `.paos-init.json` 记录 Pack、版本、状态和逐文件 SHA-256：`PASS`
- 生成内容无残留 `{{PLACEHOLDER}}`：`PASS`
- Candidate 实例状态为 `PROVISIONAL`：`PASS`
- 未写入 Active Project Registry、未 Push、未 Tag、未 Promotion：`PASS`

## 自动化覆盖

`04_project_factory/test_factory.py` 包含 Candidate Pack 的 Dry Run 与 Apply E2E，并同时覆盖路径越界、非空目标拒绝、缺失变量和 Git 初始化。

## 正式验收边界

正式 E2E 仍为 `BLOCKED_TEMPLATE_APPROVAL`。只有 Founder 针对固定 Commit/SHA 批准 Template Pack 后，才能复制到 `01_templates/`、以非 provisional 模式生成项目并形成 `PROJECT_FACTORY_ACCEPTANCE.md`。
