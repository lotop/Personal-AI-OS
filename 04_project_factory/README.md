# Project Factory

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED (PAOS-018)`

Project Factory 负责从已批准模板创建独立业务项目，并生成可供人工登记的项目候选数据与可验证安装基线。Factory 不直接写入 OS Registry，也不预填虚假的首张正式 Task Card。

- `FACTORY_SPEC.md`：职责、输入、输出和边界。
- `INIT_WORKFLOW.md`：项目创建状态机。
- `VALIDATION.md`：新项目验收条件。
- `factory.toml`：允许的项目类型、Overlay 和安全默认值。
- `create_project.py`：默认 Dry Run 的项目创建引擎。
- `test_factory.py`：路径、变量和 Manifest 安全边界测试。

核心基础模板包 `01_templates/project-base-pack` 版本 `1.1.0` 已正式获得批准（PAOS-TMPL-002），由 `factory.toml` 路由为 `PROJECT_SCAFFOLD`，支持正式创建（非 provisional）。核心结构模板包 `01_templates/core-template-pack` 版本 `1.1.2` 已正式获得批准（PAOS-TMPL-003），由 Factory 路由为 `ARTIFACT_LIBRARY`，不能直接作为完整项目脚手架实例化。Pack 用途不写入或改动 Approved Manifest。

Factory 会在 Dry Run 和 Apply 前核对 Approved Pack 的稳定内容 Digest。`.paos-init.json` V0.2 记录 PAOS/Factory/Template 版本、批准引用、Pack Digest、逐文件 SHA-256、生成器和 Registry Candidate，供未来 Upgrade/Migration 三方 Diff 使用。

未批准的 Working Pack 如未来重新出现，必须显式使用 `--provisional`，且永远只能 Dry Run；`--provisional --apply` 会被拒绝。目标父目录必须预先存在，Factory 不隐式创建多级父目录。
