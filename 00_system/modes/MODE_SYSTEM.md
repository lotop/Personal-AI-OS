# Mode System Specification

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`（`PAOS-017`）

## 定位

Mode 只描述当前交互的行为边界，不是 Agent、权限、知识库、执行阶段或项目事实来源。V1.1 Minimum 不记录 Mode 切换历史，也不使用多轴 Mode 状态机。

## 正式 Modes

| Mode | 主要产出 | 默认写入 |
|---|---|---|
| `CHAT` | 澄清、解释、短答 | 无或 Conversation |
| `WORK` | 规划、研究、实施、验证与交付 | Task Write Set |
| `REVIEW` | 缺陷、风险、证据与建议 | 默认只读 |

研究、策略、产品、编码和头脑风暴属于任务标签或 Skill，不属于需要持久化的 Mode。

## 进入条件

- Objective、Scope 和预期输出明确。
- 需要写入时已经声明 Write Set 与权限。
- 高风险任务已经确认审批边界。

## 上下文加载

按 Manifest First 顺序加载：

1. Global Governance 与 Security 中直接适用的规则。
2. 当前 Mode。
3. 当前项目入口、Decisions 与 Project Memory。
4. 当前 Task Card。
5. 与 Read Set 直接相关的 Source、Knowledge 与文件。

不得默认加载全部 Modes、全部项目、完整历史或 Archive。Context Manifest 应记录加载文件、版本、原因和估算大小。

## 继承与冲突顺序

运行平台强制政策与安全边界始终优先。项目内按：`Global Security/Governance → Approved Project Rules → Current Task Card → Agent Defaults` 合成；Founder 当前指令可调整任务，但不能被解释为自动批准、外部数据授权或不可逆操作授权，除非指令明确覆盖该操作。

任何影响权限、Source of Truth、Write Set、外部传输或正式交付物的冲突必须 Fail Closed，并生成 Conflict/Decision Needed；普通输出风格冲突可采用更具体的当前 Task Card。

## 行为切换

- 从 `REVIEW` 转为写入型 `WORK` 时必须建立或更新 Task Card。
- 行为切换不自动扩大 Write Set、网络权限或 Approval Scope。
- 短答和澄清不需要持久化当前 Mode。

## 退出条件

- 产出满足 Acceptance Criteria 或明确进入 Blocked。
- 验证与 Review 已完成。
- 适用时生成 Handoff、Decision 或 Memory Candidate。
- Working、Temp、Cache 和 Logs 已按生命周期处理。

`REVIEW` 发现问题后不得在同一只读阶段静默修复；需要切换到具有写入权限的 Task/Mode。
