# Concurrency Policy

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`（`PAOS-016`）

## 最小协议

- 一个复杂任务对应一张 Task Card。
- Task Card 必须声明 Owner、Read Set、Write Set 和 Dependencies。
- 读取型任务可以并行。
- 写入型任务必须检查 Write Set 是否冲突。
- 同一 Canonical 文件只允许一个 Owner 修改。
- 实现阶段的并行写入使用独立 branch 与 Git Worktree。
- 普通任务默认不得直接修改 `main`、merge、tag 或执行 Promotion。

## Direct Main 小修订例外

只有同时满足以下条件，才可以直接修改本地 `main`：

- Founder 在当前任务中明确授权直接修改 `main`。
- 变更属于明显事实纠错、状态一致性、小范围文档或低风险配置修订。
- Write Set 明确且没有并发写入冲突。
- 变更可通过 Git 完整回滚，并在提交前执行适用验证。
- Task Card 记录采用例外的理由与验收标准。

涉及复杂功能、架构迁移、重叠写入、高风险自动化或不可逆动作时，仍必须使用独立 branch/worktree。Direct Main 授权只适用于本地仓库，不自动授权 commit 之外的 Tag、Push、Release Approval、Promotion 或外部部署。

## 冲突处理

发生写入重叠、决策矛盾或 Schema 不一致时，任务转为 `BLOCKED` 或 `REVIEW`，交回总控任务处理。
