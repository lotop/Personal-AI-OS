# Recovery Drill｜V1.2.1 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-09-02`
>
> Source Commit：`c8e3ecc04a4dbc5a5d4f6995f10e97a9dd6aa42a`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从固定的 V1.2.1 Release Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同的 Tree Digest V0.2。

## 冷克隆结果

- 命令：`git clone --no-local /Users/lotop/Personal-AI-OS`。
- 恢复 Commit：`c8e3ecc04a4dbc5a5d4f6995f10e97a9dd6aa42a`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Path：`06_deployment/recovery_artifacts/v1.2.1-c8e3ecc0.bundle`（本地、Git Ignored）。文件名内嵌 Tested Commit 前缀，避免重复演练原地覆盖上一次物证。
- Bundle Head：`c8e3ecc04a4dbc5a5d4f6995f10e97a9dd6aa42a`。
- Bundle SHA-256：`4fbcc965afabf2727cc199a0a674601621713ce1c3916723942616b9e15bcf98`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`c8e3ecc04a4dbc5a5d4f6995f10e97a9dd6aa42a`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree Digest Algorithm：`0.2`。
- Tree SHA-256：`fc974fecf69c5ba29b16f71ca25e34427282631740b8fbc6156d92b66659a848`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和本机保留的离线 Git Bundle 能够恢复；M5 已能直接读取 Artifact、重算 SHA-256、执行 `git bundle verify` 并核对 Head 与 Tree Digest V0.2。尚未证明私有远端、异地 Bundle、全新设备、Secret 重新绑定或大型资产 Object Storage 的恢复。
