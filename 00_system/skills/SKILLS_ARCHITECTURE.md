# Skills Architecture

> 状态：`WORKING`

## 定位

Skill 是按需加载的可复用工作协议，不是常驻系统提示，也不自动获得额外权限。

## Registry 字段要求

- Stable ID、名称、版本和 Owner。
- 触发条件与明确 Non-goals。
- Source、安装位置和完整性信息。
- 支持的平台与 `NATIVE/ADAPTER/MANUAL/UNSUPPORTED/UNVERIFIED` 状态。
- 所需权限、网络、工具和外部依赖。
- 输入、输出、测试、失败方式和卸载路径。

## 生命周期

`DISCOVERED → REVIEWED → CANDIDATE → TESTED → APPROVED → ENABLED → DEPRECATED → ARCHIVED`

Skill 更新不得静默改变权限、网络访问、外部写入或破坏性行为。跨 Agent 复用时保持核心协议一致，平台入口与原生格式由 Adapter 处理。
