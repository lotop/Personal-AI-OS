# Memory Pipeline Specification

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 分层

- `L1 Personal Memory`：跨项目稳定偏好、长期目标和协作方式。
- `L2 Project Memory`：项目目标、架构、决定、状态、关键约束和已验证知识。
- `L3 Session Memory`：本次任务的临时上下文、假设和 Working Notes。

## 流程

`Conversation/Source → Select → Verify → Working → Approve/Discard → Review/Archive`

## 入库条件

长期 Memory 必须满足：

- 对未来任务持续有用。
- 来源和适用范围明确。
- 区分事实、偏好、假设和待验证事项。
- 不含 Secret、无关敏感信息或大段可重新获取的 Source。
- 与现有 Memory 无未处理冲突。

## 最小记录

进入长期 Memory 的记录至少包含：

- 类型：`FACT | PREFERENCE | DECISION | INFERENCE`。
- 层级：L1 或 L2；L2 必须有 `project_id`。L3 属于 Working Notes，不进入长期 Memory Registry。
- 来源定位与观察时间；只有在来源内容可能变化或需要完整性证明时才记录 Revision/Hash。
- 状态：`WORKING | APPROVED | ARCHIVED`。
- 时效性事实的复核时间或复核条件。

`confidence`、`extractor_version`、撤回链等字段按风险选用，不作为每条记录的强制负担。

## 隔离规则

- 跨项目读取默认 `SCOPE_DENIED`，不得在找不到 Project Memory 时 fallback 到其他项目。
- L1 只能保存跨项目稳定且已确认的偏好/原则，不保存业务项目事实。
- 更正、撤回、争议和过期保留 supersedes/retracted_by 证据；过期不自动删除。

## 更新规则

- 新信息默认形成 Working，不直接覆盖现有 Approved 条目。
- 稳定偏好变化时保留 Superseded 关系和生效日期。
- 项目状态信息必须设置复核条件或过期时间，避免陈旧状态伪装为事实。
- Conversation Summary 只是提取输入，不自动等同于 Memory。

## Session Close 输出

发生适用的 Session Close 时，只提取：Completed、Decisions、Open Questions、Risks、Next Actions、Memory Candidates、Files 与 Validation Evidence。无长期价值的过程推理不进入 Memory。

只有自动化批量抽取或审计场景才要求 `source_set_sha256`、`extractor_version` 和幂等键；人工 Session Close 不强制维护这些字段。
