# Project AGENTS Template Candidate

> 模板状态：`CANDIDATE`
>
> 模板版本：`0.1-candidate`
>
> Canonical Authority：`NONE`
>
> Owner：`paos-04-factory`

> 可执行 Candidate Pack：`07_working/candidates/project-base-pack/`

## 模板说明

- 解决的问题：为 Codex 等能读取 `AGENTS.md` 的 Agent 提供项目级最小 Router、安全边界和完成协议。
- 使用层级：Project Root。
- 维护者：模板由 Personal AI OS 维护；实例化后由业务项目 Owner 维护项目事实。
- Source-of-Truth 属性：批准后的模板是结构来源；实例化的项目文件是该项目的指令入口，不反向修改模板。
- 与其他文件关系：读取 `PROJECT.md`、`project.toml`、适用 Decisions、Task Card 和相关 Source；不复制全部知识库。

---

# {{PROJECT_NAME}}

> Project ID：`{{PROJECT_ID}}`
>
> Owner：`{{OWNER}}`
>
> Template Version：`{{TEMPLATE_VERSION}}`

## 项目定位

本仓库是 `{{PROJECT_NAME}}` 的独立项目仓库。项目目标、范围和成功标准以 `PROJECT.md` 为准，机器可读元数据以 `project.toml` 为准。

## 启动顺序

处理非简单任务前，按最小充分原则读取：

1. 本文件和项目级已批准规则。
2. `PROJECT.md`、适用 Decisions 和当前状态。
3. 当前 Task Card。
4. 与任务直接相关的 Source、Knowledge 和文件。

不得默认加载全部历史、归档、其他项目或无关资料。

## Source of Truth

- `sources/`：原始输入，只读，不静默改写。
- `knowledge/`：项目批准后的长期知识。
- `working/`：Working Draft，不具有 Canonical Authority。
- `archive/`：已替代但需追溯的材料。
- `tmp/`、`cache/`、`logs/`：临时运行资产，不进入 Promotion。

Conversation、AI 总结和 Generated 文件不得自动成为项目事实。

## Task Card

复杂任务必须声明：

- Objective
- Scope 与 Non-goals
- Read Set 与 Write Set
- Dependencies
- Expected Output
- Acceptance Criteria
- Owner
- Permissions

并行写入必须确保 Write Set 不重叠；同一正式文件不得由多个任务同时修改。

## 权限与安全

- 使用完成任务所需的最小权限。
- 不读取、输出或提交真实 Secret。
- 不静默覆盖 Source、Approved 或 Canonical 内容。
- 删除、部署、外部发布、权限升级和破坏性清理需要明确授权。
- Generated Adapter 必须可追溯到批准的 Source 和生成器版本。

## 完成协议

复杂任务遵循：

`Understand → Plan → Execute → Validate → Review → Handoff → Cleanup`

宣布完成时必须分别说明：已修改、已验证、已提交、已部署、尚未完成和需要决策的事项。未经验证不得声称部署或恢复成功。

## 冲突处理

当用户当前指令、项目规则、Task Card、Agent 默认行为发生冲突时，不静默选择。影响目标、权限、Source of Truth 或正式交付物的冲突必须交给 Project Owner 决定。

## 待确认字段

- 是否保留 `Non-goals` 为每张 Task Card 必填字段。
- 是否将 `Permissions` 设为所有复杂任务的必填字段。
- `knowledge/` 是否只允许 Approved，还是允许 Candidate 子层。
- Session Close 与 Handoff 是否必须在每个复杂任务结束时生成文件。

## 当前实现说明

本文件保留为逐项讨论入口；可执行模板位于 Candidate Pack 中。两者均未获 Founder Approval，不得移动到 `01_templates/` 或用于正式项目创建。
