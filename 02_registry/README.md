# Registry

> 状态：`WORKING`

Registry 使用一级 TOML 文件，记录项目、任务、Agent、Skill、Runtime 和 Hook。六个 Registry 均已在 `00_system/schemas/bindings.toml` 绑定对应 JSON Schema，并由仓库验证器检查。

- `projects.toml`
- `tasks.toml`
- `agents.toml`
- `skills.toml`
- `runtimes.toml`
- `hooks.toml`

Schema 只验证结构与最小枚举；Runtime 事实、审批状态和外部授权仍需独立证据。
