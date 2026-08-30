# Validators

- `validate_repository.py`：仓库、Schema、生命周期、Template Pack 与 Adapter 一致性。
- `tree_digest.py`：对 Git tracked working tree 生成确定性 SHA-256。
- `ci_gate.py --profile local-offline`：统一运行全部本地、无网络验证。
- `ci_gate.py --profile release-readiness`：在本地验证后要求 R0–R12 全部通过；Blocked 返回 exit code `14`。

统一约定：`0=PASS`、`10=LOCAL_VALIDATION_FAIL`、`14=READINESS_BLOCKED_OR_STALE`。外部授权缺失不得记录为 PASS，也不得由本地 profile 触发外发。

> 状态：`WORKING`

`validate_repository.py` 提供当前可执行的最小验证，包括：

- 必需目录和入口文件。
- TOML 与 JSON 解析。
- Registry Stable ID 唯一性。
- Task 状态合法性和多维进度字段。
- 资产类别与成熟度分离。
- 高置信度 Secret 模式。
- 未跟踪 Git 文件和远端配置提示。

Schema、完整悬空引用、Adapter Provenance 和跨 Worktree Write Set 冲突将在后续版本加入。
