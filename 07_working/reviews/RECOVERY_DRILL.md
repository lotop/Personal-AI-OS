# Recovery Drill｜V1.1.2 Approved Local Release

> 状态：`APPROVED`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`2e83648615ff486dec748b47642079b3f5f0efc4`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.2 Release Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch main`。
- 恢复 Commit：`2e83648615ff486dec748b47642079b3f5f0efc4`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`2e83648615ff486dec748b47642079b3f5f0efc4`。
- Bundle SHA-256：`2f1e0d17b1ce0ca2d0dc6582288dc8668982ea9cd6c0cce64d77198c048dec19`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`2e83648615ff486dec748b47642079b3f5f0efc4`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`41c6844a31c32a3dbfa95afd142eb69dac132714c9417253495d37aa5e4e723f`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
