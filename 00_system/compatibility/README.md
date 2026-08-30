# Compatibility

- `platforms.toml`：平台身份、原生文件和审计状态。
- `adapter_profiles.toml`：生成 Candidate Adapter 的平台配置 Source。
- `capabilities.toml`：逐平台、逐能力区分文档支持、已配置、Config Load、Runtime Verified 与授权阻塞。

禁止把 `supported_by_docs`、`configured` 或 `config_loaded` 单独解释为 `runtime_verified`。

> 状态：`WORKING`

跨 Agent 能力使用以下状态：`NATIVE`、`ADAPTER`、`MANUAL`、`UNSUPPORTED`、`UNVERIFIED`。

在官方资料核验前，不得假定不同平台的 Hooks、Permissions、Skills、Settings 或 Subagents 语义等价。
