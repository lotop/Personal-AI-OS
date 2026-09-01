# Configuration Formats

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`（`PAOS-016`）

- Markdown：规则、说明、决策、知识和模板。
- TOML：人工维护的 Canonical Config 与 Registry。
- JSON：平台原生配置和机器生成数据。
- JSONL：追加式事件与审计记录。
- YAML：仅在外部工具明确要求时使用。
- Secrets：仅保存引用，不保存真实值。

所有结构化配置后续必须绑定 Schema 版本并通过解析验证。
