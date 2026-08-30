# Personal AI OS V1.1
 
> 状态：`APPROVED_FOR_RELEASE`
>
> Approval Reference：`PAOS-REL-001`
>
> Release Version：`v1.1.0`

本仓库是 Personal AI OS V1.1 的本地 Canonical Control Plane Repository。

当前已完成 PAOS-007 批准的 V1.1 Minimum 体系建设，并通过全量 M1–M6 发布门禁审计，支持多 Agent（Codex & Gemini）协同、项目工厂脚手架以及离线恢复。

业务项目保持为独立项目和独立仓库，不存放在本仓库内部。

## 当前状态

- 阶段：`V1.1 Canonical Baseline`
- 发布门禁（M1–M6）：`ALL PASS`
- 核心模板：`01_templates/project-base-pack`（版本 `1.0.0` 已批准）
- 自动 Canonical Promotion：关闭（由 Founder / 总控显式授权）
- 自动部署：关闭
- 破坏性 GC：关闭

## 入口

- `PROJECT.md`：项目目标、范围和成功标准
- `AGENTS.md`：Agent 启动 Router Working
- `DECISIONS.md`：已确认和候选决策索引
- `SYSTEM.toml`：系统级机器可读元数据
- `00_system/`：治理、安全、Mode、Memory、Conversation、Lifecycle、Skills 与 Multi-Agent Sync
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

## 本地验证

- 推荐 Python：3.11+（见 `.python-version`）。
- Python 3.9/3.10 可安装 `requirements.txt` 中的 `tomli`；带有 pip vendored tomli 的环境也可直接运行。
- 一键本地离线验证：`python3 05_harness/ci_gate.py --profile local-offline`。
- 发布准备度：`python3 05_harness/ci_gate.py --profile release-readiness`；该命令不会执行 Tag、Push、部署或 Promotion。
