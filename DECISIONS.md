# Decisions

> 状态：`APPROVED`
>
> 已批准基线：`v1.1.4`（`PAOS-REL-005`）
>
> 当前发布：`v1.1.4`，由本地 annotated tag 与 Release Evidence 绑定

本索引记录已经由 Founder 明确确认的决策事实。Decision Record 正式结构模板由 `PAOS-TMPL-003` 批准。

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

### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准

- 状态：`APPROVED`
- 决定：批准 Personal AI OS V1.1.1 作为当前 Canonical Control Plane 基线，纳入 Codex、Claude Code 与 Gemini Adapter、Project Factory Template Pack `1.1.0`、加固后的 M1–M6 Release Audit 与可校验恢复证据。
- 授权范围：合并到本地 `main`，创建本地 annotated tag `v1.1.1`，并执行 Canonical Promotion；本次不授权 Push、远端发布或外部部署。
- 运行时边界：Codex Runtime Smoke 为 PASS；Claude Code Config Load 为 PASS 但 Live Runtime 未授权；Gemini Config Load 为 CONDITIONAL PASS 且 Live Runtime 未授权。不得扩大解读。
- 绑定规则：发布实现冻结 Commit 为 `e95cf5aee29bcc018454dcac08d5e04301ab482d`；正式 Release Commit 由 annotated tag `v1.1.1` 精确绑定。

### PAOS-009｜Direct Main 小修订例外

- 状态：`APPROVED`
- 决定：当 Founder 明确授权，且任务属于明显事实纠错、低风险、小范围、可回滚修订时，可以直接修改本地 `main`，无需为形式完整性单独建立分支。
- 边界：Task Card 必须记录例外理由并完成验证；复杂功能、架构迁移、并发写入和高风险自动化仍使用独立 branch/worktree；本规则不自动授权 Tag、Push、Release Approval、Promotion 或外部部署。

### PAOS-010｜精简 Root Router

- 状态：`APPROVED`
- 决定：根 `AGENTS.md` 采用精简 Router，完整 Policy 保持在 `00_system/`，避免重复与规则漂移。

### PAOS-011｜Phase 1 Hooks 固定禁令

- 状态：`APPROVED`
- 决定：Phase 1 Hooks 可检查并拒绝已批准的固定禁令，但不得代替 Founder 批准或执行自动 Promotion、commit、merge、push、deploy、publish、delete。

### PAOS-012｜Deployment 层级

- 状态：`APPROVED`
- 决定：`06_deployment/` 作为 Agent Adapter 部署、备份与恢复规范层；Generated Adapter 不反向成为 Canonical Source。

### PAOS-TMPL-003｜V1.1.2 Core Template Pack 批准

- 状态：`APPROVED`
- 日期：`2026-08-31`
- Owner：`paos-14-v1-1-2-formal-release`
- Context：Founder 明确要求不再逐项等待模板确认，直接交付完整 V1.1.2 正式版，并要求说明由 AI 代为做出的决定。
- Decision：批准 `01_templates/core-template-pack`（版本 `1.1.2`）作为 Personal AI OS 的正式核心模板包。
- Scope：Decision、Profile、Preferences、Communication、Mode、Memory、Knowledge Extraction、Task Card、Session Close、Handoff、Skill Registry、GC Plan 与 Project AGENTS 模板。
- Constraints：本批准不授权 Push、外部部署、真实项目数据传输或破坏性删除；Dashboard 继续按 Founder 指令排除。
- Evidence：模板包 Manifest 完整，候选模板已归档，仓库验证与 CI Gate 必须通过。
- Consequences：`07_working/candidates/` 不再承载当前待确认模板；后续项目和任务可直接引用 Approved Core Template Pack。
- Alternatives：继续逐项确认模板；因 Founder 明确要求交付完整成品，本轮不采用。
- Supersedes：`07_working/candidates/CORE_TEMPLATE_CANDIDATES.md`
- Approval：Founder / 2026-08-31 / 批准模板批量完成并通过校验后进入 Approved。

### PAOS-REL-003｜Personal AI OS V1.1.2 正式发布批准

