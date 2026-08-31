# Validators

- `validate_repository.py`：仓库、Schema、生命周期、Template Pack 与 Adapter 一致性。
- `tree_digest.py`：对 Git tracked working tree 生成确定性 SHA-256。
- `ci_gate.py --profile local-offline`：统一运行全部本地、无网络验证。
- `ci_gate.py --profile release-readiness`：在本地验证后要求 M1–M6 全部通过；Blocked 返回 exit code `14`。

统一约定：`0=PASS`、`10=LOCAL_VALIDATION_FAIL`、`14=READINESS_BLOCKED_OR_STALE`。外部授权缺失不得记录为 PASS，也不得由本地 profile 触发外发。

> 状态：`WORKING`

`validate_repository.py` 提供当前可执行的最小验证，包括：

- 必需目录和入口文件。
- TOML 与 JSON 解析。
- Schema 自身只使用已实现的关键字（未实现关键字直接失败，不静默通过）。
- `bindings.toml` 声明的 Registry / Manifest / Template Pack Schema 校验。
- 已部署 Adapter 与 `03_adapters/` 源文件的字节一致性。
- Registry Stable ID 唯一性。
- Task 单一状态与验证证据格式。
- Skill 与 Hook Owner 必须是已登记 Task；Capability 的版本证据必须与 Runtime Registry 对齐。
- `SYSTEM.toml` 已批准基线与 `02_registry/projects.toml` 本仓库记录的跨文件一致性。
- 资产类别与 V1.1 Minimum 状态集合。
- Template Pack 未登记文件与来源缺失。
- 高置信度 Secret 模式。
- `07_working/reviews/*.md` 的日期字段，以及状态取值必须来自已登记词汇表
  （`states.toml` 的 `maturity_states` 与 `tasks.toml` 的 `allowed_statuses`）。
- 未跟踪 Git 文件和远端配置提示。

完整悬空引用、Adapter Provenance 和跨 Worktree Write Set 冲突将在后续版本加入。
