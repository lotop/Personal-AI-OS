# Memory Pipeline Specification

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 分层

- `L1 Personal Memory`：跨项目稳定偏好、长期目标和协作方式。
- `L2 Project Memory`：项目目标、架构、决定、状态、关键约束和已验证知识。
- `L3 Session Memory`：本次任务的临时上下文、假设和 Working Notes。

## 流程

`Conversation/Source → Extract → Classify → Deduplicate → Verify → Candidate → Approve → Publish → Review/Expire`

## 入库条件

长期 Memory 必须满足：

- 对未来任务持续有用。
- 来源和适用范围明确。
- 区分事实、偏好、假设和待验证事项。
- 不含 Secret、无关敏感信息或大段可重新获取的 Source。
- 与现有 Memory 无未处理冲突。

## Claim Contract

每条可持久化 Claim 必须单独记录：

- `claim_id`、`claim_type = FACT | PREFERENCE | DECISION | INFERENCE`。
- `memory_layer = L1 | L2 | L3`。
- L2 必须有 `project_id`；L3 必须有 `session_id`。
- `source_revision`、`source_locator`、`source_sha256`、`source_author`、`observed_at`、`extractor_version`。
- `governance_status`、`validity_status`、`lifecycle_status` 三条独立状态轴。
- `review_at` 或明确的复核条件；时效性事实不得无限期有效。

`confidence` 只描述不确定程度，不能代替 Claim Type、来源或验证状态。

## 隔离规则

- 跨项目读取默认 `SCOPE_DENIED`，不得在找不到 Project Memory 时 fallback 到其他项目。
- L1 只能保存跨项目稳定且已确认的偏好/原则，不保存业务项目事实。
- 更正、撤回、争议和过期保留 supersedes/retracted_by 证据；过期不自动删除。

## 更新规则

- 新信息默认形成 Candidate，不直接覆盖现有条目。
- 稳定偏好变化时保留 Superseded 关系和生效日期。
- 项目状态信息必须设置复核条件或过期时间，避免陈旧状态伪装为事实。
- Conversation Summary 只是提取输入，不自动等同于 Memory。

## Session Close 输出

Session Close 只提取：Completed、Decisions、Open Questions、Risks、Next Actions、Memory Candidates、Files 与 Validation Evidence。无长期价值的过程推理不进入 Memory。

每个 Close 还必须有 `close_id`、`close_sequence`、`session_id`、`source_set_sha256`、`close_status` 和 `extractor_version`；重复执行必须能识别同一 Source Set，不重复创建 Memory Claim。
