# Decisions

> 状态：`APPROVED`
>
> 已批准基线：`v1.2.2`（`PAOS-REL-008`）
>
> 当前发布：`v1.2.2`，由本地 annotated tag 与 Release Evidence 绑定

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
- Supersedes：`09_archive/v1.1.2-template-candidates/CORE_TEMPLATE_CANDIDATES.md`（批准时位于 `07_working/candidates/`，已随本决定归档）
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

### PAOS-017｜V1.2 Mode + Memory + Session Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 Identity、Mode、Memory、Conversation、Multi-Agent Sync 共 8 个文件组成 V1.2 Approval Pack 02，并按审计建议完成四组修正和状态 Promotion。
- Memory Boundary：Memory 中的 Decision 只能引用或摘要已批准 Decision Record，不能替代 `DECISIONS.md` 或从 Conversation 自动产生正式决定。
- Concurrency Boundary：保留 `PAOS-009` Direct Main 小修订例外；普通或复杂写入仍使用 Branch/Worktree，不扩大并发写入权限。
- Scope：仅限 `V1.2_APPROVAL_PACK_02_MODE_MEMORY_SESSION.md` 明列的 8 个文件。
- Boundary：不批准任何个人 Memory/Identity 正文、跨项目读取、自动 Memory/Decision/Task Promotion；不构成 Merge、V1.2 Release、Tag、Push 或外部数据授权。
- Integration：在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；默认 Canonical 生效等待最终合并与 V1.2 Release Evidence。
- Founder Approval：用户明确批准“Pack 02 按审计建议修正并 Promotion”。

### PAOS-018｜V1.2 Factory + Templates Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 Approved Templates 与 Project Factory 组成 V1.2 Approval Pack 03；Approved Template Pack 保持字节不变，Factory 按六组审计建议修正并 Promotion。
- Integrity Boundary：Approved Pack 的用途和内容 Digest 由 `04_project_factory/factory.toml` 外部登记；Factory 在 Dry Run/Apply 前按排序后的相对路径与逐文件 SHA-256 校验，不改写 Approved Template Manifest。
- Installation Baseline：`.paos-init.json` V0.2 记录 PAOS/Factory/Template 版本、Approval Reference、Pack Digest、生成器、逐文件 SHA-256 和 Registry Candidate，作为未来 Upgrade/Migration 基线；不自动上传或回写 AI OS。
- Creation Boundary：Working Pack 永远只能 Dry Run；Approved Pack 生成的项目在 Owner 验收前统一为 `PROVISIONAL`；Factory 不自动写 OS Registry，也不预填首张正式 Task Card。
- Filesystem Boundary：目标父目录必须预先存在；最终 staging 替换前再次确认目标不存在，不隐式创建多级父目录或覆盖后来出现的目标。
- Scope：仅限 `V1.2_APPROVAL_PACK_03_FACTORY_TEMPLATES.md` 明列的 Approved Templates 和 7 个 Factory 文件；Template 内容零漂移。
- Boundary：不创建真实业务项目，不实现 Upgrade Engine、自动反馈上传或差异化 Overlay；不构成 Merge、V1.2 Release、Tag、Push 或外部部署授权。
- Integration：在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；默认 Canonical 生效等待最终合并与 V1.2 Release Evidence。
- Founder Approval：用户明确批准“Pack 03 按审计建议修正并 Promotion”。

### PAOS-019｜V1.2 Harness + Hooks Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 20 个 Harness Rule/Config/Schema 文件与 10 个实现/测试文件组成 V1.2 Approval Pack 04，并按审计记录的七组修正完成实施与 Promotion。
- Release Gate Boundary：`release_gates.toml` 成为 M1–M6 顺序、ID 与名称的真实配置源；M2 执行无递归基础检查，M3 对 Approved Project Pack 执行真实 `--apply --git` E2E，不依赖历史 Working Review。
- Evidence Boundary：Tree Digest V0.2 纳入 Git path、mode、object kind 与 blob SHA-256；V1.1.4 V0.1 Recovery Evidence 保持历史原文，V1.2 必须重新生成 V0.2 Evidence。
- GC Boundary：Apply 必须校验受管 Plan 路径、固定 Plan ID、Retention、真实引用扫描、嵌套文件类型与 Founder 单次授权引用；仍只允许可恢复 Quarantine，不永久删除。
- Hook Boundary：只批准 Hook Implementation Boundary；当前实现数与启用数均为 0，`02_registry/hooks.toml` 保持 `WORKING`/Disabled，不生成配置、不执行 Trust、不启用 Hook。
- Scope：仅限 `V1.2_APPROVAL_PACK_04_HARNESS_HOOKS.md` 明列的 Pack 文件及其审计、Decision、Task/Evidence 记录。
- Boundary：不修改 Adapter、不刷新 Recovery Evidence、不构成 Merge、V1.2 Release、Tag、Push、Hook Enable、外部部署或数据授权。
- Integration：在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；默认 Canonical 生效等待最终合并与 V1.2 Release Evidence。
- Founder Approval：用户明确回复“批准”。

