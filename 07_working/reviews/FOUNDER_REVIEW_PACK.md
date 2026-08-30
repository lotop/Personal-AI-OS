# Founder Review Pack｜Personal AI OS V1.1 Minimum

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 已解决

Founder 已通过 `PAOS-007` 批准实施 V1.1 Minimum：

- 资产状态只保留 `WORKING / APPROVED / ARCHIVED`。
- Canonical Authority 由批准记录、固定 Commit 与 Release Evidence 表达。
- Mode 只保留 `CHAT / WORK / REVIEW`。
- Session Close 与 Handoff 按交接、跨环境、长暂停、Blocked 或持久结论触发。
- Release Readiness 收敛为 M1–M6；Promotion 是 M6 后的授权动作。
- Gemini 在 V1.1 为 `CONDITIONAL`：Config Load 是 M4 证据，Live Runtime 不阻塞发布。

PAOS-007 只批准 Working 实施，不构成 Template Approval、Release Approval、Canonical Promotion、Tag、Push 或部署授权。

## 待决定 1｜首个 Template Pack

当前 Working Pack 已通过 Provisional E2E。请在固定 Commit/SHA 上决定是否批准以下结构：

- `AGENTS.md`、`PROJECT.md`、`project.toml`
- `DECISIONS.md`、`TASKS.md`
- 条件式 `SESSION_CLOSE.md`、`HANDOFF.md`
- `sources/ knowledge/ working/ archive/ tmp/`

批准后仍需从 Approved Pack 执行 Formal Factory E2E。

## 待决定 2｜Gemini Live Smoke

Gemini Live Runtime 不阻塞 V1.1。若仍希望执行，需单独明确允许发送的最小非敏感测试文本；系统不会默认外发仓库内容。

## 待决定 3｜V1.0 Baseline

V1.0 原始文件、Commit 或 Tag 不可得。建议将 V1.1 定义为第一个可验证 Baseline，不声称完成 V1.0 Migration。

## 待决定 4｜基础设施范围

Private Git Remote、加密备份目标、Credential Manager、对象存储、手机 Capture 和跨设备恢复尚未验证。需决定哪些属于 V1.1 Required，哪些进入后续版本。

## 待决定 5｜最终发布

只有 M1–M5 对同一固定 Commit 通过后，才提交 M6 Release Approval。批准前不会 Tag、Push、发布或执行 Canonical Promotion。
