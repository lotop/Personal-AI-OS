# Hook Implementations

> 状态：`WORKING`

本文件定义 Hook implementations 的候选边界。当前不包含启用中的 Hook；出现真实 scripts 和 tests 时再建立 `hooks/` 子目录。

所有实现必须遵循 `00_system/governance/HOOKS_POLICY.md`，并在 `02_registry/hooks.toml` 登记。

当前 Registry 已完整登记 Matcher、Scope、权限、副作用、幂等键、超时、失败/重试策略、日志范围与 Owner；这些记录只描述禁用状态下的候选合同，不代表脚本已经实现或通过 Runtime 验证。
