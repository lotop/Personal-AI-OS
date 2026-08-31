# Changelog

## V1.1.2 Formal Release Preparation

- 新增 Approved `01_templates/core-template-pack` 版本 `1.1.2`，覆盖 13 类核心模板。
- 登记 `PAOS-TMPL-003`，按 Founder 明确授权批量批准核心模板，不再逐项等待确认。
- 原 `07_working/candidates/` 候选模板归档到 `09_archive/v1.1.2-template-candidates/`。

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
