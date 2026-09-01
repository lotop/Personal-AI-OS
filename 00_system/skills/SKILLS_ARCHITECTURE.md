# Skills Architecture

> 状态：`APPROVED`
>
> 适用版本：`V1.2.0`
>
> Canonical Authority：`PAOS-021`

## 定位与原则

Skill 是按需加载的可复用专业工作协议（SOP），不是全局常驻的系统规则，也不自动获得超越当前会话和任务的额外权限。

- **按需加载**：仅在用户意图或当前任务明确涉及该领域时触发，不无差别全量加载。
- **协议自治**：Skill 以标准 Markdown 形式沉淀专业知识、执行步骤、安全预检与报告模板。
- **权限不扩散**：Skill 的执行受限于当前 Agent 的 Session 权限与 Task Card 声明的 Write Set，严禁执行未经明确授权的破坏性操作或静默修改 Canonical 事实源。

## 标准目录与文件格式

所有受管 Skill 统一定义于 `.agents/skills/<skill-id>/` 目录下：

```text
.agents/skills/<skill-id>/
├── SKILL.md                 # 必须：技能主定义（含标准 YAML Frontmatter）
├── references/              # 可选：参考文档与规范
└── scripts/                 # 可选：辅助验证或处理脚本
```

### `SKILL.md` 标准 Frontmatter 契约

每个 `SKILL.md` 必须以标准 YAML Frontmatter 开头，包含以下字段：

```yaml
---
name: skill-id-lowercase
description: 简明扼要的触发场景与功能描述，供 Agent 理解与路由匹配。
---
```

## Registry 字段要求与元数据

在 `02_registry/skills.toml` 中登记的技能需声明：

- `id`：符合 `^[a-z0-9-]+$` 的稳定标识符。
- `path`：相对仓库根目录的有效路径（如 `.agents/skills/<skill-id>/SKILL.md`）。
- `artifact_state`：`WORKING` / `APPROVED` / `ARCHIVED`。
- `owner`：已在 `tasks.toml` 中登记的 Task ID。
- `description`：明确的触发条件与功能摘要。

## 生命周期

Skill 的完整演化遵循以下生命周期：

`DISCOVERED → REVIEWED → CANDIDATE → TESTED → APPROVED → ENABLED → DEPRECATED → ARCHIVED`

1. **DISCOVERED / REVIEWED**：发现或设计新的工作流协议。
2. **CANDIDATE / TESTED**：编写在 `.agents/skills/` 下，完成语法验证与演练。
3. **APPROVED / ENABLED**：经 Founder 确认或 Pack Promotion，登记入 Skills Registry。
4. **DEPRECATED / ARCHIVED**：被新流程替代后归档，保留追溯证据。

## 跨平台兼容与适配

- **Codex / ChatGPT**：通过项目规则按需读取 `.agents/skills/` 下的 `SKILL.md`。
- **Claude Code**：在 `CLAUDE.md` 治理框架下按需引用协议，不自行私建未登记技能。
- **Gemini CLI**：遵循 Session Protocol 与 Skill 指引执行。
- 平台入口由各适配器统一协调，保持核心 SOP 业务逻辑一致。
