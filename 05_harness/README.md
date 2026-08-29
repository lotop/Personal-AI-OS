# Harness

> 状态：`WORKING`

Harness 负责让任务可靠完成，不负责定义项目事实。

共同最小协议候选：`Understand → Plan → Execute → Validate → Review → Handoff → Cleanup`。

当前说明文件采用一级结构：`WORKFLOWS.md`、`VALIDATORS.md`、`HOOKS.md`、`MIGRATIONS.md`、`RECOVERY.md`、`HANDOFFS.md` 和 `RELEASE_GATES.md`。只有出现真实实现文件时才建立对应子目录。

当前可执行工具：

- `validate_repository.py`：仓库、Schema、状态和 Secret 检查。
- `generate_adapters.py`：确定性生成 Codex 与 Gemini CLI Adapter。
- `release_audit.py`：输出机器可读的 V1.1 Gate 状态，不执行 Promotion。