- 状态：`APPROVED`
- 日期：`2026-08-31`
- Owner：`paos-14-v1-1-2-formal-release`
- Context：Founder 明确要求交付 V1.1.2 正式版，不再保留未完成模板、待确认项或未授权的 Release Blocker。
- Decision：批准 Personal AI OS V1.1.2 作为当前 Canonical Control Plane 本地正式发布版本。
- Scope：V1.1.2 状态纠错、Direct Main 小修订规则、Registry Schema 绑定、Temp Cleanup 机制、Gemini Session Manager 非 Dashboard 治理修正、Approved Core Template Pack `1.1.2`、恢复证据与 M1-M6 Release Audit。
- Authorization：允许在本地 `main` 创建正式 release commit，并创建本地 annotated tag `v1.1.2`；不授权 Push、远端发布、外部部署、真实项目数据传输或 Dashboard 验收。
- Runtime Boundary：Codex Runtime Smoke 为 PASS；Claude Code Config Load 为 PASS 但 Live Runtime 未授权；Gemini Config Load 为 CONDITIONAL PASS 且 Live Runtime 未授权。不得扩大解读。
- Evidence：实现冻结 Commit `b76a8d2f0ba48b4b39afd9ebb9cab4d13172156a`；最终 Release Commit 由 annotated tag `v1.1.2` 精确绑定；`ci_gate.py --profile release-readiness` 必须 PASS。
- AI-made Decisions：批量批准 13 类核心模板；将旧候选模板归档而非保留为待确认；维持 Dashboard 排除；维持 Push 与外部部署不授权。
- Approval：Founder / 2026-08-31 / 批准 V1.1.2 本地正式发布、Release Approval 与本地 annotated tag。

### PAOS-013｜远端同步授权（GitHub origin）

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：`paos-15-post-v1-1-2-remediation`
- Context：`PAOS-REL-003` 明确不授权 Push；Founder 在本轮任务中明确要求提交本次整改并推送到 GitHub，构成对该边界的单次显式解除。
- Decision：授权将本地 `main` 推送到既有远端 `origin`（`https://github.com/lotop/Personal-AI-OS.git`）。
- Scope：仅推送 `main` 分支的提交历史。
- 明确不包含：
  - 不推送 annotated tag（`v1.1.0`、`v1.1.1`、`v1.1.2` 保持本地绑定）；
  - 不构成远端发布、Release Approval、外部部署或真实项目数据传输授权；
  - 不改变 `SYSTEM.toml` 的 `release = "APPROVED_LOCAL_NO_PUSH"`——V1.1.2 的发布证据仍由本地 tag 绑定。
- External Data 记录（依 `EXTERNAL_DATA_POLICY.md` 最小字段）：
  - Provider / Destination：GitHub / `origin`（既有远端，此前已建立跟踪分支）。
  - Data Class：本仓库 Canonical Control Plane 内容，含个人路径与 Owner 标识；仓库验证器确认无 Secret 模式命中。
  - Purpose：远端备份与跨设备恢复路径。
  - Owner / Approver：Founder。
  - Authorized At：`2026-09-01`；One-shot。
  - Revocation：由 Founder 在 GitHub 侧撤除或删除远端内容。
- Consequences：远端仓库的可见性（Public / Private）由 Founder 在 GitHub 侧控制，本仓库不做假设，也不代为修改。

### PAOS-014｜Release Tag 远端发布授权

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：`paos-15-post-v1-1-2-remediation`
- Context：`PAOS-013` 授权推送 `main` 时明确排除了 annotated tag。Founder 在同一轮任务中随后明确要求推送 tag，构成对该排除条款的显式解除。
- Decision：授权将本地 annotated tag `v1.1.0`、`v1.1.1`、`v1.1.2` 推送到既有远端 `origin`。
- Supersedes：`PAOS-013` 中"不推送 annotated tag"一条；`PAOS-013` 的其余条款继续有效。
- Scope 与边界：
  - 三个 tag 指向的 Commit 均已存在于 `origin/main` 历史中，推送只新增 tag 对象，不引入新提交。
  - Tag 对象本身不得重写或移动。`v1.1.1`、`v1.1.2` 的注释含 `PAOS-REL-002`／`PAOS-REL-003`，是 M6 的绑定证据；注释中的 "local release" 字样描述的是**批准当时的范围**，由本决定记录其后续远端发布，不通过改写 tag 来"更新"。
  - 本授权不构成外部部署、真实项目数据传输或新版本 Release Approval。
- Consequences：V1.1.2 的发布证据自此可在远端独立校验；`SYSTEM.toml` 的 `implementation.release` 相应由 `APPROVED_LOCAL_NO_PUSH` 更正为 `APPROVED_REMOTE_TAG_PUSHED`。
- 远端可见性：由 Founder 在 GitHub 侧控制，本仓库不做假设，也不代为修改。

