# Changelog

## V1.3.0 Project Template Overhaul Release

由 `paos-24` ~ `paos-27` 实施，Decisions `PAOS-025`、`PAOS-TMPL-004`、`PAOS-TMPL-005`、`PAOS-REL-009`。

本次为**次版本升级**：模板包发生两次不向后兼容的结构变更，`1.2.x` 生成的项目不与新工厂兼容。

- **Project Base Pack 升级至 `1.3.0`**（`PAOS-TMPL-005`）：
  - **移除 overlay 概念**：它不改变任何生成内容也无消费方，保留只造成误解。`--overlay`、`allowed_overlays`、`overlays_csv` 与 `.paos-init.json` 的 `overlays` 一并移除；差异化职责已由类型框架承担。向导相应从 7 步简化为 6 步。
  - **`HANDOFF.md` 与 `SESSION_CLOSE.md` 改为纯追加式日志**，规则正文上移至 `AGENTS.md` 的「交接与会话收尾」一节，规则与记录载体分离。
  - **新增项目级 `CHANGELOG.md` 与「版本与发布」约定**：项目节奏由 Owner 定义，但发布必须绑定 40 位 Commit SHA、校验器退出码 `0`、工作树干净，且须经 Owner 明确授权。
  - `.paos-init.json` `schema_version` 升至 `0.3.0`；项目校验器必需文件加入 `CHANGELOG.md`。

- **新增项目创建交互向导**（`04_project_factory/new_project.py`）：逐步选择/输入参数，自动完成预演 → 确认 → 创建 → 注入 Codex/Antigravity 适配器 → 验收 → 首次提交。取值范围从 `factory.toml` 读取，`SLUG_PATTERN` 与 `AUTHORIZATION_PATTERN` 直接从既有脚本导入复用，不形成第二份规则定义。
- **修正 Skill 文档缺陷**：`deploy_adapter.py` 的 `AUTHORIZATION_PATTERN` 为 `^[A-Z0-9][A-Z0-9._:-]{2,127}$` 只接受大写，而 `project-id` 按定义是小写，原 `create-paos-project` Skill 文档给出的 `PAOS-INIT-<PROJECT_ID>` 在 `--apply` 阶段必然以 exit 2 失败。Dry Run 不校验该字段，问题只在正式部署时暴露。
- **Project Base Pack 升级至 `1.2.0`**（`PAOS-TMPL-004`）：
  - **项目类型收敛为四类**并各配一份专属约定框架，产出到项目的 `00_governance/PROJECT_TYPE_FRAMEWORK.md`：`SOFTWARE_DEVELOPMENT`（技术栈来源、工作循环、完成定义、质量红线）、`SOLUTION_RESEARCH`（来源 A/B/C/D 分级、证据要求、结论与置信度格式、方案比选）、`CONTENT_MARKETING`（受众与语气、生产流程、事实核查、发布授权、效果复盘）、`BRAND_MANAGEMENT`（品牌资产 L1~L4 分层、一致性校验、变更控制、危机响应边界）。
  - **项目目录改为数字编号**，语义可对应处沿用 PAOS 编号：`00_governance/`、`01_sources/`、`02_knowledge/`、`05_harness/`、`07_working/`、`09_archive/`、`99_temp/`。
  - **每个项目随附自己的 Harness**：`05_harness/validate_project.py` 检查结构、模板残留、占位内容、状态漂移、类型框架匹配、`[stack]` 完整性、首张 Task Card、只读边界与明文 Secret；`--require-active` 作为 `PROVISIONAL → ACTIVE` 的可验证门槛。`HARNESS.md` 定义项目自我迭代循环（发现 → 提案 → 决策 → 实施 → 归档 → 复校验），校验器本身可由项目扩展。
  - **新增 `[stack]` 表**作为技术栈唯一机器可读来源；补齐此前缺失的 `.gitignore` 与 `README.md`。
  - **Factory 支持按类型选择文件**：`load_plan` 新增 `primary_types` 过滤器，被跳过的模板仍计入已登记来源；Schema 与 `validate_repository.py` 的目标路径重复检查同步支持"类型互斥的同名目标"，并拒绝类型重叠或混入无过滤记录。
  - 既有 `1.1.0` 项目不迁移，其类型取值已不在新枚举内。
