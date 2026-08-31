# Multi-Agent Handoff｜Claude Code to Codex｜Post-V1.1.2 Remediation

> 状态：`ARCHIVED`
>
> 日期：`2026-09-01`
>
> 归档原因：Founder 明确要求忽略本 Handoff；后续工作由 `paos-16-full-audit-remediation` 基于当前仓库事实独立推进。本文件仅保留为历史证据。
>
> 层级：`TASK`
>
> Source of Truth：否。本文件只证明交接上下文；事实以 Git Commit、`02_registry/` 与 `DECISIONS.md` 为准。
>
> 结构模板：`01_templates/core-template-pack/HANDOFF_TEMPLATE.md.tmpl`（`PAOS-TMPL-003`）

## Handoff Contract

- Handoff ID：`HANDOFF-POST-V1.1.2-001`
- Task ID：`paos-15-post-v1-1-2-remediation`
- From / To：`Claude Code (claude-opus-5)` -> `Codex`
- To Runtime：`codex-cli 0.151.0-alpha.7.2`（登记见 `02_registry/runtimes.toml`）
- Base Commit / Branch：`d5dac3a037d3ca9b9731886da4099d49c3250bcd` / `main`
- 前一基线：`b2b0ef8b4ec20be4a2cfb2426174d0532ddafa72`（annotated tag `v1.1.2`）
- Write Set：见下方"实际 Write Set"，与其他任务无重叠。
- Task Card：`07_working/reviews/POST_V1.1.2_REMEDIATION_TASK.md`
- Next Owner：Codex（执行恢复演练与后续发布准备）

## 起点

从 `main` 的 `d5dac3a` 开始。该提交已通过本地离线 CI 全部 8 项检查。

```bash
git -C /Users/lotop/Personal-AI-OS log --oneline -1
python3 05_harness/ci_gate.py --profile local-offline
```

## Completed

**事实纠错**

- `02_registry/projects.toml` 已批准基线由 `1.1.1` 更正为 `1.1.2`；移除未经决策记录的 `working_target`。
- `SYSTEM.toml` 的 `approved_baseline.git_commit` 拆分为 `freeze_commit`（`b76a8d2`）与 `release_commit`（`b2b0ef8`），消除"tag 指向该 commit"的歧义读法；`system.schema.json` 同步。
- 三处越权工作日志状态归一：`PASS` → `DONE`、`APPROVED_EVIDENCE` → `APPROVED`、`APPROVED_FOR_RELEASE` → `APPROVED`。各文件正文的 `结论：PASS` 字段未改动，`release_audit.py` 的 M3/M5 文本断言不受影响。
- `README.md` 的 "M6 应保持 BLOCKED" 更正；`00_system/identity/README.md` 与 `PAOS-TMPL-003` 对齐；`05_harness/README.md`、`VALIDATORS.md`、`00_system/schemas/README.md` 同步。
- overlay 在 `README.md` 与 `create-paos-project` Skill 中如实描述为**分类标签**，并对齐 `factory.toml` 的 8 个取值。

**校验器加固（每项均含负向测试）**

| 检查 | 位置 | 作用 |
|---|---|---|
| `validate_baseline_consistency` | `05_harness/validate_repository.py` | `SYSTEM.toml` 基线与 `projects.toml` 本仓库记录必须一致；`git_tag` 必须等于 `v{version}` |
| `validate_schema_shapes` + `unsupported_keywords` | `validate_repository.py` / `schema_validation.py` | Schema 使用未实现关键字直接失败，不再静默通过 |
| `validate_work_logs` | `validate_repository.py` | `07_working/reviews/*.md` 状态必须来自 `states.toml` 与 `tasks.toml` 的已登记词汇表 |
| `is_recovery_followup` | `05_harness/release_audit.py` | M5 跟进白名单改为目录前缀判定，审计器不再随每次发布修改 |
| M6 基线绑定 | `release_audit.py` | 断言 `git_tag`、`approval_reference`、`release_commit` 与 Tag/Decision 精确一致 |

`schema_validation.py` 的 `pattern` 由 `re.search` 改为 `re.fullmatch`；`additionalProperties` 限定布尔值。

**其他**

- 历史 R0-R12 Gate 入口归档至 `09_archive/v1.1-release-gates-v2/`。
- `test_release_audit.py` 解除对活体门禁状态的耦合（改为断言 `runtimes.toml` 事实），`audit()` 加单次缓存，减少重复 fork。
- `DECISIONS.md` 新增 `PAOS-013` 远端同步授权。

## 实际 Write Set

```
SYSTEM.toml  README.md  CHANGELOG.md  DECISIONS.md
00_system/identity/README.md
00_system/schemas/README.md  00_system/schemas/system.schema.json
02_registry/projects.toml  02_registry/tasks.toml
05_harness/schema_validation.py  05_harness/validate_repository.py  05_harness/release_audit.py
05_harness/test_schema_validation.py  05_harness/test_release_audit.py
05_harness/README.md  05_harness/VALIDATORS.md
07_working/reviews/{POST_V1.1.2_REMEDIATION_TASK,PROJECT_FACTORY_ACCEPTANCE,RECOVERY_DRILL,TEMP_CLEANUP}.md
09_archive/v1.1-release-gates-v2/        （由 05_harness/ 迁入）
.agents/skills/create-paos-project/SKILL.md
```

