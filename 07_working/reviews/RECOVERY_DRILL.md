# Recovery Drill｜V1.1.2 Working Revision

> 状态：`WORKING_EVIDENCE`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`b352d9031930f7227fe98852ae8e5b060351672d`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.2 Working Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch main`。
- 恢复 Commit：`b352d9031930f7227fe98852ae8e5b060351672d`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`b352d9031930f7227fe98852ae8e5b060351672d`。
- Bundle SHA-256：`b8ced3b58ec33c70c6553627210cde9bd1ce9d9efea6f431260e643aae4bdbd0`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`b352d9031930f7227fe98852ae8e5b060351672d`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`493d74d018145c61f8d6e3f30d35361c89aa00a1c54e6705c082cc1740295ad2`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
