# Handoffs

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-019`

Handoff 只在跨 Owner、跨 Agent、跨 Worktree、跨设备或长时间暂停后需要他人恢复工作时要求。普通任务完成不强制生成独立 Handoff 文件。

最低证据：Task ID、Objective、当前 Commit/Branch、Files、Completed、Remaining、Validation、Risks、Blockers、Decision Needed 和下一步入口。只有并行写入或发生冲突时才强制列出完整 Read/Write Set 与 Base/Head Commit。

没有 Commit 的临时工作必须明确列出未提交文件；聊天摘要不得替代 Git 与文件证据。