### PAOS-020｜V1.2 Deployment + Recovery Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 26 个 Compatibility/Runtime/Adapter/Deployment 文件组成 V1.2 Approval Pack 05，并按审计记录的七组修正完成实施与分层 Promotion。
- Contract Boundary：`00_system/compatibility/README.md`、`adapter_profiles.toml`、`03_adapters/README.md` 与 `06_deployment/` 规则升级为 Approved Contract；Platforms/Capabilities/Runtime Registry 保持时间敏感 `WORKING` Evidence；Generated Adapter 与项目部署目标保持 `GENERATED/WORKING`。
- Generation Boundary：Adapter Generator 默认只输出 Plan，写入必须显式 `--write`；Profile 未知字段、目标漂移、symlink、特殊文件、未声明输出和部分失败全部 Fail Closed/回滚。
- Deployment Boundary：只接受受管 Manifest；Apply 强制单次授权、Target Scope、不可变记录、覆盖备份和全事务回滚。本次只部署仓库项目级 Codex/Claude/Gemini 目标，不授权用户级配置。
- Runtime Boundary：Codex `0.152.0` 当前 Context/Runtime Evidence 为 PASS；Claude Code `2.1.252` 仅完成隔离 `doctor` Config Check，Live Runtime 未授权；Gemini CLI 当前未安装，历史 Config Load 不冒充当前验证。
- Recovery Boundary：V1.2 Recovery Evidence 必须使用 Tree Digest V0.2 并等待全部 Pack/最终实现冻结；Recovery Package 与 Clean Distribution Package 分离，Private Remote、全新设备、大型资产与 Secret 重绑定在真实演练前保持 `NOT_TESTED`。
- Scope：仅限 `V1.2_APPROVAL_PACK_05_DEPLOYMENT_RECOVERY.md` 明列的 Pack 文件及其审计、Decision、Task/Evidence 记录。
- Boundary：不安装 Gemini、不执行 Claude/Gemini Live Runtime、不启用 Hook/MCP/Plugin/Skill、不刷新最终 V1.2 Recovery Evidence；不构成 Merge、V1.2 Release、Tag、Push、外部数据授权或纯净发行包发布。
- Integration：在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；默认 Canonical 生效等待最终合并与 V1.2 Release Evidence。
- Founder Approval：用户明确回复“可以”。

### PAOS-021｜V1.2 Skills Pack 批准

- 状态：`APPROVED`
- 日期：`2026-09-01`
- Owner：Founder / `paos-19-v1-2-canonical-promotion-audit`
- Decision：批准 Skills Architecture、Schema、Registry 规范与具体已登记 Skills 组成 V1.2 Approval Pack 06，完成实施与 Promotion。
- Contract Boundary：`00_system/skills/SKILLS_ARCHITECTURE.md` 升级为 Approved Canonical Rule；`00_system/schemas/skill-registry.schema.json` 升级为 0.2；`02_registry/skills.toml` 保持 Runtime Registry；已登记 Skills 保持在 `.agents/skills/` 下按需工作协议定位。
- Protocol Boundary：规范标准 YAML Frontmatter 契约（`name`/`description`）；明确 Skills 按需加载、非全局常驻、权限不扩散与严禁未经授权破坏性操作安全红线。
- Alignment Boundary：修复 `create-paos-project` 技能中的 `deploy_adapter.py` 调用参数，增加 `--authorization-ref` 与 `--backup-dir` 说明，与 Pack 05 部署安全门禁精确对齐。
- Validation Boundary：`validate_repository.py` 增加对已登记 Skill 实体文件存在性与 Frontmatter 格式的深度校验；Schema 测试套件增加针对 Skill Registry 的校验用例。
- Scope：仅限 `V1.2_APPROVAL_PACK_06_SKILLS.md` 明列的 Pack 文件及其审计、Decision、Task/Evidence 记录。
- Integration：在 `codex/v1.2-canonical-promotion` 分支形成批准实现与 Promotion Evidence；默认 Canonical 生效等待最终合并与 V1.2 Release Evidence。
- Founder Approval：用户明确批准推进。

