# Project Initialization Workflow

> 状态：`WORKING`

## 状态机

`REQUESTED → SCOPED → PLANNED → GENERATED → VALIDATED → PROVISIONAL → ACTIVE`

失败状态：`BLOCKED`、`FAILED_VALIDATION`、`ROLLED_BACK`。

## 流程

1. Capture 项目意图，不立即创建目录。
2. 检查是否与现有项目重复、从属或冲突。
3. 确认 ID、Slug、Owner、目标、范围和 Non-goals。
4. 选择 Primary Type、Overlays 和 Template Pack 版本。
5. 检查目标路径为空且不位于 Personal AI OS 仓库内部。
6. 先生成 Dry Run Manifest，列出所有计划文件和写入路径。
7. 用户确认后创建独立 Git Repository 和项目骨架。
8. 运行结构、配置、Secret、引用和 Git 验证。
9. 生成 Registry Candidate，不直接写成 `ACTIVE`。
10. 建立首张 Task Card，经批准后进入 `ACTIVE`。

## 回滚

- 初始化失败时只移除本次创建且有 Manifest 记录的文件。
- 对创建前已存在的目录和文件绝不执行删除或覆盖。
- 已产生 Git Commit 时使用新的回滚 Commit，不重写历史。
