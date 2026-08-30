# Hooks Policy

> 状态：`WORKING`

Phase 1 Hooks 默认 `enabled = false`。

允许：检查、提醒、生成 Candidate、最小审计、输出验证报告。

禁止：自动批准、Canonical Promotion、commit、merge、push、deploy、publish、delete 和破坏性清理。

每个 Hook 必须声明：Stable ID、事件、Matcher、Scope、权限、副作用、幂等键、超时、失败策略、重试策略、日志范围和 Owner。

Hook 可以提出或执行已批准的固定拒绝规则，但不得代替用户允许高风险操作。

## Fail Closed 边界

- Hook 配置缺失、Schema 失败或权限范围不明时，不执行副作用。
- `deny` 只能基于已批准且可追溯的固定禁令；Hook 不得自行扩大禁令语义。
- Hook 超时不得默认转为允许高风险操作。
- Hook 日志不得包含 Secret 或未经授权的外部 Payload。
- Phase 1 Hook 不得修改 `SOURCE`、`APPROVED`、`CANONICAL`、Git Tag 或远端状态。
