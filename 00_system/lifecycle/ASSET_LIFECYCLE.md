# Asset Lifecycle Specification

> 状态：`WORKING`

## 两个独立维度

- Artifact Class：描述资产是什么，例如 Source、Rule、Template、Generated、Temp、Cache、Log。
- Maturity State：描述正式程度，例如 Working、Candidate、Approved、Canonical、Superseded、Archived。

Source 保持 Source；从 Source 派生的规则或知识进入 Maturity 流程。Generated 永远记录生成来源，不反向成为 Canonical Authority。

## 生命周期动作

- `CREATE`：记录 Owner、Class、State、来源和版本。
- `PROMOTE`：验证后从 Working/Candidate 进入 Approved/Canonical。
- `SUPERSEDE`：新版本替代旧版本但保留追溯。
- `ARCHIVE`：退出默认上下文加载，仍可恢复。
- `GC_CANDIDATE`：达到保留期，只生成 Dry Run 清单。
- `DELETE`：仅对批准范围执行，并保留删除与恢复记录。

## GC Gate

- Phase 1 只允许 Dry Run。
- Source、Approved、Canonical、Decision、Release Evidence 和未关闭 Task 依赖默认不可删除。
- 删除前必须验证路径、Owner、引用、备份和恢复窗口。
- 通配符、仓库根、用户目录和未解析变量不得成为破坏性目标。
