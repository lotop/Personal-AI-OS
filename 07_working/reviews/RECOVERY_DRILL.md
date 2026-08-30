# Recovery Drill｜V1.1.1 Candidate

> 状态：`WORKING_EVIDENCE`
>
> 执行日期：`2026-08-31`
>
> Source Commit：`e95cf5aee29bcc018454dcac08d5e04301ab482d`
>
> Machine Evidence：`07_working/reviews/recovery_evidence.toml`

## 场景

从冻结的 V1.1.1 Candidate Commit 创建不使用本地对象捷径的冷克隆，并创建只包含候选分支的离线 Git Bundle。两个恢复副本都必须精确恢复同一 Commit、通过本地 CI、通过 Adapter Check，并具有相同 Tree Digest。

## 冷克隆结果

- 命令：`git clone --no-local --branch codex/claude-code-support`。
- 恢复 Commit：`e95cf5aee29bcc018454dcac08d5e04301ab482d`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 离线 Bundle 结果

- Bundle Head：`e95cf5aee29bcc018454dcac08d5e04301ab482d`。
- Bundle SHA-256：`d344631624f57b2e7a642eb88caf707f08cda69b43816b4f602748b86ac4644d`。
- `git bundle verify`：退出码 `0`。
- Bundle 恢复 Commit：`e95cf5aee29bcc018454dcac08d5e04301ab482d`。
- Local Offline CI：`PASS`。
- Adapter Generator `--check`：`ADAPTERS_OK`。
- `git fsck --full`：退出码 `0`。

## 内容一致性

- Source/Cold Clone/Bundle Clone Commit：精确一致。
- Tree SHA-256：`08d1baa9f234a040a372cb18a8a95002373ba3470c82a4fe2194d47ccf499c5e`。
- Machine Evidence 与本报告 Commit、Bundle SHA、Tree SHA：一致。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini Live Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
