# Conflict Resolution

> 状态：`WORKING`

## 冲突类型

- 目标或范围冲突。
- Source of Truth 冲突。
- Schema、状态或命名冲突。
- Write Set 或文件 Owner 冲突。
- 平台能力与通用规则冲突。
- 当前用户指令与历史决策冲突。

## 处理流程

1. 停止有冲突的正式写入或 Promotion。
2. 保留双方 Source、版本和上下文，不静默合并。
3. 记录影响文件、决定点、风险和可逆选项。
4. 技术兼容问题由总控评审；影响目标、权限或事实的问题由 Founder 决定。
5. 决定后更新 Decision、Migration 和相关 Registry。

自动化只能识别和阻断冲突，不得自行替代 Founder 选择。
