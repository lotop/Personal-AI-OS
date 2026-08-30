# Founder Review Pack｜Personal AI OS V1.1

> 状态：`WORKING`
>
> Canonical Authority：`NONE`
>
> 用途：集中呈现仅能由 Founder 决定的事项；技术验证结果不需要逐项人工批准。

## 当前可复核结论

- Repository 骨架、Schema、Adapter 生成、Codex Runtime、离线 Git Bundle 恢复已形成验证证据。
- Candidate Project Base Pack 已可执行，Provisional E2E 已通过。
- Gemini CLI 配置加载已通过；Live Runtime 未执行，原因是尚无外部数据传输授权。
- V1.0 原始文件、Commit 或 Tag 不可得，不能声称完成了 V1.0 → V1.1 的完整迁移审计。
- V1.1 尚未发布；没有 Release Approval、Release Tag 或 Canonical Promotion。

## 决策 0｜治理状态与 Hook 权限

请确认：

1. 是否保留 `APPROVED` 与 `CANONICAL` 为两个不同状态（建议保留：批准不等于已经进入唯一运行时 Source of Truth）。
2. 是否采用 `origin_class / governance_state / lifecycle_state / materialization_class` 四维模型，淘汰含义混杂的单一 `status`。
3. Phase 1 Hook 是否允许对已批准的固定安全禁令执行自动 `deny`；继续禁止 Hook 自动 `allow / approve / promote / publish / delete`。
4. Canonical Promotion 是否要求 annotated tag；是否进一步强制 signed tag 留待确认。

## 决策 1｜首个 Candidate Template Pack

### 解决什么问题

让 Project Factory 可以生成一个具有统一治理、安全、任务、交接和生命周期边界的独立项目。

### 层级、维护者与权威性

- 层级：Project Factory Base Template。
- 模板维护者：Personal AI OS Factory Owner。
- 实例维护者：生成后由业务 Project Owner 维护。
- 当前属性：`CANDIDATE / Canonical Authority NONE`。
- 批准后的属性：仅模板结构获得 `APPROVED`；生成项目内容不会因此自动成为 Canonical。

### 文件关系

- `project.toml`：机器可读身份、类型、路径和安全默认值。
- `PROJECT.md`：目标、范围、Non-goals 和成功标准。
- `AGENTS.md`：Agent Router、加载顺序、权限和完成协议。
- `DECISIONS.md`、`TASKS.md`：根级索引/模板，避免单文件子目录。
- `SESSION_CLOSE.md`、`HANDOFF.md`：会话增量和跨任务交接。
- `sources/ knowledge/ working/ archive/ tmp/`：因具有独立生命周期而保留目录，使用 `.gitkeep` 初始化。

### Founder 待确认

1. 是否批准 Pack 中 7 个根级模板作为第一批整体结构；若否，请指出需拆回逐文件审批的文件。
2. `Non-goals` 与 `Permissions` 是否为复杂 Task Card 必填字段。
3. `knowledge/` 是否只允许 Approved，或允许 `knowledge/candidates/`。
4. Session Close 与 Handoff 是按复杂任务“必需”，还是“发生交接/形成持久结论时必需”。
5. Provisional 项目转正式时，采用“从 Approved Pack 重新生成”还是“受控 Migration”。

## 决策 1A｜Mode Contract 轴模型

第二轮 Mode 独立审计建议将当前 Mode 拆为：

- `interaction_profile = WORK | CHAT`
- `intent_mode = BRAINSTORM | RESEARCH | STRATEGY | PRODUCT | CODING | REVIEW`
- `execution_phase = INTAKE | PLAN | EXECUTE | VERIFY | CLOSE`

当前本地 Candidate 仍使用兼容的单一 `primary_mode + supporting_mode`，并新增 `WORK / PLANNING`。请确认采用三轴模型，还是保留单轴模型；在确认前不会把 Mode Registry 升级为 Approved。

## 决策 2｜Gemini Capability Tier 与外部数据授权

选择其一：

- `REQUIRED`：V1.1 发布前授权一次最小 Live Smoke，并将 Gemini Runtime 设为强制能力。
- `CONDITIONAL`：V1.1 可发布，但明确标注 Gemini 仅完成 Config Load，Live Runtime 未验证。
- `OUT_OF_SCOPE`：V1.1 不承诺 Gemini Runtime，仅保留 Adapter Candidate。

若选择 `REQUIRED`，仍需单独明确允许向 Google Gemini 发送哪一段最小、非敏感测试文本；系统不会默认发送本仓库内容。

## 决策 3｜V1.0 Baseline Disposition

选择其一：

- 等待取得 V1.0 原件后再发布。
- 接受 reconstructed baseline，同时列明无法验证项。
- 将 V1.1 定义为第一个可验证 Baseline，但不声称完成 V1.0 Migration。

## 决策 4｜基础设施范围

以下项目不能用本地测试伪造完成：Private Git Remote、加密备份目标、Credential Manager、对象存储、手机 Capture 入口，以及跨设备/远端丢失恢复。请决定哪些属于 V1.1 Required，哪些进入后续版本。

## 决策 5｜最终发布

只有前述范围明确、阻断问题关闭后，系统才会冻结一个 Release Commit、Evidence Pack Hash 和 Promotion Plan，请 Founder 对该固定版本选择：`APPROVE / REJECT / RETURN_FOR_FIX`。

批准前不会打 Tag、Push、发布或将 Candidate 静默晋升为 Canonical。
