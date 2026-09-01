# Recovery Drill｜V1.2.0 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-09-02`
>
> Source Commit：`65fda3fbfbb0d250694799ff7662ae9286dc5989`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从固定的 V1.2.0 Release Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同的 Tree Digest V0.2。

## 冷克隆结果

- 命令：`git clone --no-local /Users/lotop/Personal-AI-OS`。
- 恢复 Commit：`65fda3fbfbb0d250694799ff7662ae9286dc5989`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Path：`06_deployment/recovery_artifacts/v1.2.0.bundle`（本地、Git Ignored）。
- Bundle Head：`65fda3fbfbb0d250694799ff7662ae9286dc5989`。
- Bundle SHA-256：`5a51f344438e458b6dfa7e60782ba8dc8fb9194d5535df0c1c5bcd2f67bceb46`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`65fda3fbfbb0d250694799ff7662ae9286dc5989`。
- Local Offline CI：`PASS`（8/8 PASS）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree Digest Algorithm：`0.2`。
- Tree SHA-256：`59c157bb0686f492640ca094e762bec6e45b3ad9a37a876da429ad8f7052a1fd`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和本机保留的离线 Git Bundle 能够恢复；M5 已能直接读取 Artifact、重算 SHA-256、执行 `git bundle verify` 并核对 Head 与 Tree Digest V0.2。尚未证明私有远端、异地 Bundle、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