### PAOS-REL-004｜Personal AI OS V1.1.3 本地正式发布批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：`paos-17-v1-1-3-local-release`
- Context：PAOS-016 完成 Post-V1.1.2 全仓整改后，发现两个 Approved Template Manifest 被原地加入 Factory 分类字段；同时 M6 的 `release_commit` 字段要求 Commit 在自身 Tree 中声明自身 Hash，无法作为可持续发布协议。Founder 明确指令“修复后直接发布”。
- Decision：批准 Personal AI OS V1.1.3 作为当前 Canonical Control Plane 本地正式发布版本。
- Scope：Approved Manifest 恢复、Factory Pack 路由迁移、GC/Factory/Schema/Hooks/Deployment 加固、M5 Bundle Artifact 实体验证、M6 annotated tag 直接绑定及相关文档与 Registry 同步。
- Authorization：允许直接在本地 `main` 完成 Release Commit，并创建本地 annotated tag `v1.1.3`；不授权 Push、远端 Tag 发布、外部部署、真实项目数据传输或 Dashboard 验收。
- Runtime Boundary：Codex Runtime Smoke 保持 PASS；Claude Code Config Load 为 PASS 但 Live Runtime 未授权；Gemini Config Load 为 CONDITIONAL PASS 且 Live Runtime 未授权。
- Evidence：实现冻结 Commit `67486a16630c466a6f46710116eadfbcd0c5fff5`；冻结 Tree SHA-256 `75268a184d145f70886cf81b3d9972b5afbac0f68414dd14ad7d905cbff357d7`；最终 Release Commit 由 annotated tag `v1.1.3` 精确绑定；M1–M6 必须全部 PASS。
- Template Integrity：`project-base-pack` Manifest SHA-256 `9854c574add72b7904d6cb1405b7031da5b12a2ac77b85eaa4c54e0f9279a941`；`core-template-pack` Manifest SHA-256 `46a870b0a4ce6b7d52560c24bbdb9422f93b814055ec8a89792ea4322a7a40d7`，均与 `v1.1.2` 批准基线一致。
- AI-made Decisions：Pack Kind 属于 Factory 路由而非 Approved Template Manifest；Release Commit 只由 Git annotated tag 绑定；本地 Bundle Artifact 被 Git 忽略但必须由 M5 读取并验证。
- Approval：Founder / 2026-09-01 / 明确授权修复后直接发布 V1.1.3，本地 Tag，不 Push。

### PAOS-015｜V1.1.4 一致性修订与 V1.2.0 Stable 路线

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder
- 决定：先完成不建分支的 V1.1.4 小范围一致性修订，再以 V1.2.0 作为“可创建项目、无未决 Canonical Working、可构建纯净发行包”的 Stable 目标。
- Approval Mechanism：当前 Working 资产按六个不重叠的 Module Approval Pack 审核确认，不要求对 64 个文件逐一进行独立对话；每个 Pack 仍必须提供用途、层级、维护者、Source-of-Truth 属性、文件清单、风险与 Diff。
- Boundary：本决定批准路线与审核机制，不等同于批准任一 Pack 内容、Canonical Promotion、V1.1.4/V1.2.0 Release Approval、Tag、Push 或外部发布。
- Evidence：Founder 指令“启动1，2”。

### PAOS-REL-005｜Personal AI OS V1.1.4 本地正式发布批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：`paos-18-v1-1-4-consistency`
- Decision：批准 Personal AI OS V1.1.4 作为状态一致性 Patch Release。
- Scope：修正 Decision Index、Physical Architecture 与 PAOS-015 Task 状态漂移；纳入 V1.2 Approval Pack 审核入口，但不执行任何 V1.2 Pack Promotion。
- Authorization：允许在本地 `main` 完成 Release Commit、刷新恢复证据并创建 annotated tag `v1.1.4`；不授权 Push、外部部署、Dashboard、真实项目数据传输或 V1.2 Canonical Promotion。
- Evidence：实现冻结 Commit `4405931d54d40f9567017be0c3bc3891b7c2f838`；最终 Release Commit 由 annotated tag `v1.1.4` 精确绑定；M1–M6 必须全部 PASS。
- Founder Approval：用户明确批准“本地发布 v1.1.4，不 Push”。

### PAOS-016｜V1.2 Governance + Security Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 Governance、Security、Lifecycle 共 16 个文件组成 V1.2 Approval Pack 01，并按审计建议完成四项修正和状态 Promotion。
- Evidence Model：批准证据可以绑定文件 SHA-256，也可以绑定固定 Git Commit 与不可变 Git Tree/Manifest Digest；最终 V1.2 Canonical Authority 仍必须由 Release Evidence 激活。
- Scope：仅限 `V1.2_APPROVAL_PACK_01_GOVERNANCE_SECURITY.md` 明列的 16 个文件。
- Boundary：不启用 Hooks、外部数据传输、Push、Deploy、破坏性 GC；不批准其他五个 Pack，也不构成 V1.2.0 Release Approval。
- Integration：本 Pack 在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；合并及 V1.2 Release 仍由总控任务单独执行。
- Founder Approval：用户明确批准“Pack 01 按审计建议修正并 Promotion”。

## Candidate Decisions

- 当前无待确认 Candidate Decision。
