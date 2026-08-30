# Conversation Naming and Session Close

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## Conversation Naming

建议格式：

`项目简称｜工作流或 Mode｜具体主题｜状态`

状态候选：`进行中`、`待确认`、`已完成`、`已阻塞`、`已归档`。标题用于检索，不作为正式项目状态来源。

## Session Close 触发

仅在以下任一情况发生时要求 Session Close：

- 切换 Agent、任务 Owner、Worktree 或设备。
- 进入 Blocked、等待审批或长时间暂停。
- 即将压缩上下文或归档 Conversation，且存在未沉淀的重要结论。
- 形成需要进入 Decision、Project Knowledge 或长期 Memory 的结论。

普通短答、连续工作中的阶段更新和无持久结论的任务不要求 Close 文件。

## 必需内容

- Objective 与实际 Scope。
- Completed 与未完成事项。
- Decisions 与待确认事项。
- Files、Commit、Branch 与 Worktree。
- Validation Evidence。
- Risks、Blockers 与 Next Actions。
- Memory Candidates 与不应进入 Memory 的过程信息。

Session Close 是 Handoff 输入，不自动成为 Decision、Memory 或 Canonical Project State。

自动化批量 Close 可以增加 Close ID、Sequence、Source Set SHA-256 与 Extractor Version；这些字段不作为人工 Close 的强制要求。
