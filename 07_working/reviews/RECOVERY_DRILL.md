# Recovery Drill｜V1.1.1 Candidate

> 状态：`WORKING_EVIDENCE`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`f67ce69b90288aed00a84999cadaa7aa15a8bdc1`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.1 Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含候选分支的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch codex/v1.1.1-consistency`。
- 恢复 Commit：`f67ce69b90288aed00a84999cadaa7aa15a8bdc1`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`f67ce69b90288aed00a84999cadaa7aa15a8bdc1`。
- Bundle SHA-256：`be89581bef14fa6f653d22244afb0efe3c567397d7942159957c00381ec8a740`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`f67ce69b90288aed00a84999cadaa7aa15a8bdc1`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`fb4c3d2aeccfa223e13f469ebb8b3619486d4f9a64cd0b9832252bd764a292a3`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
