# Decisions

> 状态：`WORKING`
>
> 已批准基线：`v1.1.0`（`PAOS-REL-001`）
>
> 当前修订：`v1.1.1` Working Candidate

正式 Decision Record 模板尚未确认。本索引先记录已经由 Founder 明确确认的决策事实。

## Approved Decisions

### PAOS-001｜V1.1 直接建设

- 状态：`APPROVED`
- 决定：当前仓库直接建设 Personal AI OS V1.1；V1.0 仅作历史基线，不维持并行运行目录。

### PAOS-002｜Canonical 文档语言

- 状态：`APPROVED`
- 决定：Canonical Markdown 默认中文；路径、配置键、状态码和必要技术术语保留英文。

### PAOS-003｜结构化配置格式

- 状态：`APPROVED`
- 决定：人工维护的 Canonical Config 与 Registry 默认使用 TOML；JSON/JSONL 用于机器数据；YAML 仅在外部工具要求时使用。

### PAOS-004｜多任务协作模型

- 状态：`APPROVED`
- 决定：采用一个 Project、一个总控任务、多个专业任务、任务内部临时 Subagents；并行写入实现阶段使用 Git Worktree，Canonical Promotion 由总控统一处理。

### PAOS-005｜定向扁平化

- 状态：`APPROVED`
- 决定：`02_registry/` 与说明型 `05_harness/` 使用一级文件结构；具有稳定语义、多文件或独立生命周期的目录继续保留。

### PAOS-006｜Project Factory 位置

- 状态：`APPROVED`
- 决定：Project Factory 使用顶层 `04_project_factory/`，负责新项目创建、初始化和验收。

### PAOS-007｜V1.1 Minimum 简化

- 状态：`APPROVED`
- 决定：V1.1 以个人控制平面的最低可运行闭环为目标，保留安全、Git、项目隔离、Template、Factory、验证、部署与恢复核心；简化 Mode、资产状态、任务进度、Release Gate 与 Session Close/Handoff。
- 实施边界：本决定授权形成 `WORKING` 实现，不构成 Template Approval、Release Approval、Canonical Promotion、Tag、Push 或部署授权。
- 具体约束：
  - Mode 只保留 `CHAT / WORK / REVIEW` 三种行为边界；研究、策略、产品和编码作为任务标签或 Skill。
  - 资产最小状态为 `WORKING / APPROVED / ARCHIVED`；Canonical Authority 由批准记录、固定 Commit 与 Release Tag 共同证明，不要求每个文件维护四维状态。
  - 任务只保留一个主状态与验证证据，不再维护四个并行进度字段。
  - Release Readiness 收敛为六个 Gate；Promotion 是批准后的动作，不是发布前 Gate。
  - Session Close 与 Handoff 仅在交接、跨环境、长暂停、Blocked 或形成长期结论时要求。
  - 旧模型保留为历史证据并标记 `SUPERSEDED`，不再作为当前运行入口。

### PAOS-TMPL-001｜首个核心 Template Pack 批准

- 状态：`APPROVED`
- 决定：批准 `01_templates/project-base-pack`（版本 `1.0.0`）作为 Personal AI OS V1.1 的官方首个已批准模板包。
- 依据：通过 `04_project_factory/create_project.py` 正式 E2E 实例化验收，生成物完整性与 SHA-256 均符合 Schema 定义。

### PAOS-TMPL-002｜Claude Code Template Pack 纳入批准

- 状态：`APPROVED`
- 决定：批准 `01_templates/project-base-pack` 升级至版本 `1.1.0`，纳入薄层 `CLAUDE.md` Adapter 与项目级 `.claude/settings.json`；`AGENTS.md` 继续作为统一项目规则入口。
- 边界：不得将 Claude Auto Memory、Conversation、`.claude/rules/`、Hooks、Skills、Subagents 或 MCP 配置自动升级为 Canonical；外部数据发送仍需独立授权。
- 依据：Founder 已明确确认 Claude Code 纳入 V1.1.1，并授权执行；正式 Factory E2E 与 Claude Code 隔离 Config Load 均须通过。

### PAOS-REL-001｜Personal AI OS V1.1 正式发布批准

- 状态：`APPROVED`
- 决定：批准 Personal AI OS V1.1 作为首个可运行、可验证、支持多 Agent（Codex & Gemini）协同的 Canonical Control Plane 基线正式发布。
- 适用范围：
  - 确立 V1.1 为首个完整基线；
  - Gemini 在 V1.1 维持 CONDITIONAL（配置加载支持，不阻塞发布）；
  - 核心基础设施聚焦于本地 Git Canonical Repository 与离线恢复 Bundle 闭环。

### PAOS-008｜V1.1.1 一致性与证据加固实施

- 状态：`APPROVED`
- 决定：在独立分支实施 V1.1.1 状态一致性、Registry/Skill 收口、Release Audit 加固、当前 Commit 恢复演练和新版 Handoff。
- 实施边界：本决定授权形成并提交 V1.1.1 Release Candidate；不构成 V1.1.1 Release Approval、Tag、Push、Merge 或 Canonical Promotion 授权。
- 验收边界：M5 必须校验机器可读恢复证据与 Commit/Bundle/Tree Digest；M6 必须校验 Founder Approval、annotated Tag 与当前 HEAD 的精确绑定。

## Candidate Decisions

- `PAOS-REL-002`｜V1.1.1 正式发布批准（待 Founder 在最终验证后决定）。
- 根 `AGENTS.md` 采用精简 Router，而不是完整 Policy Core。
- Phase 1 Hooks 可以拒绝固定禁令，但不得代替用户批准操作。
- `06_deployment/` 作为 Agent 部署、备份与恢复层。
