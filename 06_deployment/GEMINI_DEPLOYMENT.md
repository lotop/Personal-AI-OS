# Gemini CLI Deployment

> 状态：`WORKING`
>
> 官方资料核验：`2026-08-30`

## 原生能力边界

- Gemini CLI 默认使用分层 `GEMINI.md` 作为上下文文件。
- 项目级设置位于 `.gemini/settings.json`，覆盖用户设置。
- `context.fileName` 可以配置一个或多个上下文文件名。
- Hooks 在 `settings.json` 的 `hooks` 对象中配置，并通过 JSON 输入输出通信。
- 项目级 Hooks 应视为不可信代码，启用前必须完成信任检查。

## 候选部署映射

- Personal AI OS 规则源 → 生成 `GEMINI.md` Router，不直接复制全部治理正文。
- `.gemini/settings.json` → 仅写平台原生字段；可配置读取 `AGENTS.md` 与 `GEMINI.md`。
- Gemini Adapter → 保存于 `03_adapters/gemini-cli/`，部署前进行 JSON Schema 验证。
- Hooks → Phase 1 保持禁用，后续逐项生成与审批。

## 验收

- `/memory show` 或等效检查能显示预期上下文层级。
- 项目级设置通过官方 JSON Schema。
- 没有把 TOML 字段直接写入 Gemini 原生 JSON。
- Hooks 不输出非 JSON 内容到标准输出。
- Smoke Test 能读取项目目标、Task Card 和适用规则。
