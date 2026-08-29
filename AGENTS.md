# Personal AI OS V1.1

> 模板版本：`0.4-candidate`
>
> 状态：`CANDIDATE`
>
> Canonical Authority：`NONE`

本文件是仓库根入口的候选版本，尚未批准。它负责导航和最低限度的安全边界，不承载全部治理正文。

## 系统定位

本仓库用于建设 Personal AI OS 的 Canonical Control Plane。业务项目保持为独立项目和独立仓库，只在 Registry 中登记。

## Source of Truth

- 正式系统规则位于 `00_system/`。
- 已批准模板位于 `01_templates/`。
- Registry 位于 `02_registry/`，人工维护的结构化配置默认使用 TOML。
- Agent 专用配置位于 `03_adapters/`，属于 `GENERATED`，不得作为规则源头直接维护。
- Project Factory 位于 `04_project_factory/`，只能正式实例化已批准模板。
- Harness 位于 `05_harness/`。
- 部署、备份与恢复规范位于 `06_deployment/`。
- `07_working/`、`99_temp/`、Conversation、Cache 和 Logs 不是正式事实来源。

未经明确批准，不得将任何 `WORKING` 或 `CANDIDATE` 内容晋升为 `APPROVED` 或 `CANONICAL`。

## 最小充分上下文

按以下顺序加载与当前任务直接相关的内容：

1. 适用的 `00_system/governance/` 与 `00_system/security/` 规则。
2. 当前 Mode。
3. 当前项目的 `PROJECT.md`、适用 Decisions 与 Memory。
4. 当前 Task Card。
5. 与任务直接相关的 Source、Knowledge 和文件。

不得无差别加载全部 Modes、历史、项目或归档资料。

## Task Card 与并发

非简单任务必须声明：`Objective`、`Scope`、`Read Set`、`Write Set`、`Dependencies`、`Expected Output`、`Acceptance Criteria` 和 `Owner`。

- 读取型工作可以并行。
- 写入不同文件的任务必须具有不重叠的 `Write Set`，实现阶段优先使用独立 Git Worktree。
- 修改同一个 Canonical 文件的任务不得并行。
- 普通任务不得直接修改 `main` 或执行 Canonical Promotion。
- Founder 决策、跨任务冲突、合并、Tag 和 Promotion 回到总控任务。

详细规则由 `00_system/governance/CONCURRENCY_POLICY.md` 定义。

## 信息状态

必须分别记录资产类别与成熟度。资产类别包括 `SOURCE`、`RULE`、`TEMPLATE`、`CONFIG`、`REGISTRY`、`GENERATED`、`TEMP`、`CACHE`、`LOG`、`ARCHIVE`；成熟度包括 `WORKING`、`CANDIDATE`、`APPROVED`、`CANONICAL`、`SUPERSEDED`、`ARCHIVED`。

Conversation 只能作为历史或证据，不能直接等同于 Memory、Decision 或 Project Knowledge。

## 配置与 Adapter

- Markdown 用于规则、说明、决策和知识。
- TOML 用于人工维护的 Canonical Config 与 Registry。
- JSON 用于目标平台要求的配置和机器生成数据。
- JSONL 用于追加式事件与审计记录。
- YAML 仅在外部工具明确要求时使用。
- 密钥、Token 和密码不得写入仓库。

Adapter 必须从已批准的 Source 生成，并标明来源、版本和生成状态。

## Hooks

Hooks 只能执行已批准并登记的规则。Phase 1 默认关闭，只允许检查、提醒、产生 Candidate 和最小审计。

Hooks 不得自动批准、Promotion、commit、merge、push、deploy、publish、delete 或执行破坏性清理。Hook 必须声明触发事件、权限、副作用、幂等策略、超时和失败策略。

具体规则由 `00_system/governance/HOOKS_POLICY.md` 与 `05_harness/HOOKS.md` 定义。

## Harness

共同最小流程候选为：

`Understand → Plan → Execute → Validate → Review → Handoff → Cleanup`

在宣布完成前，必须提供验证证据，更新必要的 Decisions/Knowledge，完成适用 Handoff，并处理 Working、Temp、Cache 和 Logs。

## 安全与恢复

- 不静默覆盖 Source、Approved 或 Canonical 内容。
- 不扩大权限或读取与任务无关的秘密。
- GC 默认 Dry Run，并保留恢复路径。
- 部署、备份和恢复必须有可验证记录。

## 冲突优先级

1. 用户当前任务中的明确指令。
2. 当前项目已批准的约束。
3. 当前 Task Card。
4. 当前 Mode。
5. Personal AI OS 全局治理规则。
6. Agent 或 Runtime 默认行为。

影响目标、权限、Source of Truth 或正式交付物的冲突不得静默处理。
