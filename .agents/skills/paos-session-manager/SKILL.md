---
name: paos-session-manager
description: 管理 Personal AI OS 的会话命名、任务状态建议与条件式 Session Close。当用户要求新任务开工、会话起名或重命名、同步任务状态、处理阻塞、执行 Session Close、任务收尾或整理多 Agent 任务窗口时使用。标题只用于检索；只有满足验收条件且当前任务授权写入时，才更新 Task Registry 或持久化知识。
---

# PAOS Session Manager

遵循 `00_system/conversations/SESSION_PROTOCOL.md`。本 Skill 状态为 `WORKING`，不自行产生 Canonical Authority，也不执行 Tag、Push、Release Approval 或 Promotion。

## 权限边界

- 窗口标题是检索标签，不是 Task、Decision、Memory 或 Project State 的事实来源。
- 标题建议与 Registry 写入必须分开；只有当前任务明确授权写入且证据充分时才修改账本。
- 非简单任务先建立 Task Card，再登记或更新 Task Registry。
- Session Close 只生成交接与沉淀候选，不自动批准 Decision、Memory 或 Canonical 内容。
- 若当前环境不能直接重命名窗口，只提供建议，不声称已完成重命名。

## 命名

使用四段式建议：

```text
项目简称 ｜ CHAT/WORK/REVIEW ｜ 具体主题 ｜ 状态
```

状态候选为 `进行中`、`待确认`、`已阻塞`、`已完成`、`已归档`。Task ID 单独保存在 Task Card/Registry 中，不替代项目简称。

示例：`PAOS ｜ WORK ｜ 修正会话管理技能 ｜ 进行中`

## 会话初始化

1. 识别项目简称、Mode、具体主题与当前状态。
2. 给出简洁标题建议；有可用任务管理工具且用户要求时，可直接重命名。
3. 仅在实际存在非简单任务、Write Set 包含账本且已获授权时登记 Task。
4. 不以“已生成标题”为由声称 Task Card 或账本已经同步。

## 状态同步

- 等待用户决策或外部答复时，建议 `待确认`，记录 Decision Needed。
- 存在无法继续的依赖或权限缺口时，建议 `已阻塞`，记录 Blocker 与恢复条件。
- Registry 更新必须引用实际证据；不得预填未来验证、Approval 或 Tag。

## Session Close

仅在下列情况之一发生时要求 Close：

- 工作需要交给另一 Agent、Owner、Worktree 或设备；
- 任务阻塞、等待关键批准或进入较长暂停；
- 会话即将压缩或归档，且有需持久化的结论；
- 产生了应进入 Decision 或 Memory 流程的长期结论。

简短答疑、连续阶段工作和无持久化价值的简单完成不强制 Close。

Close 至少记录 Objective、实际 Scope、Completed、Changed Files、Validation、Open Risks、Decision/Memory Candidates、Next Owner/Next Step。需要真实交接时再生成 Handoff。

## DONE 门槛

只有同时满足以下条件，才可建议或在已授权账本中写入 `DONE`：

1. Acceptance Criteria 已满足；
2. 验证证据已记录；
3. 没有未解决 Blocker 或 Decision Needed；
4. 当前 Task Owner 具有对应 Write Set 与状态更新权限。

否则使用 `REVIEW`、`BLOCKED` 或保持当前状态。用户口头表示“做完了”只触发收尾核验，不自动越过上述门槛。
