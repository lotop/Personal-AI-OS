# Deployment

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

本目录定义 Personal AI OS 向 Codex、Gemini CLI 等 Agent 的部署、验证、回滚、备份和恢复规则。

- `DEPLOYMENT_SPEC.md`：共同部署协议。
- `CODEX_DEPLOYMENT.md`：Codex 部署边界。
- `GEMINI_DEPLOYMENT.md`：Gemini CLI 部署边界。
- `BACKUP_RECOVERY.md`：备份与恢复验收。
- `deploy_adapter.py`：默认 Dry Run、覆盖前强制备份的平台部署器。
- `test_deployment.py`：创建、幂等和替换回滚边界测试。

当前只准备部署规范；尚未写入用户级 Agent 配置，也未启用 Hooks。
