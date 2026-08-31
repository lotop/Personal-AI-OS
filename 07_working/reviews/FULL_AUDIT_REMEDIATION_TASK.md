# Personal AI OS 全仓审计整改任务

> 状态：`REVIEW`
>
> 日期：`2026-09-01`
>
> Task ID：`paos-16-full-audit-remediation`
>
> Owner：`paos-16-full-audit-remediation`

## Objective

继续 Codex 在 V1.1.2 发布后完成的全仓审计，修复已确认且不依赖 Founder 新决策的实现缺陷，并为每个缺陷补充自动化负向验证。

## Scope

- 加固 Temp/Cache Cleanup：执行阶段必须证明计划未被篡改，且每个计划项仍属于实时发现的允许清理范围。
- 加固 Project Factory：结构化格式变量安全转义、渲染后验证、Template Pack 用途声明与可实例化边界。
- 恢复 JSON Schema Draft 2020-12 的 `pattern` 匹配语义。
- 收紧 M5 Recovery Follow-up 白名单，避免任意平铺文件绕过恢复证据新鲜度检查。
- 复核此前审计中的 Gemini、Hooks、Deployment 与状态文档问题；只修复具有本地证据的确定问题。
- 归档已被明确忽略的 Claude Handoff，但保留历史证据。

## Excluded

- `dashboard/**`：遵循 Founder 既有指令，本任务不修改、不运行、不验收。
- 首个真实业务项目验证：等待 Founder 后续指定项目和目标路径。
- Live Runtime、外部数据传输、远端部署、Push、Tag、Release Approval 与 Canonical Promotion。
- 未经批准的 Overlay 差异化模板设计。

## Read Set

- 全仓库受管文件、Git 历史与现有验证记录。
- 与 Factory、GC、Hooks、Adapters、Deployment、Schema 和 Release Gate 直接相关的规则与实现。

## Write Set

- `04_project_factory/`、`05_harness/` 中与本任务缺陷直接相关的实现、测试和说明。
- `01_templates/*/template.toml` 及其 Schema（仅增加 Pack 用途与验证边界，不修改已批准模板正文）。
- `00_system/`、`02_registry/` 中与上述实现一致性直接相关的配置、Schema 与账本。
- `07_working/reviews/` 中本任务记录、旧 Handoff 归档状态与验证证据。
- `README.md`、`CHANGELOG.md`（仅事实同步）。

## Dependencies

- 以当前本地 `main` 为实施基线。
- 依据 Founder 既有明确指令直接在本地仓库实施明显错误修订；不建立分支、不 Push。
- 修改同一文件时不并行写入。

## Expected Output

- 缺陷修复及对应负向测试。
- 完整本地离线 CI 结果与专项验证证据。
- 未解决项与下一阶段边界清单。

## Acceptance Criteria

- 篡改 Cleanup Plan 不能移动任何非实时发现的允许清理项。
- Factory 对结构化目标文件执行安全渲染和解析验证；无效输入不能产生可应用计划。
- Factory/M3 明确区分可实例化 Project Pack 与仅供内容复用的 Artifact Template Pack。
- JSON Schema `pattern` 与 Draft 2020-12 非隐式锚定语义一致。
- M5 只允许已声明的恢复证据与任务账本发生恢复后跟进变化。
- 每项修复至少有一个会在旧实现失败的负向测试。
- `python3 05_harness/ci_gate.py --profile local-offline` 返回 `PASS`。
- 执行 Temp/Cache Cleanup 计划与安全重验；不执行破坏性删除。

## Completed

- Cleanup Apply 重新执行实时候选发现并核对 Path、Class、Reason、Reference Scan、Hold、Hash 与 Real Path；伪造 Canonical 文件和分类会在任何移动前失败。
- Project Factory 增加 Pack Kind 边界、渲染后 TOML/JSON/JSONL 解析验证；Core Artifact Library 不再被误当作项目脚手架。
- M3 只统计 Approved `PROJECT_SCAFFOLD`，并逐 Pack 执行真实 Dry Run。
- JSON Schema `pattern` 恢复 Draft 2020-12 非隐式锚定语义。
- M5 Follow-up 从任意平铺文件收紧为明确证据、Task Card、Handoff 与 Task Registry 类别。
- M6 强制要求 `approved_baseline.version`、Tag、Approval Reference 与 Release Commit 全部精确绑定。
- Hooks Registry 补齐 Policy 要求的完整合同字段与 Owner 引用门禁；Hooks 仍保持 Phase 1 Disabled。
- Adapter Deployment 增加 Manifest 必填字段、重复目标、symlink 逃逸、Source/Target 变化与 CREATE/REPLACE TOCTOU 防护。
- Gemini 配置按当前官方文档复核：`context.fileName` 支持数组且项目设置位于 `.gemini/settings.json`；仓库说明已与实际 `AGENTS.md` 加载方式对齐。
- Capability 中的 Codex 版本证据与 Runtime Registry 对齐。
- Claude Handoff 已按 Founder 指令标记为 `ARCHIVED`，不再作为执行入口。

## Validation Evidence

- `python3 05_harness/ci_gate.py --profile local-offline`：`PASS`，8/8 checks。
- `04_project_factory/test_factory.py`：14 tests PASS。
- `05_harness/test_schema_validation.py`：11 tests PASS。
- `05_harness/test_release_audit.py`：13 tests PASS。
- `05_harness/test_temp_cleanup.py`：6 tests PASS。
- `06_deployment/test_deployment.py`：7 tests PASS。
- `05_harness/validate_repository.py`：`ERRORS=0`；提交前仅保留 Dirty Working Tree warning。
- `generate_adapters.py --check`：`ADAPTERS_OK`。
- `git diff --check`：PASS。
- Python Compile：PASS；缓存定向到 `/private/tmp/paos16-pycache`，未写入仓库。
- Temp Cleanup：生成并安全应用 `gc-20260831T210102Z`，发现 `0` 项，无文件被移动或删除。
- Gemini 官方证据：`https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md`。

## Open Risks / Excluded Follow-up

- `dashboard/**` 仍按 Founder 指令排除，未运行、未修改、未验收。
- 真实业务项目 E2E 等待 Founder 指定项目与仓库外目标路径。
- Claude Code / Gemini Live Runtime 仍受外部数据授权边界限制。
- Release Readiness 当前预期为 `M5 STALE / M6 BLOCKED`；本任务不是新版本发布、Tag 或 Release Approval。
- Recovery Drill 的 Bundle 未作为仓库内 Artifact 保留；下一次正式发布演练需要同时确定外部 Bundle 保存位置与可独立校验的 Artifact Reference。
