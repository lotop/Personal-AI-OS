# Harness

Release Readiness 新模型使用 `release_audit_v2.py` 与 `release_gates_v2.toml`。旧版 `release_audit.py` 暂时保留作历史兼容，不再用于新的 Founder Review Pack；新版验证通过并获得迁移确认后再移除旧入口。

> 状态：`WORKING`

Harness 负责让任务可靠完成，不负责定义项目事实。

共同最小协议候选：`Understand → Plan → Execute → Validate → Review → Handoff → Cleanup`。

当前说明文件采用一级结构：`WORKFLOWS.md`、`VALIDATORS.md`、`HOOKS.md`、`MIGRATIONS.md`、`RECOVERY.md`、`HANDOFFS.md` 和 `RELEASE_GATES.md`。只有出现真实实现文件时才建立对应子目录。

当前可执行工具：

- `validate_repository.py`：仓库、Schema、状态和 Secret 检查。
- `generate_adapters.py`：确定性生成 Codex 与 Gemini CLI Adapter。
- `release_audit.py`：输出机器可读的 V1.1 Gate 状态，不执行 Promotion。
