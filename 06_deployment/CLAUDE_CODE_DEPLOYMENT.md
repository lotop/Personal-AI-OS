# Claude Code Deployment

> 状态：`APPROVED`
>
> Approval Reference：`PAOS-020`
>
> 官方资料核验：`2026-08-31`

## 原生能力边界

- Claude Code 在会话启动时读取分层 `CLAUDE.md`；它不会原生读取 `AGENTS.md`。
- `CLAUDE.md` 支持 `@relative/path` 导入，因此本系统通过 `@AGENTS.md` 复用统一 Router，不复制治理正文。
- 共享项目设置位于 `.claude/settings.json`，个人覆盖位于 `.claude/settings.local.json`。
- Hooks、Skills、Subagents 与 Permissions 使用 Claude Code 原生格式；不同平台的同名能力不得假定语义等价。

## Working 部署映射

- 根 `CLAUDE.md` → 导入根 `AGENTS.md`，再附加最小 Claude Code 平台说明。
- `.claude/settings.json` → 只声明官方 JSON Schema 与 `.env` 读取拒绝规则；不预授权写入、命令、网络或外部数据传输。
- Claude Code Adapter → 由 `00_system/compatibility/adapter_profiles.toml` 生成至 `03_adapters/claude-code/`。
- Project Factory → 仅在 Working Candidate Pack 中加入 `CLAUDE.md` 与 `.claude/settings.json`；正式 Template Pack 需单独 Template Approval。
- Hooks → Phase 1 保持关闭。

## 部署与验证

```bash
# 只检查生成结果
python3 05_harness/generate_adapters.py --check

# 先预览部署计划
python3 06_deployment/deploy_adapter.py \
  --manifest 03_adapters/claude-code/manifest.toml \
  --target .

# 经确认后部署；若目标已存在且不同，必须同时提供 --backup-dir
python3 06_deployment/deploy_adapter.py \
  --manifest 03_adapters/claude-code/manifest.toml \
  --target . \
  --apply \
  --backup-dir 99_temp/deployment_backups/claude-code \
  --record-dir 99_temp/deployment_records \
  --authorization-ref PAOS-020 \
  --scope PROJECT
```

## 验收边界

- `CLAUDE.md` 与 `.claude/settings.json` 和生成器输出一致。
- `CLAUDE.md` 只通过仓库内相对路径导入 `AGENTS.md`，不触发外部文件导入。
- JSON 格式有效，且没有扩大默认权限、启用 Hooks 或写入 Secret。
- 本机安装 Claude Code 后，可先做不发送项目内容的 Config Load 检查。
- Live Runtime Smoke 会向 Anthropic 服务发送上下文；必须取得 External Data Authorization，并优先使用合成、非敏感 Payload。

## 当前状态

- Working Adapter：`GENERATED`、`DEPLOYED_CANDIDATE`。
- Config Check：`PASS`（本机 Claude Code `2.1.252`，隔离 `CLAUDE_CONFIG_DIR` 执行 `claude doctor` exit `0`；未登录、未发送 Prompt；Managed Settings 未获取）。
- Live Runtime：`BLOCKED`（尚无 External Data Authorization，未登录、未发送项目内容）。
- Hooks：未配置、未启用。
