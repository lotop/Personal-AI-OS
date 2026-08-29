# Backup and Recovery

> 状态：`WORKING`

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
