# Schemas

> 状态：`WORKING`

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

`05_harness/schema_validation.py` 实现无第三方依赖的必要 JSON Schema 子集。该子集只支持 `type`、`enum`、`minLength`、`pattern`、`minItems`、`uniqueItems`、`items`、`required`、`properties` 与布尔 `additionalProperties`；`pattern` 按整串匹配。使用未实现关键字的 Schema 会被 `validate_repository.py` 直接判定失败，不会静默通过。`02_registry/` 当前六个 TOML Registry 均已绑定 Schema；Schema 验证通过不代表字段语义已经获得 Founder Approval。
