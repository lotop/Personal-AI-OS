# Validators

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
