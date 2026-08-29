# Personal AI OS V1.1

> 状态：`WORKING`
>
> Canonical Authority：`NONE`

本仓库正在建设为 Personal AI OS V1.1 的本地 Canonical Repository。

当前阶段只建立物理骨架、Working Draft 和验证机制。任何核心规则、模板、架构决定或配置在获得明确批准前，都不得标记为 `APPROVED` 或 `CANONICAL`。

业务项目保持为独立项目和独立仓库，不存放在本仓库内部。

## 当前状态

- 阶段：`Physical Architecture + Implementation Spec`
- Git 分支：`main`
- 正式 Release：尚未建立
- 自动 Canonical Promotion：关闭
- 自动部署：关闭
- 破坏性 GC：关闭

## 入口

- `PROJECT.md`：项目目标、范围和成功标准
- `AGENTS.md`：Agent 启动 Router Candidate
- `DECISIONS.md`：已确认和候选决策索引
- `SYSTEM.toml`：系统级机器可读元数据
- `00_system/`：治理、安全、Mode、Memory 和 Lifecycle
- `01_templates/`：逐项批准后的复用模板
- `02_registry/`：Projects、Tasks、Agents、Skills、Runtimes 和 Hooks
- `03_adapters/`：Codex、Gemini 等平台生成适配层
- `04_project_factory/`：新项目创建、初始化与验收
- `05_harness/`：执行、验证、交接与恢复
- `06_deployment/`：Agent 部署、备份和恢复
- `07_working/`：Spec、Candidate 与 Review
- `08_history/`：V1.0 等历史证据
- `09_archive/`：已替代但需追溯的材料
- `99_temp/`：Temp、Cache、Logs 与临时 Generated
