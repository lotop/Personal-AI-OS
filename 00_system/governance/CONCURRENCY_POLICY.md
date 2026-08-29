# Concurrency Policy

> 状态：`WORKING`

## 最小协议

- 一个复杂任务对应一张 Task Card。
- Task Card 必须声明 Owner、Read Set、Write Set 和 Dependencies。
- 读取型任务可以并行。
- 写入型任务必须检查 Write Set 是否冲突。
- 同一 Canonical 文件只允许一个 Owner 修改。
- 实现阶段的并行写入使用独立 branch 与 Git Worktree。
- 普通任务不得直接修改 `main`、merge、tag 或执行 Promotion。

## 冲突处理

发生写入重叠、决策矛盾或 Schema 不一致时，任务转为 `BLOCKED` 或 `READY_FOR_REVIEW`，交回总控任务处理。
