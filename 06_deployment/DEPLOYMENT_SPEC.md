# Deployment Specification

> 状态：`WORKING`

## 共同流程

`Preflight → Generate → Diff → Validate → Approve → Deploy → Smoke Test → Record → Rollback Ready`

## 部署边界

- Canonical Source 保存在 Personal AI OS Git Repository。
- 平台原生配置由 Adapter 生成，不反向成为规则源头。
- 部署前必须展示 Diff、目标路径、权限和副作用。
- 用户级配置与项目级配置分开管理。
- Secret 只使用环境变量或系统 Secret Store 引用。
- Hooks 默认关闭，启用必须逐项审批。
- 部署失败必须能够恢复部署前版本。

## 环境状态

- `PLANNED`：仅有部署方案。
- `GENERATED`：Adapter 已生成但未写入目标。
- `VALIDATED`：格式与语义检查通过。
- `DEPLOYED`：已写入目标位置。
- `SMOKE_TESTED`：目标 Agent 已加载并通过最小测试。
- `ROLLED_BACK`：已恢复到部署前状态。

当前状态：Codex、Claude Code 与 Gemini CLI 项目级 Working Adapter 已部署。Codex Runtime Smoke 为 `PASS`；Gemini Config Load 为 `PASS`，Live Runtime 等待外部数据授权；Claude Code 因本机未安装 CLI，Config Load 与 Live Runtime 均保持 `BLOCKED`。
