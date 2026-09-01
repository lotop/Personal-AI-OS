# Antigravity CLI Deployment

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-022`
>
> 官方资料核验：`2026-09-02`

## 原生能力边界

- Google DeepMind Antigravity (AGY) 体系原生支持项目级 `AGENTS.md` / `GEMINI.md` 作为上下文文件。
- 项目级设置位于 `.gemini/settings.json`，工作区定制位于 `.agents/`（包含 skills 与 rules）。
- 全局用户定制位于 `~/.gemini/config/`。
- `context.fileName` 可以配置一个或多个上下文文件名（如 `["AGENTS.md"]`）。
- 当前官方键为 `context.loadMemoryFromIncludeDirectories`；不得使用已漂移的 `loadFromIncludeDirectories`。
- Folder Trust 启用且目录不受信任时，项目 Settings 会被忽略；部署成功不等于 Config/Context Load。
- Hooks 在 `settings.json` 的 `hooks` 对象中配置，并通过 JSON 输入输出通信。
- 项目级 Hooks 应视为不可信代码，启用前必须完成信任检查。

## 当前部署映射

- Personal AI OS 规则源保持为根 `AGENTS.md`，不复制或分叉 Canonical Rule。
- `.gemini/settings.json` 通过官方 `context.fileName` 数组将 `AGENTS.md` 设为项目上下文文件；当前不额外生成 `GEMINI.md` Router。
- Antigravity Adapter → 保存于 `03_adapters/antigravity-cli/`，部署前进行 JSON Schema 验证。
- Hooks → Phase 1 保持禁用，后续逐项生成与审批。

## 验收

- Antigravity IDE / CLI 能正确识别工作区规则与技能。
- 项目级设置通过官方 JSON Schema。
- 没有把 TOML 字段直接写入 Antigravity 原生 JSON。
- Hooks 不输出非 JSON 内容到标准输出。
- 当前任务在 Antigravity 运行环境下成功读取项目目标、Task Card 和适用规则。
