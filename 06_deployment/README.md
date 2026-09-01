# Deployment

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED`
>
> Approval Reference：`PAOS-020`

本目录定义 Personal AI OS 向 Codex、Claude Code、Gemini CLI 等 Agent 的部署、验证、回滚、备份和恢复规则。

- `DEPLOYMENT_SPEC.md`：共同部署协议。
- `CODEX_DEPLOYMENT.md`：Codex 部署边界。
- `CLAUDE_CODE_DEPLOYMENT.md`：Claude Code 部署边界。
- `GEMINI_DEPLOYMENT.md`：Gemini CLI 部署边界。
- `BACKUP_RECOVERY.md`：备份与恢复验收。
- `deploy_adapter.py`：默认 Dry Run；Apply 强制单次授权、Scope、不可变记录和覆盖前备份的平台部署器。
- `test_deployment.py`：生成/部署的 containment、幂等、授权与事务回滚测试。

当前只准备并部署项目级 Working Adapter；尚未写入用户级 Agent 配置，也未启用 Hooks。
