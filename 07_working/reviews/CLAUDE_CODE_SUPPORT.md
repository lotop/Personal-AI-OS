# Claude Code Support Review

> 状态：`ARCHIVED`
>
> Canonical Authority：`NONE`
>
> 分支：`codex/claude-code-support`
>
> 执行日期：`2026-08-31`
>
> Replacement：`PAOS-TMPL-002`、`PAOS-REL-002` 与 `HANDOFF_V1.1.1.md`

## Objective

为 Personal AI OS 控制平面与 Project Factory Working Candidate 增加 Claude Code 原生入口和可验证的项目配置，同时复用 `AGENTS.md` Router，不复制治理正文。

## Scope 与边界

- Read Set：适用 Governance/Security、Compatibility、Adapter Generator、Deployment、Factory 与 Candidate Pack。
- Write Set：Compatibility Source、Claude Code Generated Adapter、项目级部署目标、Candidate Pack、Harness/Factory 验证及相关导航。
- Non-goals：不修改 Approved Template Pack，不安装 Claude Code，不运行会发送项目内容的 Live Runtime，不启用 Hooks，不执行 Commit、Tag、Push 或 Promotion。

## 变更原因与官方依据

Claude Code 原生读取 `CLAUDE.md`，不会直接读取 `AGENTS.md`。官方文档明确支持在 `CLAUDE.md` 使用 `@AGENTS.md` 导入；共享项目配置位于 `.claude/settings.json`。因此采用薄 Adapter，继续以 `AGENTS.md` 和 `00_system/` 为 Source of Truth。

## 实施

- 在 `adapter_profiles.toml` 登记 Claude Code context 与 settings Source。
- 生成 `03_adapters/claude-code/CLAUDE.md`、`settings.json` 和 Manifest。
- 部署根 `CLAUDE.md` 与 `.claude/settings.json`；配置只拒绝读取 `.env` 类文件，不扩大权限。
- 优化薄启动器：加入 `/context` 诊断、导入失败停止、禁止 `/init` 覆盖，以及 Auto Memory 与项目级扩展的治理边界。
- 在 Working Candidate Pack `0.3.0-working` 中加入相同入口和配置。
- 增加 Claude Code Deployment 说明、Capability Evidence 和离线验证覆盖。

## Compatibility 与 Migration

- 对 Codex 与 Gemini CLI 向后兼容；两者现有生成目标不变。
- 正式 `01_templates/project-base-pack` 已按 `PAOS-TMPL-002` 升级至 `1.1.0`，纳入 `CLAUDE.md` 与 `.claude/settings.json`。
- Candidate Pack 的 Claude 文件已按 `PAOS-TMPL-002` 迁移到正式 Pack；本条保留为历史实施轨迹。

## Rollback

- 根项目回滚：删除本轮新建的 `CLAUDE.md` 与 `.claude/settings.json`，并回退 Compatibility Source/Generator；Generated 文件应重新生成，不直接修补。
- Candidate Pack 回滚：回退 `template.toml` 至 `0.2.0-working` 并移除两项新增 Candidate 文件。
- 本轮没有用户级设置、Hooks、外部发布或不可逆迁移。

## 验收状态

- Adapter Generation：`PASS`（`ADAPTERS_OK`）。
- Local Offline CI：`PASS`（repository、factory、schema、release-audit tests、deployment、tree-digest、adapters）。
- Factory Tests：`PASS`（11 tests，包含 Working Candidate Dry Run、Apply、Git init 与 Claude 文件断言）。
- Deployment Tests：`PASS`（3 tests，包含幂等、覆盖前备份与部分失败回滚）。
- Candidate Factory E2E：`PASS`。
- `git diff --check`：`PASS`。
- Claude Config Load：`PASS`（官方 npm 包 `2.1.251`，`claude doctor` exit `0`；未登录、未发送项目内容）。
- Claude Live Runtime：`BLOCKED_EXTERNAL_DATA_AUTHORIZATION`。
- Release M4：满足 Config Load 要求；Live Runtime 保持 Conditional，不冒充 Runtime PASS。
- Template Approval / Release Approval / Promotion：已由 `PAOS-TMPL-002`、`PAOS-REL-002` 与 `v1.1.1` 完成；本 Review 不再代表当前状态。
