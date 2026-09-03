# Project Factory Specification

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED (PAOS-018)`

## 用途与层级

- 用途：以一致、可追溯、可回滚的方式创建独立项目。
- 层级：Personal AI OS Control Plane。
- 维护者：总控任务；实现可由 Factory Owner 提交，总控评审。
- Source of Truth：本规范批准后可成为 Factory 规则来源；生成出的业务项目自行拥有其项目文件。

## 输入

- `project_id`、名称、Slug 和 Owner。
- 项目边界、目标和 Non-goals。
- 一个 Primary Type。
- 已批准的 Template Pack 版本。
- 目标路径和 Git 初始化策略。

## 项目类型候选

| 类型 | 适用 | 专属框架文件 |
|---|---|---|
| `SOFTWARE_DEVELOPMENT` | 软件开发 | `TYPE_SOFTWARE_DEVELOPMENT.md.tmpl` |
| `SOLUTION_RESEARCH` | 方案调研 | `TYPE_SOLUTION_RESEARCH.md.tmpl` |
| `CONTENT_MARKETING` | 内容营销 | `TYPE_CONTENT_MARKETING.md.tmpl` |
| `BRAND_MANAGEMENT` | 品牌管理 | `TYPE_BRAND_MANAGEMENT.md.tmpl` |

每个类型都必须在 Template Pack 中提供一份专属约定框架，经 `template.toml` 的 `primary_types` 过滤器产出到目标项目的 `00_governance/PROJECT_TYPE_FRAMEWORK.md`。**新增类型时必须同步提供框架文件**，否则该类型的项目会缺少类型约定，项目自校验器会报错。

每个项目只选一个主要类型。分类标签（overlay）已在 `PAOS-TMPL-005` 中移除：它不改变任何生成内容，也无任何消费方，留着只会造成误解。

## 输出

- 可选的独立项目目录和 Git Repository；默认只输出 Dry Run。
- 项目级 `AGENTS.md`、`PROJECT.md`、`project.toml` 和 Decisions 入口。
- Working、Source、Knowledge、Archive 与 Temp 边界。
- `.paos-init.json` V0.3 安装基线，包含 Project Registry Candidate 数据，但不直接写入 OS Registry。
- 空白 `TASKS.md` 任务模板；首张正式 Task Card 只在项目 Objective/Scope 确认后创建。
- Dry Run Manifest、逐文件 SHA-256 和回滚所需信息。

## 不变量

- 不把业务项目创建在 Personal AI OS 仓库内部。
- 不覆盖任何已存在目标，也不隐式创建不存在的多级父目录。
- 不把未批准模板用于正式创建。
- Approved Template Pack 必须通过 Factory 外部登记的稳定内容 Digest 校验。
- Working Template Pack 永远只能 Dry Run，不能 Apply。
- 不写入真实 Secret。
- 不自动批准项目或执行 Canonical Promotion。
- 模板实例化后，业务项目拥有生成文件；OS 只提供升级建议和 Migration。

## 模板关系

`01_templates/` 保存批准后的模板；`07_working/candidates/` 只在未来存在新候选时保存待审模板。Factory 只能正式实例化前者，并以 `factory.toml` 中的 Pack Kind 和 Approved Digest 验证用途与内容。Candidate 演练必须显式使用 `--provisional`，只输出 Dry Run。

无论 Template Pack 是否已批准，新生成项目在 Owner 验收前统一记录为 `PROVISIONAL`；Template 的批准状态由 `.paos-init.json.template_state` 独立记录。Factory 不自动批准项目、Task 或 Registry Record。
