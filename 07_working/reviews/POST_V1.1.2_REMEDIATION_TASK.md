# Post-V1.1.2 Review Remediation Task

> 状态：`REVIEW`
>
> 日期：`2026-09-01`
>
> Task ID：`paos-15-post-v1-1-2-remediation`
>
> Owner：`paos-15-post-v1-1-2-remediation`

## Objective

修复 V1.1.2 全仓库评审发现的状态漂移、文档失真与校验器盲区，并把每一项人工发现转化为可自动执行的检查，避免同类问题复发。

## Scope

- Registry 与 System 基线一致性纠错，并新增跨文件一致性校验。
- `SYSTEM.toml` 冻结提交与发布提交字段拆分，并在 M6 增加绑定断言。
- Schema 子集校验器增加未实现关键字守卫，`pattern` 改为整串匹配。
- 工作日志状态词汇表校验。
- M5 恢复跟进白名单由逐版本文件名改为目录前缀。
- 过期文档纠正（README、Harness README、VALIDATORS、Schemas README、Identity README、Skill）。
- 历史 R0-R12 Gate 模型入口归档。

## Non-goals

- `dashboard/**`：按 Founder 本轮明确指令完全排除，不修改、不验收、不纳入本任务范围。
- 不执行 merge、tag、Release Approval、Promotion 或外部部署。
- 不推送 annotated tag；`v1.1.0`／`v1.1.1`／`v1.1.2` 保持本地绑定。
- 不实现 overlay 的差异化模板内容；本轮只纠正其文档描述。
- 不新建真实业务项目。

## Read Set

全仓库只读评审。

## Write Set

- `SYSTEM.toml`
- `02_registry/projects.toml`、`02_registry/tasks.toml`
- `00_system/schemas/system.schema.json`、`00_system/schemas/README.md`
- `00_system/identity/README.md`
- `05_harness/schema_validation.py`、`validate_repository.py`、`release_audit.py`
- `05_harness/test_schema_validation.py`、`test_release_audit.py`
- `05_harness/README.md`、`05_harness/VALIDATORS.md`
- `07_working/reviews/TEMP_CLEANUP.md`、`RECOVERY_DRILL.md`、`PROJECT_FACTORY_ACCEPTANCE.md`
- `07_working/reviews/POST_V1.1.2_REMEDIATION_TASK.md`
- `README.md`、`CHANGELOG.md`
- `.agents/skills/create-paos-project/SKILL.md`
- `09_archive/v1.1-release-gates-v2/`（由 `05_harness/` 迁入）

## Direct Main 例外理由

依据 `PAOS-009`，Founder 在本轮明确授权实施评审结论并直接在本地 `main` 提交。变更集中于事实纠错、文档同步与校验器加固，Write Set 无并发冲突，可通过 Git 完整回滚。

远端推送依据 `PAOS-013` 单次授权，仅推送 `main` 分支提交历史，不推送 tag、不构成远端发布或Release Approval。

## 已修复项

| # | 问题 | 处置 |
|---|---|---|
| 1 | `projects.toml` 仍声明 `approved_version = 1.1.1`，与 `SYSTEM.toml` 基线矛盾 | 更正为 `1.1.2` / `v1.1.2`；移除未经决策的 `working_target`；新增 `validate_baseline_consistency` 防复发 |
| 2 | `approved_baseline.git_commit` 与 `git_tag` 实际指向不同 Commit，字段名有歧义 | 拆分为 `freeze_commit` 与 `release_commit`；同步 Schema；M6 断言 `release_commit == tag commit` 且 `git_tag`、`approval_reference` 与 Decision 一致 |
| 3 | Schema 子集校验器静默忽略未实现关键字；`pattern` 用子串匹配 | 新增 `unsupported_keywords()` 递归守卫并接入验证器；`pattern` 改 `re.fullmatch`；`additionalProperties` 限定布尔 |
| 4 | 工作日志出现 `PASS` / `APPROVED_FOR_RELEASE` / `APPROVED_EVIDENCE` 等未登记状态 | 归一为已登记词汇表取值；新增 `validate_work_logs` 状态门禁，词汇表动态取自 `states.toml` 与 `tasks.toml` |
| 5 | M5 跟进白名单硬编码逐版本文件名，每次发布都要改审计器本体 | 改为 `is_recovery_followup()` 目录前缀判定（仅 `07_working/reviews/` 平铺文件与 `02_registry/tasks.toml`） |
| 6 | README 声明 `M6 应保持 BLOCKED`，与实测 PASS 矛盾 | 更正为实际行为，并说明工作区不干净时 M1 BLOCKED 属预期 |
| 7 | `identity/README.md` 声称核心模板尚未确认，与 `PAOS-TMPL-003` 矛盾 | 更正为模板已批准、正文仍需按 Memory Pipeline 单独批准 |
| 8 | overlay 被描述为"扩展包/功能叠加包"，实际不改变任何生成内容 | README 与 Skill 更正为"分类标签"并显式说明未实现；Skill 的取值列表与 `factory.toml` 对齐 |
| 9 | `test_release_audit.py` 断言活体仓库门禁 PASS，把合法 BLOCKED 表现为测试失败 | 改为直接断言 `runtimes.toml` 事实，并对 `audit()` 做单次缓存，减少重复 fork |
| 10 | `release_audit_v2` 等历史入口仍留在活跃目录 | 归档到 `09_archive/v1.1-release-gates-v2/` 并更新引用 |

## 未修复项（需 Founder 决策）

- `dashboard/**`：按指令排除。其 `0.0.0.0` 绑定、全仓库静态根与硬编码 Gate 状态问题**仍然存在**，删除前不应运行 `dashboard/server.py`。
- overlay 差异化模板内容：属于新 Template Pack 工作，需要独立 Task 与 Template Approval。
- 首个真实业务项目端到端闭环：需 Founder 指定项目与目标路径。

## Acceptance Criteria

- `python3 05_harness/ci_gate.py --profile local-offline` 返回 `PASS`。
- 每一条新增校验都有对应的负向测试。
- 提交后 M5 如实转为 `STALE`，并在 Handoff 中显式记录需要重跑恢复演练。
- 不产生 tag、不推送 tag、不执行 Release Approval 或 Promotion。

## Validation

见本目录同批次执行记录与 `CHANGELOG.md` 的 `Unreleased` 段。
