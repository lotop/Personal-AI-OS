# Physical Architecture V1.1

> 状态：`WORKING`
>
> Canonical Authority：`NONE`
>
> Owner：`paos-00-control`

## 目标

定义 Personal AI OS V1.1 的唯一仓库、目录职责、依赖方向、写入边界和部署边界，为后续模板、Project Factory 与 Agent Adapter 提供共同物理基础。

## 仓库拓扑

- `/Users/lotop/Personal-AI-OS`：本地候选 Canonical Repository。
- `main`：集成分支；未通过验证与 Founder Approval 的内容不得执行 Canonical Promotion。
- `task/*`：实现任务分支；并行写入时配合 Git Worktree。
- `origin`：私有远端灾备与协作副本，不取代本地 Canonical Authority。
- ChatGPT Project：讨论、Capture、研究和审批界面，不是文件系统 Source of Truth。

## 顶层结构

```text
Personal-AI-OS/
├── 00_system/             # 全局规则、状态、Mode、Security、Compatibility
├── 01_templates/          # 仅保存逐项批准后的复用模板
├── 02_registry/           # 人工维护的 TOML Registry
├── 03_adapters/           # 从批准规则生成的平台适配产物
├── 04_project_factory/    # 新项目创建、初始化与验收
├── 05_harness/            # 工作流、验证器、Hooks、迁移与恢复
├── 06_deployment/         # Agent 部署、备份、恢复和设备迁移
├── 07_working/            # Spec、Candidate 与 Review
├── 08_history/            # 历史证据与旧基线说明
├── 09_archive/            # 已替代但仍需追溯的材料
├── 99_temp/               # Temp、Cache、Logs 与 Generated 暂存
├── AGENTS.md              # Codex 等 Agent 的根级 Router Candidate
├── PROJECT.md             # 项目目标与范围
├── DECISIONS.md           # 决策索引
└── SYSTEM.toml            # 系统级机器可读入口
```

## 目录设计规则

1. 只有当子目录表达稳定语义、存在多个文件或具有独立生命周期时才建立子目录。
2. 单一说明文件优先提升到所属模块一级，避免一层目录只包含一个 Markdown。
3. `00_system/` 保留治理域子目录，因为各域后续包含规则、Schema 或 Registry。
4. `07_working/` 和 `99_temp/` 保留生命周期子目录，因为清理与权限规则不同。
5. `03_adapters/` 可以为每个平台建立子目录，因为平台原生文件名、格式和部署位置不同。

## 依赖方向

```text
00_system + 01_templates + 02_registry
                    ↓
          04_project_factory
                    ↓
             03_adapters
                    ↓
          05_harness + 06_deployment
```

- Adapter 不得反向成为规则来源。
- Harness 不得定义项目事实。
- Working、History、Archive 和 Temp 默认不参与运行时上下文。
- Project Factory 只能实例化已批准模板；未批准模板只能用于 Candidate 演练。

## 写入边界

- `00_system/`、`01_templates/`、`02_registry/`：总控或明确 Owner 写入。
- `03_adapters/`：生成器写入；人工修改必须回到 Source。
- `04_project_factory/`、`05_harness/`、`06_deployment/`：实现代码和规范经验证后写入。
- `07_working/`：允许 Working/Candidate/Review，不具有 Canonical Authority。
- `08_history/`、`09_archive/`：只追加可追溯材料，不静默覆盖。
- `99_temp/`：允许清理；破坏性 GC 默认关闭。

## 平台适配边界

- Codex：根级 `AGENTS.md` 是项目指令入口；项目部署配置使用 `.codex/config.toml` 或用户级配置，具体生成内容由 Codex Adapter 决定。
- Gemini CLI：默认使用层级 `GEMINI.md`；项目设置位于 `.gemini/settings.json`，因此 Gemini 原生 Adapter 使用 JSON，而非强行转换为 TOML。
- 其他 Agent：必须先完成官方能力核验，再登记为 `NATIVE`、`ADAPTER`、`MANUAL`、`UNSUPPORTED` 或 `UNVERIFIED`。

## 验收条件

- 顶层目录职责唯一且无循环依赖。
- 所有入口引用均存在。
- TOML 可解析，Stable ID 唯一。
- Source、Canonical、Generated、Working、Temp 边界可被验证器检查。
- Project Factory 与 Codex/Gemini Adapter 有明确部署位置和回滚路径。

## 当前未完成项

- V1.0 原始文件未取得，正式 Diff 尚不可证明。
- 首个 Project Base Template Pack 已形成可执行 Candidate 并通过 Provisional E2E，但尚未 Founder Approval。
- Codex/Gemini Candidate Adapter 已生成并部署；Codex Live Runtime 通过，Gemini 仅 Config Load 通过，Live Runtime 等待外部数据授权。
- 本地 Clean Clone 与 Offline Git Bundle 恢复已验证；Private Remote、外部资产、Credential 与完整 Host Recovery 尚未验证。
- Release Readiness 已按 PAOS-007 收敛为 M1–M6；旧 R0–R12/P1–P2 模型已归档，当前因 Template、恢复证据刷新与 Release Approval 保持 Blocked。