- **移除 `dashboard/`**（`PAOS-025`）：Founder 确认该组件不再需要。该目录自 `paos-13` 起长期排除在治理与验收之外，内容保留在 Git 历史与既有 tag、Bundle 中。相关历史评审记录与 `PAOS-023` 的安全整改记录一并保留，不改写。

## V1.2.2 Evidence Integrity Release

由 `paos-22-v1-2-1-post-release-remediation` 与 `paos-23-v1-2-2-release` 实施，Decisions `PAOS-023`、`PAOS-024`、`PAOS-REL-008`。

- **补记 tag 重新指向**：annotated tag `v1.2.1` 于 `2026-09-02` 由 `299f25a` 重新指向 `15cfee2`，原发布提交不再有 ref 指向。该事实此前无任何记录，现由 `PAOS-023` 与 Task Card 固化；本轮不再移动任何 tag。
- **harness git 环境隔离**（`c8e3ecc0`，由 Antigravity 会话实施）：`release_audit.py`、`tree_digest.py`、`validate_repository.py`、`create_project.py` 的 git 子进程改用受控 `GIT_ENV`，消除跨平台沙箱下的用户级 git 配置干扰。
- **恢复物证不再可被原地覆盖**：Recovery Artifact 文件名必须内嵌 Tested Commit 前缀，M5 增加断言并补充单元测试；`v1.2.1.bundle` 重命名为 `v1.2.1-c8e3ecc0.bundle`。
- **修复 CI Gate 漏报**：`release_audit.py` 无论 overall 为 PASS/STALE/BLOCKED 都返回 exit 0，此前默认 profile 把 BLOCKED 显示成 PASS。`ci_gate.py` 增加 `release-state` 项，直接解析 JSON 并如实暴露 `overall` 与未通过的 Gate。
- **状态漂移更正**：`SYSTEM.toml` 的 `freeze_commit` 更正为 `c8e3ecc0`；恢复状态由 `PASS_V1.2.0` 更正为 `PASS_V1.2.1`；`release` 更正为 `APPROVED_LOCAL_TAG_NOT_PUSHED`（main 由 Founder 自行同步至 origin，Release Tag 保持本地）。
- **运行时账本按实测更正**：`claude-code` 由 `TRANSIENT_AVAILABLE` / `NOT_RUN` 更正为 `INSTALLED` / `PASS` 并附证据；对应测试改为"PASS 必须带证据"的通用断言，不再钉死平台字面量。`antigravity-cli` 的 `version = "CURRENT"` 记入待办。
- **Dashboard 安全整改**：只监听 `127.0.0.1`（原 `0.0.0.0`）；静态根由仓库根收紧至 `dashboard/`（`.git/` 不再可下载）；移除 `Access-Control-Allow-Origin: *`；门禁面板由硬编码的 `WAITING_V1.1.2` 改为真实 `release_audit.py` 输出；`/guide` 缺失时明确 404。
- **悬空引用更正**：`DECISIONS.md` 中 `CORE_TEMPLATE_CANDIDATES.md` 的路径更正为归档后的实际位置。
- **Temp 清理**：按 Founder 单次授权删除 19 个过期 GC Plan 与全部 Quarantine 批次（9 个 `.DS_Store`、12 个 `.pyc`、1 个可重新生成的 Adapter 备份），并清除 `__pycache__` 与 `.DS_Store`。`99_temp/` 由约 404KB 降至 44KB。部署记录与部署备份作为证据保留，未删除。
- **发布**：Founder 授权 annotated tag `v1.2.2`（`PAOS-REL-008`），完成冷克隆与离线 Bundle 双路径恢复演练。

## V1.2.1 Platform Migration Release

