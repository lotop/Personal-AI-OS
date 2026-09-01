# Asset Lifecycle Specification

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`（`PAOS-016`）

## 两个独立维度

- Artifact Class：描述资产是什么，例如 Source、Rule、Template、Generated、Temp、Cache、Log。
- State：V1.1 Minimum 只使用 `WORKING`、`APPROVED`、`ARCHIVED`。

Source 保持 Source；从 Source 派生的规则或知识可由 Working 进入 Approved。Generated 永远记录生成来源，不反向成为 Canonical Authority。Canonical Authority 由批准记录、固定 Commit 与 Release Tag 共同证明，不逐文件维护额外状态轴。

## 生命周期动作

- `CREATE`：记录 Owner、Class、State、来源和版本。
- `APPROVE`：经验证和明确批准后从 Working 进入 Approved。
- `REPLACE`：新版本替代旧版本；旧版本进入 Archive 并保留追溯。
- `ARCHIVE`：退出默认上下文加载，仍可恢复。
- `GC_CANDIDATE`：达到保留期，只生成 Dry Run 清单。
- `DELETE`：仅对批准范围执行，并保留删除与恢复记录。

## GC Gate

- Phase 1 默认只允许 Dry Run；Founder 对明确的 Temp/Cache 范围授权后，可以执行可恢复 Quarantine，但仍不得永久删除。
- Source、Approved、Canonical、Decision、Release Evidence 和未关闭 Task 依赖默认不可删除。
- 删除前必须验证路径、Owner、引用、备份和恢复窗口。
- 通配符、仓库根、用户目录和未解析变量不得成为破坏性目标。

GC Dry Run 必须生成 immutable `gc_plan`，至少包含 Plan ID、Policy Version、生成时间、过期时间、目标真实路径、当前 Hash、引用扫描结果、Hold、恢复截止日和逐项 Reason Code。执行前必须重新校验 Hash、引用、Hold 与 Policy Version；任一变化都使 Plan 变为 `STALE`。

Quarantine/Trash 必须使用固定隔离位置，记录原路径、移动后 Hash、访问权限和恢复截止日，并从普通上下文加载与下一轮 GC 扫描中排除。Retention 必须为每类资产解析出唯一值，执行器不得在 min/max 区间中自行选择。V1.1.2 清理器只接受 `.DS_Store`、`__pycache__`、`*.pyc` 与 `99_temp/` 中非保护项。
