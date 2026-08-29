# Mode System Specification

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 定位

Mode 是任务执行策略，不是 Agent、权限、知识库或项目事实来源。每项复杂任务只有一个 `primary_mode`，最多一个 `supporting_mode`。

## Mode 候选

| Mode | 主要产出 | 默认写入 |
|---|---|---|
| `CHAT` | 澄清、解释、短答 | 无或 Conversation |
| `BRAINSTORM` | 多个候选方向 | Working |
| `RESEARCH` | 来源、证据、结论与未知项 | Working Research |
| `STRATEGY` | 决策选项、假设、风险与 Gate | Working/Candidate |
| `PRODUCT` | PRD、用户流程、验收标准 | Working/Candidate |
| `CODING` | 实现、测试与变更记录 | Task Write Set |
| `REVIEW` | 缺陷、风险、证据与建议 | 默认只读 |

## 进入条件

- Objective、Scope 和预期输出明确。
- 当前 Mode 与任务产出匹配。
- 需要写入时已经声明 Write Set 与权限。
- 高风险任务已经确认审批边界。

## 上下文加载

按 Manifest First 顺序加载：

1. Global Governance 与 Security 中直接适用的规则。
2. 当前 Mode Contract。
3. 当前项目入口、Decisions 与 Project Memory。
4. 当前 Task Card。
5. 与 Read Set 直接相关的 Source 与文件。

不得默认加载全部 Modes、全部项目、完整历史或 Archive。Context Manifest 应记录加载文件、版本、原因和估算大小。

## 退出条件

- 产出满足 Acceptance Criteria 或明确进入 Blocked。
- 验证与 Review 已完成。
- 需要的 Handoff、Decision Candidate 与 Memory Candidate 已生成。
- Working、Temp、Cache 和 Logs 已按生命周期处理。

`REVIEW` 发现问题后不得在同一只读阶段静默修复；需要切换到具有写入权限的 Task/Mode。
