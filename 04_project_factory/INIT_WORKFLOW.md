# Project Initialization Workflow

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED (PAOS-018)`

## 状态机

`REQUESTED → SCOPED → PLANNED → GENERATED → VALIDATED → PROVISIONAL → ACTIVE`

失败状态：`BLOCKED`、`FAILED_VALIDATION`、`ROLLED_BACK`。

## 流程

1. Capture 项目意图，不立即创建目录。
2. 检查是否与现有项目重复、从属或冲突。
3. 确认 ID、Slug、Owner、目标、范围和 Non-goals。
4. 选择 Primary Type、Overlays 和 Template Pack 版本。
5. 检查目标不存在、父目录已存在且目标不位于 Personal AI OS 或其他 Git Repository 内。
6. 校验 Template Pack Kind、Approval Reference、文件 Allowlist 与 Factory 外部登记的 Pack Digest。
7. 先生成 Dry Run Manifest，列出所有计划文件、写入路径、安装基线和 Registry Candidate。
8. 用户确认后，Approved Pack 可创建独立 Git Repository 和项目骨架；Working Pack 只能 Dry Run。
9. 运行结构、配置、Secret、引用和 Git 验证；生成期间若目标后来出现，停止落地且不覆盖。
10. 在 `.paos-init.json` 中保留 `PROVISIONAL` Registry Candidate，不直接写入 OS Registry。
11. Project Owner 验收项目 Objective/Scope 后建立首张正式 Task Card，再决定是否进入 `ACTIVE`。

## 回滚

- 初始化使用同级临时 staging；失败时只移除该 staging，不移除目标父目录。
- 对创建前已存在的目录和文件绝不执行删除或覆盖。
- 已产生 Git Commit 时使用新的回滚 Commit，不重写历史。