- **平台标识与运行时全面更正**：将历史 `gemini-cli` 全面迁移更正为 **`antigravity-cli` (Google DeepMind Antigravity CLI / AGY)**。
- **适配器生成与部署重构**：生成 `03_adapters/antigravity-cli/`，目标保持原生映射至 `.gemini/settings.json` 与 `.agents/`，更新部署说明文档为 `06_deployment/ANTIGRAVITY_DEPLOYMENT.md`。
- **运行时账本真实证据刷新**：在 `runtimes.toml` 中将 `antigravity-cli` 状态更正为 `INSTALLED`（实测 `config_load = PASS`, `runtime_smoke = PASS`），消除历史未安装失真状态。
- **Schemas 与门禁全面对齐**：升级 Task、Hook、Runtime 与 System Schemas 平台枚举，更新 `release_audit.py` M4 适配器门禁。
- **文档与技能调用同步**：更新 `create-paos-project` 技能、`SKILLS_ARCHITECTURE.md` 与 `README.md`。
- Founder 授权本地 annotated tag `v1.2.1`（`PAOS-REL-007`）；不 Push。

## V1.2.0 Formal Release

- **六大 Approval Pack 全面收口**：完成 Governance、Security、Lifecycle、Identity、Mode、Memory、Factory、Templates、Harness、Hooks、Deployment、Recovery 与 Skills 全部六个模块的审查、修正与 Canonical Promotion。
- **治理与安全规则升级**：完善审批控制、变更审计、冲突解决、源码保护与外部数据权限安全红线。
- **项目工厂与模板体系强化**：模板零 Diff 固化，Factory 自动化验证与多平台初始化闭环。
- **Harness 与验证工具演进**：Tree Digest 升级至 V0.2（纳入 Git object kind/mode 与 SHA-256），Schema 校验器与 Repository Validator 强化 symlink 防御与深度契约检查。
- **适配器与部署安全门禁**：修复 Gemini 配置键漂移；`deploy_adapter.py` 强制要求 `--authorization-ref`、`--backup-dir` 覆盖保护并输出不可变部署记录。
- **Skills 架构规范**：升级 `SKILLS_ARCHITECTURE.md` 为 Approved Rule，对齐 `create-paos-project` 部署参数与标准 YAML Frontmatter。
- **发布与双路径恢复**：完成冷克隆与离线 Bundle 双路径演练，固化 V1.2.0 恢复证据，并通过 M1~M6 全部门禁。
- Founder 授权本地 annotated tag `v1.2.0`（`PAOS-REL-006`）；不 Push。

## V1.1.4 Local Release

- 修正 Decision Index、Physical Architecture 与 PAOS-015 Task Registry 的 V1.1.3 状态漂移。
- 登记 V1.1.4 → V1.2.0 Stable 路线，并建立六个 Module Approval Pack 审核机制。
- 本版本只发布一致性修订和审核入口，不执行 V1.2 Canonical Promotion。
- Founder 授权本地 annotated tag `v1.1.4`；不 Push。

## V1.1.3 Local Release

- 修复 PAOS-016 对两个 Approved Template Manifest 的原地元数据修改，将 Pack Kind 迁移到 Factory 自有配置。
- Factory 与 Repository Validator 共同校验 Pack 用途路由，拒绝未登记 Pack、非法类型及悬空路由。
- 移除 `approved_baseline.release_commit` 的 Git Commit 自引用设计；最终 Release Commit 改由 annotated tag 直接绑定。
- M5 新增实际 Bundle Artifact 路径、SHA-256、`git bundle verify` 与 Bundle Head 校验。
- 本地 Recovery Bundle 保存在被 Git 忽略的 `06_deployment/recovery_artifacts/`，不随 Push 传输。

## Post-V1.1.2 Working（本地继续修订）

- 建立 `paos-16-full-audit-remediation`，忽略并归档已失真的 Claude Handoff，恢复 Codex 原全仓审计整改清单。
- Cleanup Apply 阶段重新发现并核对允许清理范围，拒绝被篡改为 Canonical 文件或伪造分类的计划项。
- Template Pack 增加 `PROJECT_SCAFFOLD`／`ARTIFACT_LIBRARY` 用途；Factory 对结构化输出执行计划阶段解析，M3 对每个 Approved Project Pack 运行真实 Dry Run。
- JSON Schema `pattern` 恢复 Draft 2020-12 非隐式锚定语义；M5 白名单收紧到已声明的证据、Task Card 与 Handoff 类别。
- Hooks Registry 补齐 Policy 要求的合同字段；Adapter 部署拒绝目标 symlink 逃逸与重复目标。
- Gemini 部署说明与实际 `context.fileName = ["AGENTS.md"]` 配置及当前非 Live Runtime 边界对齐。
- Capability 中的 Codex 版本证据与 Runtime Registry 对齐，并新增 Skill/Hook Owner 与 Capability/Runtime 跨文件引用门禁。