### PAOS-REL-006｜Personal AI OS 1.2.0 Release 批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-20-v1-2-formal-release`
- Decision：批准 Personal AI OS V1.2.0 本地正式发布，包括六大 Approval Pack 的合流、双路径恢复演练、Tree Digest V0.2 固化与本地 annotated tag `v1.2.0`。
- Baseline Boundary：已批准基线正式晋升为 `v1.2.0 / PAOS-REL-006`。
- Release Gate Boundary：M1~M6 全部门禁通过；Release Evidence 由 annotated tag 与本地 Bundle 共同证明。
- Synchronization Boundary：本发布仅限本地 Control Plane，不执行 `git push`；远端同步由 Founder 自行在 VS Code 独立操作。
- Founder Approval：用户明确批准发版推进。

### PAOS-022｜Antigravity 平台迁移与适配规范批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-21-antigravity-platform-migration`
- Decision：将系统中历史 `gemini-cli` 平台标识与适配层全面迁移更正为 `antigravity-cli`（Google DeepMind Antigravity CLI / AGY），并与当前真实本地环境对齐。
- Contract Boundary：`00_system/compatibility/adapter_profiles.toml`、`platforms.toml` 与 `capabilities.toml` 将平台更正为 `antigravity-cli`；原生配置文件保持 `.gemini/settings.json` 与 `.agents/` 映射。
- Adapter Boundary：适配器重命名生成至 `03_adapters/antigravity-cli/`；部署规范更新为 `06_deployment/ANTIGRAVITY_DEPLOYMENT.md`；`create-paos-project` 技能更新部署路径。
- Runtime Boundary：在 `02_registry/runtimes.toml` 中将 `antigravity-cli` 状态更正为 `INSTALLED`（实测 `config_load = PASS`, `runtime_smoke = PASS`），消除历史未安装失真状态。
- Schema Boundary：Task、Hook、Runtime 与 System Schemas 全面增加/更新 `antigravity-cli` 平台枚举支持。
- Founder Approval：用户明确指示更正并批准实施方案。

### PAOS-REL-007｜Personal AI OS 1.2.1 Release 批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-21-antigravity-platform-migration`
- Decision：批准 Personal AI OS V1.2.1 本地正式发布，包括 Antigravity CLI 平台迁移、真实运行时账本刷新、双路径恢复演练与本地 annotated tag `v1.2.1`。
- Baseline Boundary：已批准基线正式晋升为 `v1.2.1 / PAOS-REL-007`。
- Release Gate Boundary：M1~M6 全部门禁通过；Release Evidence 由 annotated tag 与本地 Bundle 共同证明。
- Synchronization Boundary：本发布仅限本地 Control Plane，不执行 `git push`；远端同步由 Founder 自行在 VS Code 独立操作。
- Founder Approval：用户明确批准发版推进。

