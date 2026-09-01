# Deployment Specification

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-020`
>
> 日期：`2026-09-01`

## 共同流程

`Preflight → Generate → Diff → Validate → Approve → Deploy → Smoke Test → Record → Rollback Ready`

## 部署边界

- Canonical Source 保存在 Personal AI OS Git Repository。
- 平台原生配置由 Adapter 生成，不反向成为规则源头。
- 生成器与部署器默认只展示 Plan；写入必须分别显式使用 `--write` 或 `--apply`。
- 部署前必须展示 Diff、目标路径、权限和副作用；Apply 必须提供单次授权引用、`PROJECT/USER` Scope 与独立 Record Root。
- 用户级配置与项目级配置分开管理。
- Secret 只使用环境变量或系统 Secret Store 引用。
- Hooks 默认关闭，启用必须逐项审批。
- 只接受受管 `03_adapters/*/manifest.toml`；Source、Target、Backup、Staging 不得越界、经过 symlink 或使用特殊文件。
- 部署记录必须包含 Plan Digest、Source/Previous Hash、权限模式、时间、授权、Scope、Backup 与 Rollback 状态，且不得覆盖。
- Backup、Staging、Replace 或 Record 任一步失败，必须恢复全部目标并清除本次部分 Backup/Staging。

## 环境状态

- `PLANNED`：仅有部署方案。
- `GENERATED`：Adapter 已生成但未写入目标。
- `VALIDATED`：格式与语义检查通过。
- `DEPLOYED`：已写入目标位置。
- `SMOKE_TESTED`：目标 Agent 已加载并通过最小测试。
- `ROLLED_BACK`：已恢复到部署前状态。

当前状态：Codex、Claude Code 与 Antigravity CLI 项目级 Working Adapter 已部署。Codex `0.152.0` 当前 Context/Runtime Evidence 为 `PASS`；Claude Code `2.1.252` 隔离 `doctor` Config Check 为 `PASS`，Live Runtime 未授权；Antigravity IDE / CLI 当前运行环境 Context Load 与 Runtime Smoke 实测为 `PASS`。

`Configured → Deployed → Trusted → Config Loaded → Context Loaded → Runtime Verified → External Data Authorized` 是不同证据层，后层不得由前层推断。
