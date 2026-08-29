# Permissions Policy

> 状态：`WORKING`

- 使用完成当前 Task Card 所需的最小权限。
- Subagent 继承权限时不得扩大父任务授权范围。
- 读取、写入、网络、部署和外部消息属于不同权限域。
- 破坏性操作、外部发布和权限升级必须遵循明确授权。
- Adapter 和 Hook 必须声明其权限交集与失败方式。