由 `paos-15-post-v1-1-2-remediation` 实施的评审整改；`dashboard/**` 按 Founder 指令完全排除。

- 修正 `02_registry/projects.toml` 的已批准基线漂移（`1.1.1` → `1.1.2`），并新增 `SYSTEM.toml`
  与 Project Registry 的跨文件一致性校验。
- 将 `approved_baseline.git_commit` 拆分为 `freeze_commit` 与 `release_commit`，同步 Schema，
  并在 M6 增加 Tag、Approval Reference 与 Release Commit 的绑定断言。
- Schema 子集校验器新增未实现关键字守卫；后续 PAOS-016 将 `pattern` 修正为 Draft 2020-12 匹配语义；`additionalProperties` 限定布尔值。
- 新增工作日志状态门禁；状态词汇表动态取自 `states.toml` 与 `tasks.toml`，并归一三处越权状态值。
- M5 恢复跟进白名单由逐版本文件名改为目录前缀判定，审计器不再需要随每次发布修改。
- 纠正 README 的 M6 说明、Harness 与 Schemas 说明、Identity 说明，并把 overlay 如实描述为分类标签。
- 将历史 R0-R12 Gate 模型入口归档到 `09_archive/v1.1-release-gates-v2/`。
- 解除 `test_release_audit.py` 对活体仓库门禁状态的耦合，并在测试辅助函数中对 `audit()` 结果做单次缓存。
- 登记 `PAOS-013`，按 Founder 单次授权把本地 `main` 推送到既有 GitHub `origin`；不推送 annotated tag，不构成远端发布或 Release Approval。
- 本批次改动实现文件，`M5 Recovery` 如实转为 `STALE`；下次发布前必须重跑冷克隆与离线 Bundle 恢复演练。
- 登记 `PAOS-014`，按 Founder 后续明确授权推送 annotated tag `v1.1.0`／`v1.1.1`／`v1.1.2`；该决定取代 `PAOS-013` 的 tag 排除条款，`SYSTEM.toml` 的 `implementation.release` 同步更正为 `APPROVED_REMOTE_TAG_PUSHED`。Tag 对象未被重写或移动。

## V1.1.2 Formal Release Preparation

- 新增 Approved `01_templates/core-template-pack` 版本 `1.1.2`，覆盖 13 类核心模板。
- 登记 `PAOS-TMPL-003`，按 Founder 明确授权批量批准核心模板，不再逐项等待确认。
- 原 `07_working/candidates/` 候选模板归档到 `09_archive/v1.1.2-template-candidates/`。
- 登记 `PAOS-REL-003`，授权 V1.1.2 本地正式发布、本地 release commit 与本地 annotated tag `v1.1.2`；不包含 Push、远端发布、外部部署或 Dashboard 验收。

## V1.1.2 Working Revision

- 同步审计登记为 Gemini 的 Commit `a38929e`；Dashboard 暂按 Founder 指令排除，不纳入本轮修改与验收。
- 收窄 Session Manager 权限，修正命名示例、条件式 Session Close、DONE 验证门槛、Skill Owner 与平台 ID。
- 移除未经授权的 Release/Distribution 活动任务，增加 Skill Owner 与 Task Registry 引用检查。
- 修复 V1.1.1 发布后的 Project、Deployment、Claude Review 与 Registry 状态漂移。
- 增加经 Founder 明确授权的 Direct Main 小修订例外；不包含 Push、Tag 或 Release Approval。
- 建立 Decision、Identity、Mode、Memory、Task、Session/Handoff、Skill Registry 与 GC Plan 的扁平 Working Template Candidates。
- 为 Projects、Tasks、Agents、Skills、Runtimes 与 Hooks 六类 Registry 完成 JSON Schema 绑定。
- 要求所有 `07_working/reviews/*.md` 工作日志具有日期字段并加入自动验证。
- 建立 Temp/Cache 不可变计划、重验和可恢复 Quarantine 清理机制。

