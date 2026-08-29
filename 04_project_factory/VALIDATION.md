# Project Factory Validation

> 状态：`WORKING`

新项目进入 `PROVISIONAL` 前必须验证：

- `project_id` 和 Slug 在 Registry 中唯一。
- 目标路径独立且不在 Personal AI OS 仓库内部。
- 根级入口文件存在并可读取。
- `project.toml` 可解析且 Schema 版本存在。
- 所有生成文件能追溯到 Template Pack 版本。
- Source、Working、Generated、Archive、Temp 边界明确。
- 没有真实 Secret、绝对用户路径或悬空引用。
- Git Repository 可初始化，默认分支符合策略。
- 初始化报告包含创建清单、验证结果和回滚步骤。

当前没有批准的 Template Pack，因此正式创建 Gate 为 `BLOCKED_TEMPLATE_APPROVAL`。
