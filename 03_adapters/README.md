# Adapters

> 状态：`WORKING`

Adapter 将已批准的跨平台规则转换为目标平台原生配置。

- Adapter 是 `GENERATED`，不是 Source of Truth。
- 每个 Adapter 必须带 Source 版本、生成器版本和验证结果。
- 不支持的能力必须显式标记为 `MANUAL`、`UNSUPPORTED` 或 `UNVERIFIED`。
- `codex/`：Codex 原生 TOML Candidate 与 Manifest。
- `gemini-cli/`：Gemini CLI 原生 JSON Candidate 与 Manifest。

当前 Codex 与 Gemini CLI Adapter 已生成但尚未部署。修改应回到 `00_system/compatibility/adapter_profiles.toml`，再运行 `05_harness/generate_adapters.py`。
