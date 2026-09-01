# Recovery Drill｜V1.2.2 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-09-02`
>
> Source Commit：`3a08232e78138f77a7106d9abbeec9cd46dd5939`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从固定的 V1.2.2 Release Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同的 Tree Digest V0.2。

## 冷克隆结果

- 命令：`git clone --no-local /Users/lotop/Personal-AI-OS`。
- 恢复 Commit：`3a08232e78138f77a7106d9abbeec9cd46dd5939`。
- Local Offline CI：`PASS`（9 项检查无 FAIL）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Path：`06_deployment/recovery_artifacts/v1.2.2-3a08232e.bundle`（本地、Git Ignored）。文件名内嵌 Tested Commit 前缀，V1.2.1 的 `v1.2.1-c8e3ecc0.bundle` 原样保留，未被覆盖。
- Bundle Head：`3a08232e78138f77a7106d9abbeec9cd46dd5939`。
- Bundle SHA-256：`66f079f8c8f8b21d1debd7d2181928a62a0ac97970afafe8598774a089b75e5a`。
- `git bundle verify`：退出码 `0`，`The bundle records a complete history`。
- Bundle 恢复 Commit：`3a08232e78138f77a7106d9abbeec9cd46dd5939`。
- Local Offline CI：`PASS`（9 项检查无 FAIL）。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree Digest Algorithm：`0.2`。
- Tree SHA-256：`9aae51fd5614f6f637294321f8f605bcbc0e32d0c3adc4576b01ce9bca31cc8f`（tracked files 210，两个恢复副本一致）。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 说明：两个恢复副本中的 `release-state`

本次 CI 新增的 `release-state` 检查在两个恢复副本中均显示 `BLOCKED`。这是预期结果：克隆不携带 annotated tag，M6 因此无法把 `v1.2.2` 绑定到 HEAD。该项不使 profile 失败，且如实反映"恢复副本本身不是已发布制品"这一事实。

## 边界

本次证明本地 Git 历史和本机保留的离线 Git Bundle 能够恢复；M5 已能直接读取 Artifact、重算 SHA-256、执行 `git bundle verify`、核对 Head 与 Tree Digest V0.2，并强制 Bundle 文件名内嵌 Tested Commit 前缀。尚未证明私有远端、异地 Bundle、全新设备、Secret 重新绑定或大型资产 Object Storage 的恢复。远端 `origin` 只同步 `main`，不含 `v1.1.3` 之后的任何 tag。
