# Harness

Release Readiness 当前模型使用 `release_audit.py` 与 `release_gates.toml`，只包含六个 Minimum Gate。历史的 R0-R12/P1-P2 模型入口已归档到 `09_archive/v1.1-release-gates-v2/`，不参与运行。

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-019`

Harness 负责让任务可靠完成，不负责定义项目事实。

复杂任务至少完成范围确认、实施、验证和交付；Handoff 与 Cleanup 按实际交接和资产风险触发。

当前说明文件采用一级结构：`WORKFLOWS.md`、`VALIDATORS.md`、`HOOKS.md`、`MIGRATIONS.md`、`RECOVERY.md`、`HANDOFFS.md` 和 `RELEASE_GATES.md`。只有出现真实实现文件时才建立对应子目录。

当前可执行工具：

- `validate_repository.py`：仓库、Schema、状态和 Secret 检查。
- `generate_adapters.py`：确定性生成 Codex、Claude Code 与 Gemini CLI Adapter。
- `ci_gate.py`：统一的一键本地验证入口。
- `release_audit.py`：加载 `release_gates.toml`，输出机器可读的六项 Minimum Gate，不执行 Promotion。
- `temp_cleanup.py`：仅对已知 Temp/Cache 生成不可变计划，重验后移动到可恢复 Quarantine；不永久删除。