### PAOS-023｜V1.2.1 发布后证据完整性与门禁盲区整改批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-22-v1-2-1-post-release-remediation`
- Decision：批准修复 V1.2.1 发布后遗留与新引入的证据完整性、门禁盲区与 Dashboard 安全缺陷，并补齐 tag 重新指向的治理记录。
- Tag Boundary：确认 annotated tag `v1.2.1` 已于 `2026-09-02` 由 `299f25a` 重新指向 `15cfee2`；本决定只补记该事实，不再移动、删除或重建任何 tag。原发布提交 `299f25a` 保留在历史中但不再有 ref 指向。
- Evidence Boundary：Recovery Artifact 文件名必须内嵌 Tested Commit 前缀；M5 增加对应断言，重复演练不得原地覆盖上一次物证。`SYSTEM.toml` 的 `freeze_commit` 更正为 `c8e3ecc0`，恢复状态更正为 `PASS_V1.2.1`。
- Gate Boundary：`ci_gate.py` 默认 profile 增加真实 `release_audit.py` 调用并暴露 `overall`；`release_audit.py` 以 exit 0 返回 BLOCKED 的行为不再被显示成 PASS。BLOCKED/STALE 属开发期正常状态，不使 local-offline profile 失败。
- Runtime Boundary：`claude-code` 运行时账本按实测更正为 `INSTALLED` / `runtime_smoke = PASS` 并附证据；对应测试改为"PASS 必须带证据"的通用断言，不再钉死平台字面量。
- Security Boundary：`dashboard/` 只监听 `127.0.0.1`、静态根收紧至 `dashboard/`、移除 `Access-Control-Allow-Origin: *`、门禁面板改为真实审计数据；该目录仍为 `GENERATED` / `WORKING`，不参与 Canonical Promotion。
- Scope：不发起 V1.2.2 Release，不修改 `approved_baseline.version` 与 `git_tag`，不执行 Push、部署或破坏性 GC。
- Consequences：本轮变更提交后，M5/M6 将如实转为 `STALE`/`BLOCKED`，直至 Founder 决定是否发起下一次发布。这是正确状态，不得通过重打 tag 消除。
- Founder Approval：用户明确授权修复上述问题。

### PAOS-024｜Temp 与 Quarantine 单次清理授权

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-23-v1-2-2-release`
- Decision：批准对 `99_temp/` 的过期过程文件执行一次性删除，并清除仓库内的 `__pycache__` 与 `.DS_Store`。
- Scope Boundary：删除 19 个超过 `plan_ttl_hours` 的 GC Plan 与全部 Quarantine 批次（内容为 9 个 `.DS_Store`、12 个 `.pyc` 与 1 个可由 Adapter Generator 重新生成的 `CLAUDE.md` 备份）。全部目标均在 `.gitignore` 覆盖范围内，未进入任何 Commit、Tree Digest 或 Release Bundle。
- Retention Boundary：`99_temp/deploy_records/`、`99_temp/deployment_records/` 与 `99_temp/deployment_backups/` 属于部署证据与回滚材料，**不在本次清理范围内**，全部保留。
- Tool Boundary：`00_system/lifecycle/gc.toml` 保持 `destructive_delete = false` 与 `execution_mode = "QUARANTINE_ONLY"` 不变；本次删除是工具之外的 Founder 单次授权动作，不改变 GC 默认安全策略，也不构成后续自动清理授权。
- Consequences：被删除 Quarantine 项的恢复路径同时消失；因内容均为可重新生成的 OS 与 Python 缓存产物，判定为可接受损失。
- Founder Approval：用户明确指示清理无用过程文件。

### PAOS-REL-008｜Personal AI OS 1.2.2 Release 批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-23-v1-2-2-release`
- Decision：批准 Personal AI OS V1.2.2 正式发布，内容为 `PAOS-023` 的证据完整性与门禁盲区整改、`PAOS-024` 的 Temp 清理，以及双路径恢复演练与 annotated tag `v1.2.2`。
- Baseline Boundary：已批准基线正式晋升为 `v1.2.2 / PAOS-REL-008`。
- Release Gate Boundary：M1~M6 全部门禁通过；Release Evidence 由 annotated tag 与本地 Bundle 共同证明。Bundle 文件名内嵌 Tested Commit 前缀，不覆盖 v1.2.1 的物证。
- Tag Boundary：`v1.2.2` 为新建 annotated tag，绑定本次 Release Commit；不移动、不重写任何既有 tag，`v1.2.1` 保持指向 `15cfee2`。
- Synchronization Boundary：Founder 本轮明确授权 `git push`，范围经确认后限定为 **只推送 `main`**。annotated tag `v1.2.2` 与既有本地 tag 一律不 push，`SYSTEM.toml` 的 `release = "APPROVED_LOCAL_TAG_NOT_PUSHED"` 继续成立。
- Founder Approval：用户明确指示发布 1.2.2 并推送。

