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

核心基础模板包 `01_templates/project-base-pack` 版本 `1.1.0` 已正式获得批准（PAOS-TMPL-002），类型为 `PROJECT_SCAFFOLD`，支持正式创建（非 provisional）。核心结构模板包 `01_templates/core-template-pack` 版本 `1.1.2` 已正式获得批准（PAOS-TMPL-003），类型为 `ARTIFACT_LIBRARY`，不能直接作为完整项目脚手架实例化。

未批准的 Working Pack 如未来重新出现，仍需显式使用 `--provisional` 仅供临时演练。
