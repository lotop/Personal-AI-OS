# Personal AI OS V1.1

> 状态：`APPROVED_FOR_RELEASE`
>
> Approval Reference：`PAOS-REL-001`

## Objective

建立一套可长期维护、可验证、可回滚的多项目、多 Agent、跨设备个人 AI 工作系统。

## Scope

- Global Governance 与 Security
- Mode System 与最小充分上下文
- Project Factory 与核心 Templates
- Memory、Conversation Close 与 Asset Lifecycle
- Skills、Hooks、Adapters 与 Capability Registry
- Harness、Deployment、Backup 与 Recovery

## Non-goals

- 不把业务项目本体存入本仓库。
- 不以某个 Agent 或聊天平台作为最终知识仓库。
- 不在 V1.1 初期自动批准、自动发布或执行破坏性 GC。

## Current Phase

`V1.1 Minimum Implementation`

## Success Criteria

- 存在一个可恢复的本地 Git Canonical Repository。
- 核心模板均经过逐项批准。
- Canonical 与 Generated、Working、Temp 边界可以自动验证。
- 不同 Agent 的能力差异有明确记录和降级路径。
- 项目创建、执行、验证、交接与清理可以重复运行。
