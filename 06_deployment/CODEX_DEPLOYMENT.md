# Codex Deployment

> 状态：`WORKING`
>
> 官方资料核验：`2026-08-30`

## 原生能力边界

- Codex 在运行开始时读取 `AGENTS.md` 指令链。
- 全局层默认位于 Codex Home；项目层从项目根向当前工作目录逐层发现。
- 项目配置可使用 `.codex/config.toml`，用户配置使用 Codex Home 下的 `config.toml`。
- Hooks、Skills、Rules 和权限配置必须遵循当前 Codex 原生格式，不由 Personal AI OS 自创字段替代。

## 候选部署映射

- 根 `AGENTS.md` → 当前仓库根级 Router。
- 批准的规则 → 通过 Router 最小化引用，而非全部复制进 `AGENTS.md`。
- Codex 平台配置 → `03_adapters/codex/` 中生成后，经 Diff 写入目标。
- Project Factory 新项目 → 生成项目级 `AGENTS.md` 和可选 `.codex/config.toml`。

## 验收

- Codex 能识别项目根和根级 `AGENTS.md`。
- 指令链没有超过平台限制或重复加载全部规则。
- 项目配置通过官方 Schema 或 Codex 自检。
- 默认权限不扩大，Hooks 保持关闭。
- Smoke Test 能读取项目目标、Task Card 和适用规则。
