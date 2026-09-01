# Hook Implementation Boundary

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-019`

本文件定义 Hook implementation 的已批准安全边界。当前实现数量为 `0`，启用数量为 `0`；本次批准不代表任何 Hook 已实现、已加载、已信任或通过 Runtime 验证。

所有实现必须遵循 `00_system/governance/HOOKS_POLICY.md`，并在 `02_registry/hooks.toml` 登记。

当前 Registry 登记平台、实现状态、Config Load、Runtime Test、Matcher、Scope、权限、副作用、幂等键、超时、失败/重试策略、日志范围与 Owner；它保持 `WORKING` 且全部 `enabled = false`。不同平台同名事件不得视为相同实现。

Hook 只是 Guardrail，不替代平台 Sandbox、Approval、Personal AI OS Governance 或权限系统。未由平台官方能力与 Runtime Evidence 覆盖的工具路径，不得宣称已经被 Hook 阻止。

未经 Founder 独立启用授权，不得生成或部署项目 Hook 配置、执行 Trust、启用 Hook、采集 Conversation/Secret 或新增外部传输。
