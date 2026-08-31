# V1.1 Minimum Release Gates

> 状态：`WORKING`

| Gate | 准入条件 | 必需证据 |
|---|---|---|
| M1 Repository | 唯一仓库、固定 Commit、干净工作区 | Git HEAD |
| M2 Validation | Schema、边界、安全与本地测试通过 | `ci_gate.py` 输出 |
| M3 Template & Factory | Template 已批准且 Formal E2E 通过 | Approval + Factory Evidence |
| M4 Adapter & Deployment | Adapter 无漂移；Codex Smoke 通过；Gemini Conditional Config 通过 | Runtime Registry |
| M5 Recovery | 对冻结 Commit 的恢复演练通过，且 Bundle Artifact 可定位、Hash 一致并通过 `git bundle verify` | Recovery Report + Machine Evidence + Local Bundle Artifact |
| M6 Founder Release Approval | Founder 对固定范围作出明确批准，annotated tag 将最终 Release Commit、版本与 Approval Reference 直接绑定 | Release Decision + Annotated Tag |

六个 Gate 全部 `PASS` 才达到 Release Readiness。Tag、Canonical Promotion 与发布后验证是 M6 之后的授权动作，不计作发布前 Gate，也不会由审计脚本自动执行。

`approved_baseline` 不记录 `release_commit`：Git Commit 不能在自身 Tree 中可靠声明自身 Hash。最终 Commit 由 annotated tag 的目标对象证明；System 只记录版本、Tag 名、Approval Reference 与先于发布证据提交的实现冻结 Commit。
