<!-- GENERATED WORKING. 修改 Source 或生成器，不直接修改本文件。 -->
<!-- Source: 00_system/compatibility/adapter_profiles.toml -->

@AGENTS.md

## Claude Code Adapter

本文件是 Generated Working Adapter。统一项目规则来自 `AGENTS.md`；不得在此复制或分叉 Canonical Rule。

### 初始化与诊断

- 用 `/context` 确认 Context Load，用 `/status` 确认 Settings Source；两者不得互相替代。
- 若 `@AGENTS.md` 导入失败，在复杂写入前停止并报告。
- 不使用 `/init` 覆盖本文件；改进回到 Adapter Source 和生成器。

### Claude Code 专属边界

- Auto Memory、`CLAUDE.local.md` 和 Conversation 不自动成为正式事实。
- 不自行创建或启用 Rules、Hooks、Skills、Subagents 或 MCP。
- 项目配置需经 Workspace Trust；Live Runtime 与外部数据授权单独验证。