### PAOS-025｜移除 Dashboard 组件

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-24-dashboard-removal`
- Decision：从仓库中移除 `dashboard/`（`README.md`、`index.html`、`server.py`）。Founder 确认该组件不再需要。
- Background：该目录自 `paos-13` 起长期按 Founder 指令排除在治理与验收之外，`HANDOFF_TO_CODEX_POST_V1.1.2.md` 已记录"Founder 表示后续会删除"。`PAOS-023` 曾对其执行安全整改并随 `v1.2.2` 发布，本决定在其之后生效，不改写该发布内容。
- Scope Boundary：只删除 `dashboard/` 三个文件。`07_working/reviews/**` 中关于该组件的评审记录、`CHANGELOG.md` 的历史条目、`PAOS-023` 的 Security Boundary 以及 `02_registry/tasks.toml` 中含 `dashboard` 字样的任务 ID 与验证标记全部保留，作为历史证据不得改写。
- Dependency Boundary：Harness 与 Release Gate 从未引用该目录，删除不影响 `validate_repository.py`、`release_audit.py`、`ci_gate.py` 或任何测试；`02_registry/skills.toml` 中的 `owner = "paos-13-session-manager-and-dashboard"` 是任务 ID 而非路径，保持不变。
- Recovery Boundary：内容保留在 Git 历史与 `v1.2.2` 及更早的 tag、Bundle 中，可随时取回。
- Founder Approval：用户明确说明该组件由本人删除且不再需要。

### PAOS-TMPL-004｜Project Base Pack 1.2.0 批准

- 状态：`APPROVED`
- 日期：`2026-09-02`
- Owner：Founder / `paos-25-project-template-v2`
- Decision：批准 `01_templates/project-base-pack` 升级至 `1.2.0`，取代 `1.1.0`（`PAOS-TMPL-002`）作为唯一 `PROJECT_SCAFFOLD` 模板包。
- Type Boundary：项目类型收敛为四类——`SOFTWARE_DEVELOPMENT`、`SOLUTION_RESEARCH`、`CONTENT_MARKETING`、`BRAND_MANAGEMENT`。每类必须提供一份专属约定框架，经 `template.toml` 的 `primary_types` 过滤器产出到目标项目的 `00_governance/PROJECT_TYPE_FRAMEWORK.md`。新增类型未提供框架文件即视为配置缺陷。
- Structure Boundary：项目目录改为数字编号，语义可对应处沿用 Personal AI OS 的编号：`00_governance/`、`01_sources/`、`02_knowledge/`、`05_harness/`、`07_working/`、`09_archive/`、`99_temp/`。
- Harness Boundary：每个项目随附 `05_harness/validate_project.py` 与 `HARNESS.md`。校验器只读、不自动修复、不自动改状态；`--require-active` 作为 `PROVISIONAL → ACTIVE` 的可验证门槛。项目可自行扩展该校验器，属于项目自治范围，不回写 Personal AI OS 模板。
- Stack Boundary：`project.toml` 新增 `[stack]` 表作为技术栈的唯一机器可读来源；依赖清单继续使用语言原生文件，不发明新格式。软件开发类转 `ACTIVE` 前必须填写 `language` 与 `test_command`。
- Factory Boundary：`create_project.py` 的 `load_plan` 新增 `primary_types` 过滤器；被过滤跳过的模板仍计入"已登记来源"，不触发未登记文件检查。`template-pack.schema.json` 与 `validate_repository.py` 的目标路径重复检查同步放行"类型互斥的同名目标"，并拒绝类型重叠或混入无过滤记录的情况。
- Migration Boundary：本次不迁移既有项目。`1.1.0` 生成的项目（含 `demo-test`）保持原样，其 `primary_type` 取值已不在新枚举内，重新校验时会报类型不匹配；是否重建由项目 Owner 决定。
- Evidence：四种类型各完成一次真实 `--apply --git` 创建；各自只产出匹配的类型框架；随附校验器在新项目默认模式 `ERRORS=0`，`--require-active` 正确拒绝未填写项，填写后通过，并能检出状态漂移。
- Founder Approval：用户明确指示保留四类项目类型、为每类编写独立约定框架、为新项目提供校验与自我迭代能力、目录采用数字编号。

## Candidate Decisions

- 当前无待确认 Candidate Decision。
