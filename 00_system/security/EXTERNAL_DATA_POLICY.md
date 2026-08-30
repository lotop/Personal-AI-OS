# External Data Policy

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

## 用途

定义向外部模型、连接器、远端服务、对象存储或第三方 API 发送项目数据前的授权边界。

## 默认规则

- 默认 `DENY_UNTIL_AUTHORIZED`。
- 本地配置加载、离线验证和不发送内容的 Capability Probe 不需要外部数据授权。
- 登录状态或已安装 CLI 不等于允许发送项目内容。
- 模板、AGENTS、Memory、Source、日志、文件名和系统元数据都可能包含私有信息，不得假定为公开数据。

## 授权记录最小字段

- Stable ID
- Provider / Destination
- Data Class 与精确 Payload 范围
- Purpose
- Retention / Training 已知条件或待验证项
- Owner / Approver
- Authorized At / Expires At
- One-shot 或 Reusable
- Revocation 方法

## 执行规则

- 只发送完成目标所需的最小数据。
- 授权未覆盖的新 Provider、新数据类别或新用途必须重新确认。
- Smoke Test 优先使用合成、非敏感 Payload，不发送真实项目正文。
- 日志只记录必要元数据和结果，不回写完整敏感 Payload。
- 授权被拒绝或不可验证时记录 `BLOCKED_EXTERNAL_DATA_AUTHORIZATION`，不得绕过。
