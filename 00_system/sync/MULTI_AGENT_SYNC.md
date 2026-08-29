# Multi-Agent Sync Specification

> 状态：`WORKING`

## 原则

- Git Commit、Registry、Decision 和 Task Card 是同步证据；Conversation 不是锁。
- 每个写入任务必须有 Owner、Branch/Worktree 和不重叠 Write Set。
- Agent 之间不共享未记录的隐式状态。
- Canonical Promotion、Merge、Tag 和跨任务冲突由总控处理。

## Handoff Contract

Handoff 必须包含：Task ID、Agent/Runtime、Base Commit、Branch、Write Set、Completed、Remaining、Validation、Known Risks、Required Decision 和下一位 Owner。

## 同步流程

1. 总控分配 Task Card 和 Base Commit。
2. Agent 验证 Read/Write Set 与依赖。
3. 读取工作可并行；写入工作使用独立 Worktree。
4. Agent 提交 Candidate Commit 与 Handoff。
5. 总控执行 Diff、测试、Schema、冲突和来源检查。
6. 合并后更新 Task、Decision、Knowledge 和 Release Evidence。

Adapter 只翻译平台能力；平台缺失的能力必须显式降级为 Manual 或 Unsupported。
