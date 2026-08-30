# Recovery Drill｜V1.1.1 Candidate

> 状态：`WORKING_EVIDENCE`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`6d006739ac15e20f059b675606749abfa82bf2ea`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.1 Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含候选分支的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch codex/claude-code-support`。
- 恢复 Commit：`6d006739ac15e20f059b675606749abfa82bf2ea`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`6d006739ac15e20f059b675606749abfa82bf2ea`。
- Bundle SHA-256：`cf6269bcf6283df14b865ed3a18ae87a85066107e1da42da7335fa142bd6f17b`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`6d006739ac15e20f059b675606749abfa82bf2ea`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`f85643421f406f16e34b24ff62e5e7b705c9f5ad41a00e4bc24abe664401c743`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
