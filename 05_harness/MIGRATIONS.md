# Migrations

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-019`

系统配置、Schema、Registry 和 Adapter 发生不兼容变化时，必须提供可验证、可回滚的迁移说明。

Tree Digest V0.2 将 Git mode 与 object kind 纳入摘要。V1.1.4 的 V0.1 Recovery Evidence 保持历史原文；V1.2 恢复演练必须声明 `tree_digest_version = "0.2"` 并生成新的固定证据，不得改写旧证据。
