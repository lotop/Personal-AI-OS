# V1.1 Release Gates

> 状态：`WORKING`

| Gate | 准入条件 | 必需证据 |
|---|---|---|
| G0 Repository | 唯一仓库、干净 Commit、可定位版本 | Git Commit、Repo Identity |
| G1 Inventory | 发布文件全部登记 | Artifact/Registry Report |
| G2 Schema | 强制 Schema 与格式通过 | Validator Output |
| G3 Boundary | 无 Source/Generated/Canonical 越界 | Provenance Review |
| G4 Templates | 核心模板逐项批准 | Decision Records |
| G5 Factory | 能创建并验证独立项目 | Factory E2E Evidence |
| G6 Adapters | Required Agent Adapter 生成一致 | Generator Check |
| G7 Deployment | Dry Run、部署、幂等与回滚通过 | Deployment Evidence |
| G8 Recovery | 干净恢复演练成功 | Recovery Report |
| G9 Approval | Founder 批准发布范围与例外 | Release Decision |
| G10 Promotion | 指定 Commit、Tag 与 Manifest 一致 | Release Tag/Manifest |

所有 Mandatory Gate 必须 `PASS`；`WARN` 需要带 Owner、期限和 Founder Approval 的 Waiver。存在 `FAIL` 或 `BLOCKED` 时不得宣布 V1.1 Release。
