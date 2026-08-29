# Agent Deployment Smoke Review

> 状态：`WORKING`
>
> Canonical Authority：`NONE`
>
> 执行日期：`2026-08-30`

## 范围

验证 Codex 与 Gemini CLI Candidate Adapter 的生成一致性、部署安全、幂等性和当前本机 Runtime 可用性。

## 生成与临时部署

- Adapter Generator `--check`：`PASS`。
- Codex `.codex/config.toml` 临时目录首次部署：`CREATE`。
- Gemini `.gemini/settings.json` 临时目录首次部署：`CREATE`。
- 两个平台第二次部署：`UNCHANGED`。
- 替换现有配置时强制要求 Backup Directory：测试通过。

## 本项目部署

- `.codex/config.toml`：`DEPLOYED_CANDIDATE`。
- `.gemini/settings.json`：`DEPLOYED_CANDIDATE`。
- Hooks：未配置、未启用。
- 二次 Dry Run：两个文件均为 `UNCHANGED`。

## Codex Runtime

- CLI：已安装。
- 版本：`0.151.0-alpha.7.1`。
- Repository Detection：通过，识别根目录和 `main`。
- Config Parse：通过。
- Auth 与 WebSocket：通过。
- Runtime Smoke：`PASS`。
- 只读 Smoke Thread：`01a04f4a-dd10-7d00-b8cd-1234cb086258`。
- Agent 返回：`Personal AI OS / 1.1 / NONE / WORKING`，与 `SYSTEM.toml` 一致。

本机 Codex Doctor 同时报告 Memory 数据库无法打开、部分旧会话索引不一致。这些问题位于用户级 Codex Runtime，不是本项目配置生成错误，也未阻止项目只读 Smoke Test；未经单独授权不移动或修复用户数据库。

## Gemini CLI Runtime

- CLI：通过一次性官方包可用，版本 `0.57.0`；未执行全局安装。
- Native JSON：解析通过。
- 配置字段：依据当前官方 Configuration 文档生成。
- CLI 配置加载与帮助入口：通过。
- Runtime Smoke：`BLOCKED_EXTERNAL_DATA_AUTHORIZATION`。

真实模型 Smoke 会把项目指令和最小系统字段发送到 Google Gemini 服务。当前没有 Founder 对该外发行为的明确授权，因此安全审查在请求发出前阻止了执行；没有项目内容被发送。

## 结论

项目已经具备 Codex 与 Gemini CLI 配置的生成、Dry Run、部署、幂等和回滚基础；Codex Runtime Smoke 已通过，Gemini CLI 已加载配置但尚未获得外发授权，不能将 Candidate Adapter 晋升为 Canonical。
