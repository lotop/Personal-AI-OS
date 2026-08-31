# Recovery Drill｜V1.1.2 Working Revision

> 状态：`WORKING_EVIDENCE`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`d4bbb3d378ba6b534f8039e9d5124a5a5a25cc67`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.2 Working Commit 创建不使用本地对象捷径的冷克隆，并创建只包含本地 `main` 的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch main`。
- 恢复 Commit：`d4bbb3d378ba6b534f8039e9d5124a5a5a25cc67`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`d4bbb3d378ba6b534f8039e9d5124a5a5a25cc67`。
- Bundle SHA-256：`1256e388795989b89a5e89d3d6fce5f492a3e2584e02f97cad239db18132f24a`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`d4bbb3d378ba6b534f8039e9d5124a5a5a25cc67`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`d0e5fc2b380de8962e3f0b9258ed03ea57ef7d5f6fb8478317b18a138e4a03c2`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
