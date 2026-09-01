---
name: create-paos-project
description: >-
  一键创建符合 Personal AI OS 规范的独立业务项目。
  通过 Approved Template Pack 初始化 Git 仓库、生成项目治理文件和任务模板，并部署 Codex 与 Gemini Adapter。
  当用户想要新建项目、脚手架初始化或提到“创建项目”时使用。
---

# Create PAOS Project (项目工厂创建技能)

本 Skill 用于通过 Personal AI OS 的 Project Factory 自动化创建符合规范的独立业务项目，并自动部署 Codex 与 Gemini 适配器。

---

## 1. 触发与参数收集

当用户激活本 Skill 时，首先检查是否已提供以下核心参数。只询问无法安全推断的缺失项：

1. **项目名称 (`name`)**：人类可读的名称（例如：`智能文档分析器` 或 `smart-doc-analyzer`）。
2. **项目标识 (`project-id`)**：2-63 位小写字母、数字或短横线连字符（例如：`smart-doc-analyzer`）。
3. **主项目类型 (`primary-type`)**：
   - `SOFTWARE_PRODUCT`（软件应用/产品开发，默认推荐）
   - `BUSINESS_VENTURE`（商业创业/业务规划）
   - `RESEARCH_DECISION`（深度调研与决策分析）
   - `OPERATIONS_PROGRAM`（运营与流程项目）
   - `CONTENT_BRAND`（内容创作与品牌建设）
4. **分类标签 (`overlays`)**（可选多选）：
   - 允许取值：`software`、`data`、`ai`、`security`、`compliance`、`content`、`finance`、`vendor`
     （权威来源为 `04_project_factory/factory.toml` 的 `allowed_overlays`）。
   - **当前语义**：overlay 只做取值校验，并记录到 `project.toml` 的 `overlays_csv` 与
     `.paos-init.json`。它**不会改变生成的任何文件内容**。不要向用户描述为"功能叠加包"或
     "扩展包"；差异化模板内容尚未实现。
5. **目标路径 (`target`)**：
   - 默认推荐：`/Users/lotop/Projects/<project-id>`（严禁创建在 `Personal-AI-OS` 仓库内）。
6. **负责人 (`owner`)**：默认为当前用户（`lotop`）。

---

## 2. 标准执行流程

若用户希望自己在终端逐步操作，可直接引导其运行交互向导，本 Skill 的 A~D 步骤已封装在内：

```bash
python3 /Users/lotop/Personal-AI-OS/04_project_factory/new_project.py
```

由 Agent 代为执行时，按以下步骤严格执行：

### 步骤 A：执行 Dry Run（预检与方案展示）

在 `Personal-AI-OS` 根目录下调用工厂脚本进行计划演练：

```bash
python3 /Users/lotop/Personal-AI-OS/04_project_factory/create_project.py \
  --template-pack /Users/lotop/Personal-AI-OS/01_templates/project-base-pack \
  --target <TARGET_PATH> \
  --project-id <PROJECT_ID> \
  --name "<PROJECT_NAME>" \
  --owner <OWNER> \
  --primary-type <PRIMARY_TYPE> \
  --overlay <OVERLAY_1> \
  --git
```

向用户展示生成的项目清单（Plan Manifest）。Dry Run 不创建目标项目。

### 步骤 B：正式创建项目（Apply）

用户确认目标路径和创建计划后，附加 `--apply` 参数执行正式创建：

```bash
python3 /Users/lotop/Personal-AI-OS/04_project_factory/create_project.py \
  --template-pack /Users/lotop/Personal-AI-OS/01_templates/project-base-pack \
  --target <TARGET_PATH> \
  --project-id <PROJECT_ID> \
  --name "<PROJECT_NAME>" \
  --owner <OWNER> \
  --primary-type <PRIMARY_TYPE> \
  --overlay <OVERLAY_1> \
  --git \
  --apply
```

### 步骤 C：部署 Codex 与 Antigravity 适配器

Claude Code 入口（`CLAUDE.md` 与 `.claude/settings.json`）已由 Approved Project Base Pack 直接生成，
无需额外部署。此处只为新建项目注入 Codex 与 Antigravity 的平台适配器配置。部署仅限目标项目，必须附带单次授权引用，若目标存在同名文件需提供 `--backup-dir`。

> **授权引用必须全大写。** `deploy_adapter.py` 的 `AUTHORIZATION_PATTERN` 为
> `^[A-Z0-9][A-Z0-9._:-]{2,127}$`，而 `project-id` 按定义是小写，因此必须转成大写后再拼接：
> `project-id = smart-doc-analyzer` → `--authorization-ref PAOS-INIT-SMART-DOC-ANALYZER`。
> 直接使用小写会在 `--apply` 阶段以 `ERROR: 缺少有效 Deployment 单次授权引用` 退出码 `2` 失败
> （Dry Run 不校验该字段，因此问题只在正式部署时暴露）。

```bash
# 部署 Codex 适配器
python3 /Users/lotop/Personal-AI-OS/06_deployment/deploy_adapter.py \
  --manifest /Users/lotop/Personal-AI-OS/03_adapters/codex/manifest.toml \
  --target <TARGET_PATH> \
  --scope PROJECT \
  --authorization-ref PAOS-INIT-<PROJECT_ID_UPPERCASE> \
  --record-dir 99_temp/deploy_records \
  --apply

# 部署 Antigravity 适配器
python3 /Users/lotop/Personal-AI-OS/06_deployment/deploy_adapter.py \
  --manifest /Users/lotop/Personal-AI-OS/03_adapters/antigravity-cli/manifest.toml \
  --target <TARGET_PATH> \
  --scope PROJECT \
  --authorization-ref PAOS-INIT-<PROJECT_ID_UPPERCASE> \
  --record-dir 99_temp/deploy_records \
  --apply
```

### 步骤 D：完成验证与报告

1. 验证目标目录下是否存在以下核心文件：
   - `<TARGET_PATH>/AGENTS.md`
   - `<TARGET_PATH>/PROJECT.md`
   - `<TARGET_PATH>/DECISIONS.md`
   - `<TARGET_PATH>/CLAUDE.md`（首行必须是 `@AGENTS.md`）
   - `<TARGET_PATH>/.claude/settings.json`
   - `<TARGET_PATH>/.codex/config.toml`
   - `<TARGET_PATH>/.gemini/settings.json`
   - `<TARGET_PATH>/.git`
2. 检查 `.paos-init.json` 中的 Template 版本和逐文件 SHA-256。
3. 分别报告已创建、已验证、已部署到目标项目和尚未完成的事项。
