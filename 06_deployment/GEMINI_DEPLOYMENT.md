# Gemini CLI Deployment

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-020`
>
> 官方资料核验：`2026-09-01`

## 原生能力边界

- Gemini CLI 默认使用分层 `GEMINI.md` 作为上下文文件。
- 项目级设置位于 `.gemini/settings.json`，覆盖用户设置。
- `context.fileName` 可以配置一个或多个上下文文件名。
- 当前官方键为 `context.loadMemoryFromIncludeDirectories`；不得使用已漂移的 `loadFromIncludeDirectories`。
- Folder Trust 启用且目录不受信任时，项目 Settings 会被忽略；部署成功不等于 Config/Context Load。
- Hooks 在 `settings.json` 的 `hooks` 对象中配置，并通过 JSON 输入输出通信。
- 项目级 Hooks 应视为不可信代码，启用前必须完成信任检查。

## 当前部署映射

- Personal AI OS 规则源保持为根 `AGENTS.md`，不复制或分叉 Canonical Rule。
- `.gemini/settings.json` 通过官方 `context.fileName` 数组将 `AGENTS.md` 设为项目上下文文件；当前不额外生成 `GEMINI.md` Router。
- Gemini Adapter → 保存于 `03_adapters/gemini-cli/`，部署前进行 JSON Schema 验证。
- Hooks → Phase 1 保持禁用，后续逐项生成与审批。

## 验收

- `/memory show` 或等效检查能显示预期上下文层级。
- 项目级设置通过官方 JSON Schema。
- 没有把 TOML 字段直接写入 Gemini 原生 JSON。
- Hooks 不输出非 JSON 内容到标准输出。
- Smoke Test 能读取项目目标、Task Card 和适用规则。

当前只完成项目配置生成与历史 Config Load 证据；`2026-09-01` 本机 CLI 未安装，不能将其扩大为当前 Config Load、Context Load 或 Live Runtime Smoke。
