# Project Factory

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

Project Factory 负责从已批准模板创建独立业务项目，并完成登记、初始化验证和首张 Task Card 建立。

- `FACTORY_SPEC.md`：职责、输入、输出和边界。
- `INIT_WORKFLOW.md`：项目创建状态机。
- `VALIDATION.md`：新项目验收条件。
- `factory.toml`：允许的项目类型、Overlay 和安全默认值。
- `create_project.py`：默认 Dry Run 的项目创建引擎。
- `test_factory.py`：路径、变量和 Manifest 安全边界测试。

核心项目模板尚未逐项批准，因此当前引擎会拒绝使用未批准 Template Pack 进行正式创建；Candidate 只能显式标记为 `PROVISIONAL` 进行演练。
