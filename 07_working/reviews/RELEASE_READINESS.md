# V1.1 Release Readiness

> 状态：`WORKING`
>
> 审计日期：`2026-08-30`

## Legacy G0–G10 Snapshot

以下表格保留为重构前历史快照，不再代表当前 Gate 模型。

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Repository | `PASS` | Git Baseline 与干净工作区已建立 |
| G1 Inventory | `PASS` | Git 文件清单可读取 |
| G2 Schema | `PASS` | 仓库验证器通过 |
| G3 Boundary | `PASS` | Adapter 与部署文件无漂移 |
| G4 Templates | `BLOCKED` | 核心模板尚未逐项批准 |
| G5 Project Factory | `BLOCKED` | 没有 Approved Template Pack 正式验收 |
| G6 Adapters | `PASS` | 生成一致性通过 |
| G7 Deployment | `BLOCKED` | Codex Runtime Smoke 已通过；Gemini CLI 等待项目内容外发授权 |
| G8 Recovery | `PASS` | 本地干净克隆恢复通过 |
| G9 Founder Approval | `BLOCKED` | 尚无 V1.1 Release Approval |
| G10 Promotion | `BLOCKED` | 未建立 Release Tag |

## 结论

当前总体状态：`BLOCKED`。系统已经具备继续实施与 Candidate 部署的质量基础，但不得宣布 V1.1 Release 或 Canonical Promotion。

## 当前 R0–R12 Readiness

当前机器入口：`05_harness/release_audit_v2.py`。

| Gate | 状态 | 限定范围 |
|---|---|---|
| R0 Review Pack | `PASS` | Founder Review Pack 已生成 |
| R1 Repository | `PASS_AFTER_COMMIT` | 当前修改提交并保持 clean 后复核 |
| R2 Inventory | `PASS_SCOPED` | Git tracked inventory |
| R3 Schema | `PASS` | 含 Candidate Pack Schema binding |
| R4 Invariants | `PASS_SCOPED` | 当前已实现不变量，不声称覆盖完整 |
| R5a Template Structure | `PASS` | Candidate Pack 结构与登记完整 |
| R5b Template Approval | `BLOCKED` | 等待 Founder Approval |
| R6a Factory Safety | `PASS` | 含事务回滚负向测试 |
| R6b Provisional E2E | `PASS` | 仅 Candidate/Provisional |
| R6c Formal E2E | `BLOCKED` | 依赖 R5b |
| R7a Adapter Generation | `PASS` | Byte consistency |
| R7b Codex Live | `PASS` | Readonly runtime smoke |
| R7c Gemini Config | `PASS` | Config load only |
| R7d Gemini Live | `BLOCKED_EXTERNAL_DATA_AUTHORIZATION` | 未发送项目内容 |
| R8 V1.0 Disposition | `BLOCKED_FOUNDER_DECISION` | 原件不可得 |
| R9 Recovery | `STALE` | 历史 Clean Clone/Bundle 仍有效，但需对冻结 Release Commit 重跑 |
| R10 Local Security | `PASS_SCOPED` | Secret pattern、权限与外发策略 |
| R11 Test Assurance | `PASS_SCOPED` | 本地 22 项测试；仍有后续扩展项 |
| R12 Release Approval | `BLOCKED_FOUNDER_DECISION` | 尚未冻结 release commit |

`P1 Tag/Canonical Promotion` 与 `P2 Post-promotion Verification` 是 R12 之后的执行阶段，当前分别为 `NOT_AUTHORIZED` 和 `NOT_STARTED`，不再被错误计作发布前 readiness blocker。
