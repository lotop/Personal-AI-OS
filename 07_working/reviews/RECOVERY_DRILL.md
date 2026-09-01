# Recovery Drill｜V1.2.1 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-09-02`
>
> Source Commit：`ebc1c791ccf9cbba40c4389e1df9c82f320f2dd0`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从固定的 V1.2.1 Release Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同的 Tree Digest V0.2。

## 冷克隆结果

- 命令：`git clone --no-local /Users/lotop/Personal-AI-OS`。
- 恢复 Commit：`ebc1c791ccf9cbba40c4389e1df9c82f320f2dd0`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Path：`06_deployment/recovery_artifacts/v1.2.1.bundle`（本地、Git Ignored）。
- Bundle Head：`ebc1c791ccf9cbba40c4389e1df9c82f320f2dd0`。
- Bundle SHA-256：`e5e2d6e96c4d7c16f9f4a0977b11e075a0d4d5e604d6e0338b49a21d75c9e577`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`ebc1c791ccf9cbba40c4389e1df9c82f320f2dd0`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree Digest Algorithm：`0.2`。
- Tree SHA-256：`bfdc451bff5e022046aaa3b39e2fcd9480d6d0e4dab592d9a8b7a1eda6e57d5f`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和本机保留的离线 Git Bundle 能够恢复；M5 已能直接读取 Artifact、重算 SHA-256、执行 `git bundle verify` 并核对 Head 与 Tree Digest V0.2。尚未证明私有远端、异地 Bundle、全新设备、Secret 重新绑定或大型资产 Object Storage 的恢复。