## Validation

| 项目 | 结果 |
|---|---|
| `ci_gate.py --profile local-offline` | `PASS`（repository / factory / schema / release-audit / deployment / tree-digest / temp-cleanup / adapters） |
| `validate_repository.py` | `ERRORS=0 WARNINGS=0` |
| `test_schema_validation.py` | `PASS` 10 项（新增 5 项） |
| `test_release_audit.py` | `PASS` 12 项（新增 4 项） |
| `generate_adapters.py --check` | `ADAPTERS_OK`（未触碰 Adapter 源与生成物） |
| 负向验证 | 五项新增检查逐条构造反例确认会报错，非空跑 |

## 当前 Gate 状态（`d5dac3a`）

```
M1 PASS   M2 PASS   M3 PASS   M4 PASS   M5 STALE   M6 BLOCKED
```

**M5 `STALE` 与 M6 `BLOCKED` 是设计内的正确行为，不是故障：**

- M5：恢复证据绑定在 `2e83648`，本批次改动了 `05_harness/*.py`、`SYSTEM.toml` 等实现文件，审计器如实报"恢复后仍有实现变更"。
- M6：`v1.1.2` tag 指向 `b2b0ef8`，HEAD 已前移，tag 不再绑定 HEAD。

这两项在下一次正式发布前必须由新的演练与新的 Release Approval 重新满足。**不得通过改写 `recovery_evidence.toml` 或移动 tag 来"修复"它们。**

## Remaining（交给 Codex）

1. **重跑恢复演练**（阻塞下一次发布）
   - 对 `d5dac3a` 或后续冻结 Commit 执行 `git clone --no-local` 冷克隆 + 离线 Git Bundle 双路径恢复。
   - 两个副本都必须通过 `ci_gate --profile local-offline` 与 `generate_adapters.py --check`，且 Tree Digest 一致。
   - 更新 `07_working/reviews/recovery_evidence.toml` 与 `RECOVERY_DRILL.md`，使 M5 回到 `PASS`。

2. **overlay 差异化模板内容**（可选，需独立授权）
   - 当前 overlay 只做取值校验与记录，不改变任何生成内容，文档已如实说明。
   - 若要实现，属于新 Template Pack 工作，需要独立 Task Card 与 `PAOS-TMPL` 级别批准，不得直接改 `01_templates/project-base-pack`。

3. **首个真实业务项目端到端闭环**
   - 目前 `02_registry/projects.toml` 只有控制平面自身，全部治理规则尚未经过真实项目的压力测试。
   - 需要 Founder 指定项目名与目标路径（不得落在本仓库内）后再执行。

## Known Risks

- **`dashboard/**` 未修复且已知不安全。** 按 Founder 本轮明确指令完全排除，Founder 表示后续会删除。当前 `dashboard/server.py` 绑定 `0.0.0.0`（非 localhost）、静态根为整个仓库根（`.git` 可读）、并返回硬编码的门禁状态。**在删除前不要运行它，也不要把它的 Gate 面板当作证据。**
- Claude Code 与 Gemini 的 Live Runtime 仍未获外部数据授权，`runtimes.toml` 中保持 `runtime_smoke = "NOT_RUN"`。不得把 Config Load 报告为 Runtime 验证。
- 私有远端恢复（`private_remote_recovery`）仍为 `NOT_TESTED`；本次 Push 只是备份，不等于恢复演练通过。
- Quarantine 位于 `99_temp/`，被 `.gitignore` 忽略，因此"可恢复"仅在本机磁盘范围内成立。

## Required Decision

- 是否推送 annotated tag `v1.1.0` / `v1.1.1` / `v1.1.2` 到 GitHub。`PAOS-013` **未**授权推送 tag，当前 Release 证据仍由本地 tag 绑定。
- 下一个版本号与范围（本次刻意未在 Registry 中写入任何 `1.1.3` 字样，避免发明未经决策的版本）。

## Release Boundary

- 已批准基线不变：`v1.1.2` / `PAOS-REL-003`；`SYSTEM.toml` 的 `release = "APPROVED_LOCAL_NO_PUSH"` 仍然成立，因为 tag 未推送。
- 本次仅推送 `main` 分支提交历史，依据 `PAOS-013`。
- 本次不含 Tag、远端发布、外部部署、Promotion 或真实项目数据传输。

## Evidence

- Task Card：`07_working/reviews/POST_V1.1.2_REMEDIATION_TASK.md`
- Decision：`DECISIONS.md` `PAOS-009`（Direct Main 例外）、`PAOS-013`（远端同步授权）
- Changelog：`CHANGELOG.md` `Post-V1.1.2 Working` 段
- Base Commit：`d5dac3a037d3ca9b9731886da4099d49c3250bcd`
