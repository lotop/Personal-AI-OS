# V1.1 Minimum Release Gates

> 状态：`WORKING`

| Gate | 准入条件 | 必需证据 |
|---|---|---|
| M1 Repository | 唯一仓库、固定 Commit、干净工作区 | Git HEAD |
| M2 Validation | Schema、边界、安全与本地测试通过 | `ci_gate.py` 输出 |
| M3 Template & Factory | Template 已批准且 Formal E2E 通过 | Approval + Factory Evidence |
| M4 Adapter & Deployment | Adapter 无漂移；Codex Smoke 通过；Gemini Conditional Config 通过 | Runtime Registry |
| M5 Recovery | 对冻结 Commit 的恢复演练通过 | Recovery Report |
| M6 Founder Release Approval | Founder 对固定 Commit 和范围作出明确批准 | Release Decision |

六个 Gate 全部 `PASS` 才达到 Release Readiness。Tag、Canonical Promotion 与发布后验证是 M6 之后的授权动作，不计作发布前 Gate，也不会由审计脚本自动执行。
