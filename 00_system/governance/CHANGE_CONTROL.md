# Change Control

> 状态：`WORKING`

## 变更等级

- `PATCH`：文字、链接、非语义修正，不改变行为。
- `MINOR`：向后兼容的新字段、新规则或新能力。
- `MAJOR`：不兼容 Schema、状态机、目录、权限或 Source-of-Truth 变化。
- `EMERGENCY`：为阻止数据损坏、Secret 泄露或高风险自动化而采取的最小修复。

## 必需证据

每项非 Patch 变更必须包含：Task Card、变更原因、Read/Write Set、Diff、验证结果、兼容性影响、Migration、Rollback 和 Owner。

## 控制规则

- `main` 上的 Working Commit 不等于 Canonical Promotion。
- Major Change 必须有 Decision Record 和 Migration Plan。
- Generated 文件必须由 Source 重新生成，不直接修补后宣称完成。
- Emergency Change 可以先阻断风险，但必须补交证据与复盘。
- Release Tag 只能指向通过全部 Mandatory Gate 的 Commit。
