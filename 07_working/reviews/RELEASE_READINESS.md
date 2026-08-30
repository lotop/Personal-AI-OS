# V1.1 Minimum Release Readiness

> 状态：`WORKING`
>
> 审计模型：`M1–M6`

当前机器入口：`05_harness/release_audit.py`。

| Gate | 当前预期 | 说明 |
|---|---|---|
| M1 Repository | `BLOCKED_WHILE_EDITING` | 冻结并提交实施 Diff 后复核 |
| M2 Validation | `VERIFY_AFTER_CHANGE` | 使用统一 `ci_gate.py` |
| M3 Template & Factory | `BLOCKED` | 等待 Template Approval 与 Formal E2E |
| M4 Adapter & Deployment | `PASS_EXPECTED` | Codex Live PASS；Gemini Conditional Config PASS |
| M5 Recovery | `STALE` | 必须对冻结 Release Commit 重跑 |
| M6 Founder Release Approval | `BLOCKED` | 尚无固定 Commit 的 Release Approval |

Tag、Canonical Promotion 与发布后验证是 M6 之后的授权动作，不属于发布前 Gate。

## 历史模型

G0–G10 与 R0–R12/P1–P2 是 PAOS-007 之前的历史模型。对应 V2 文件保留并标记 `ARCHIVED/SUPERSEDED`，不再参与 CI 或当前 Readiness 判断。