## V1.1.1 Local Release（Approved）

- 以 `PAOS-REL-002` 与本地 annotated tag `v1.1.1` 完成发布。
- 纳入 Claude Code Adapter、Config Load 验证与 Approved Project Base Pack `1.1.0`。
- 统一根入口、System、Project、Registry、Runtime 与 Skill 状态。
- 修正 README 中与 Task Registry 不一致的状态机说明。
- 移除重复 Skill 文件，将 `create-paos-project` 正式登记到 Skills Registry。
- 加固 M5：校验恢复 Commit、Bundle Commit、Bundle SHA-256、Tree Digest 与恢复后变更白名单。
- 加固 M6：要求 V1.1.1 Founder Approval、annotated Tag 和当前 HEAD 精确绑定。
- 旧 Gemini/Antigravity Handoff 保留为历史证据，V1.1.1 使用新 Handoff。

## Unreleased

- Founder 批准 PAOS-007，实施 V1.1 Minimum 简化；该批准不构成 Template/Release Approval 或 Promotion 授权。
- Mode 收敛为 `CHAT / WORK / REVIEW`，资产状态收敛为 `WORKING / APPROVED / ARCHIVED`。
- Task Registry 改为单一主状态加验证证据；Session Close/Handoff 改为条件触发。
- Release Readiness 从多层 Gate 收敛为 M1–M6，旧 V2 模型标记为历史快照。
- 固定 Python 3.11 推荐环境，并让 Apple Python 可使用 pip vendored tomli 运行统一本地验证。

- 初始化 Personal AI OS V1.1 本地 Working Repository。
- 补齐根级项目元数据与目录入口。
- 将根 `AGENTS.md` 升级为 `0.5-working`。
- 记录已确认的 PAOS-001 至 PAOS-004。
- 建立 Governance、Security、Modes、Memory、Lifecycle、Compatibility、Registry、Adapters 与 Harness 的 Working 骨架。
- 将总控与九个专业任务登记为可追溯的 Task Records。
- 扁平化 `02_registry/` 与说明型 `05_harness/` 子目录，并同步更新文件名和路径引用。
- 补建 `04_project_factory/` 与 `06_deployment/` Working 规范。
- 建立默认 Dry Run、拒绝覆盖、限制路径并要求 Approved Template Pack 的 Project Factory 引擎及测试。
- 依据官方资料更新 Codex 与 Gemini CLI 能力登记，并准备首个 Project AGENTS Template Candidate。
- 新增 SYSTEM、Task Registry、Adapter Manifest 与 Template Pack Schema 及无依赖验证器。
- 建立可重复生成的 Codex TOML、Gemini JSON Candidate Adapter 和默认 Dry Run 部署器。
- 将 Codex 与 Gemini CLI Candidate 配置部署到项目级路径并完成幂等演练；记录 Runtime 可用性与外部阻塞。
- 补齐 Mode、Memory、Conversation Close、Asset Lifecycle/GC、Skills、Multi-Agent Sync、Change Control、Handoff 与 Release Gate Working Specs。
- 完成本地 Git 干净克隆恢复演练，并加入机器可读 Release Gate 审计器与 Readiness Report。
- 完成 Codex CLI 只读 Runtime Smoke，验证 Agent 能加载项目指令并返回正确系统元数据。
- 验证 Gemini CLI `0.57.0` 与项目配置可加载；真实模型 Smoke 因缺少外发授权而保持阻塞，未发送项目内容。
- 完成包含完整历史的离线 Git Bundle 校验与恢复演练。
- 新增 Physical Architecture、V1.1 Consolidation Review 和 V1.0 Baseline Evidence Note。
- 将资产类别与成熟度状态分离，修正 `SOURCE` 被当作 Promotion 状态的问题。
- 将专业任务拆分为研究、本地产物、评审和实施进度，修正虚假完成状态。
- 本段记录 V1.1 正式发布前的历史实施状态；后续发布事实以 `PAOS-REL-001`、`PAOS-REL-002` 和对应 Tag 为准。
