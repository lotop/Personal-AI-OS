# Backup and Recovery

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-020`
>
> 日期：`2026-09-01`

## 最小拓扑

- 本地 Git Repository：主要工作副本。
- Private Git Remote：版本历史灾备副本。
- 加密设备备份：保护未推送 Working 状态和本地配置。
- 版本化 Object Storage：大型资产；Git 只保存 Manifest、逻辑 ID 和校验和。
- Secret Manager 或系统钥匙串：凭据，不进入 Git。

## 候选目标

- MVP `RPO ≤ 24h`。
- MVP `RTO ≤ 4h`。
- 每月执行单文件恢复。
- 每季度执行干净目录或干净设备恢复演练。
- 每半年执行远端不可用或凭据丢失场景演练。

## 恢复 Gate

- 干净克隆能够恢复 Canonical 文件。
- TOML、JSON 和内部引用验证通过。
- Adapter 可以从 Source 重新生成。
- 大型资产校验和一致。
- Secret 引用可重新绑定，但 Secret 值不出现在日志中。
- 恢复演练留下日期、操作者、输入版本、结果和问题清单。

在首次成功恢复演练前，不得宣称系统已经可恢复。

当前已完成本地 Git 干净克隆与离线 Git Bundle 恢复，证据见 `07_working/reviews/RECOVERY_DRILL.md`；Private Remote、全新设备和大型资产恢复仍未验证。

本地正式发布的 Bundle 保存于被 Git 忽略的 `06_deployment/recovery_artifacts/`。机器证据必须记录相对路径与 SHA-256；M5 会读取实际 Artifact、重算 Hash、执行 `git bundle verify` 并核对 Bundle Head。该本地 Artifact 不等于远端或异地备份，Push 也不会携带它。

## V1.2 Recovery Evidence V0.2

- 必须声明 `tree_digest_version = "0.2"`，并绑定冻结 Commit、Commit Tree、Path/Mode/Object Type/Blob Hash Tree Digest、Bundle Relative Path、Bundle SHA-256、Bundle Head 与实际恢复测试。
- 只有全部实现冻结后的新鲜证据才可用于 M5；历史 V1.1.x Evidence 保留原状态，不改写为 V1.2。
- Private Remote、全新设备、大型资产和 Secret 重绑定必须保持 `NOT_TESTED`，直到对应演练完成。

## 恢复包与纯净发行包

Recovery Package 用于恢复固定 Git 历史与证据；Clean Distribution Package 用于给第三方初始化，不含 `.git`、`07_working/`、`08_history/`、开发审计、部署记录、个人 Registry、Cache/Logs/Temp 或本机路径。两者必须由不同 Manifest 与校验和证明，不能互相替代。本规则批准生成/验证边界，不代表当前已经创建 V1.2 Recovery Evidence 或纯净发行包。
