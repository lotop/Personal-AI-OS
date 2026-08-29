# Secrets Policy

> 状态：`WORKING`

- 仓库不得保存密码、Token、API Key、私钥或生产凭据。
- 配置只能保存环境变量名、钥匙串引用或 Secret Manager 引用。
- `.env` 与本地凭据文件必须被 Git 忽略。
- 日志、Hook 输出、Handoff 和错误报告不得包含 Secret 值。
- 发现疑似泄露时停止传播并报告，不自动轮换或删除凭据。
