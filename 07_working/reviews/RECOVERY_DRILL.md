# Recovery Drill

> 状态：`WORKING`
>
> 执行日期：`2026-08-30`
>
> Source Commit：`d544eb345f6ad83754149e8aea097e2e742eda0c`

## 场景

从本地 Git Repository 创建不使用本地对象捷径的干净克隆，验证仓库内容、测试、Adapter 再生成能力与工作区完整性。

## 结果

- `git clone --no-local`：通过。
- 恢复 Commit：与 Source Commit 一致。
- Project Factory、Schema、Deployment 共 11 项测试：通过。
- Adapter Generator `--check`：通过。
- Repository Validator：`0 errors / 0 warnings`。
- 恢复后 Git Working Tree：干净。

## 离线 Git Bundle 演练

- Bundle Source Commit：`ed1ba5f2d65e2f26c01620b0d769b80b41adf88c`。
- `git bundle verify`：通过，确认包含 `main`、`HEAD` 和完整历史。
- Bundle SHA-256：`12df48dca6d66df7bf2808214246b65819e31645106f52385250196f356b42b3`。
- 从 Bundle 克隆：通过。
- 恢复后 Commit：与 Source Commit 一致。
- 11 项测试、Adapter Check 和 Repository Validator：全部通过。
- 恢复后 Working Tree：干净。

结论：`PASS`

## 边界

本次证明本地 Git 历史和离线 Git Bundle 能够恢复；尚未证明私有远端、全新设备、Gemini CLI Runtime、Secret 重新绑定或大型资产 Object Storage 的恢复。
