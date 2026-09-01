# Recovery Drill｜V1.1.3 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-09-01`
>
> Source Commit：`24de865651a7064c536bb7d223791c38db9af237`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从固定的 V1.1.3 Release Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch main`。
- 恢复 Commit：`24de865651a7064c536bb7d223791c38db9af237`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Path：`06_deployment/recovery_artifacts/v1.1.3.bundle`（本地、Git Ignored）。
- Bundle Head：`24de865651a7064c536bb7d223791c38db9af237`。
- Bundle SHA-256：`183952c02367ca13347a3d920c03ebfb65c1464eb6119a7135fb2eaf218560fb`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`24de865651a7064c536bb7d223791c38db9af237`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`b65993d552bc976331d9fa984842025121662ec4bcf9beaadfe6480b926082d8`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和本机保留的离线 Git Bundle 能够恢复；M5 已能直接读取 Artifact、重算 SHA-256、执行 `git bundle verify` 并核对 Head。尚未证明私有远端、异地 Bundle、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
