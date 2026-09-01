# Adapters

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`
>
> Approval Reference：`PAOS-022`

Adapter 将已批准的跨平台规则转换为目标平台原生配置。

- Adapter 是 `GENERATED`，不是 Source of Truth。
- 每个 Adapter 必须带 Source 版本、生成器版本和验证结果。
- 不支持的能力必须显式标记为 `MANUAL`、`UNSUPPORTED` 或 `UNVERIFIED`。
- `codex/`：Codex 原生 TOML Working Adapter 与 Manifest。
- `claude-code/`：Claude Code 原生 Markdown/JSON Working Adapter 与 Manifest。
- `antigravity-cli/`：Antigravity CLI 原生 JSON Working Adapter 与 Manifest。

当前 Codex、Claude Code 与 Antigravity CLI Working Adapter 已生成并部署到项目级路径。修改应回到 `00_system/compatibility/adapter_profiles.toml`，再运行 `05_harness/generate_adapters.py`；对其他项目或用户级目录的部署仍需单独授权。

边界：本 README 只批准 Adapter 的生成与管理规则。`03_adapters/*`、Manifest 和项目根部署目标继续保持 `GENERATED/WORKING`；文件存在或字节一致只证明 Configured/Deployed，不证明平台已通过 Trust Gate、Config/Context Load、Live Runtime 或 External Data Authorization。
