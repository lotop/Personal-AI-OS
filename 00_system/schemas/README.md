# Schemas

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-019`

当前已建立：

- `system.schema.json`
- `task-registry.schema.json`
- `project-registry.schema.json`
- `agent-registry.schema.json`
- `skill-registry.schema.json`
- `runtime-registry.schema.json`
- `hook-registry.schema.json`
- `adapter-manifest.schema.json`
- `template-pack.schema.json`
- `bindings.toml`

`05_harness/schema_validation.py` 实现无第三方依赖的必要 JSON Schema 子集。该子集只支持 `type`、`enum`、`minLength`、`pattern`、`minItems`、`uniqueItems`、`items`、`required`、`properties` 与布尔 `additionalProperties`；Schema 关键字类型和正则表达式本身也必须合法。`uniqueItems` 使用稳定 JSON 规范化，不依赖 Python `repr`。使用未实现或无效关键字的 Schema 会 Fail Closed。`02_registry/` 当前六个 TOML Registry 均已绑定 Schema。
