# Personal AI OS 独立可视化任务看板 (Dashboard)

> 资产类别：`GENERATED`
>
> 状态：`WORKING`
>
> 本目录不是 Source of Truth，只读展示 Registry 与门禁结果，不参与 Canonical Promotion。

本目录提供与主系统治理体系解耦的**可视化实时任务控制看板**。

---

## 🌟 核心特性

1. **实时热同步**：直接动态读取 `02_registry/tasks.toml`。一旦任务状态发生变更，看板无需重启，自动实时同步状态。
2. **多 Agent 筛选**：支持按 Codex、Claude Code、Antigravity CLI、ChatGPT 等维度实时过滤查看。
3. **真实门禁数据**：`/api/overview` 的 `gates` 与 `release_overall` 直接调用 `05_harness/release_audit.py`，不使用硬编码状态。
4. **完全解耦与独立**：不污染 `00_system/` ~ `06_deployment/` 核心治理结构。

---

## 🚀 启动方式

在终端运行以下一行命令即可自动在默认浏览器中打开看板：

```bash
python3 dashboard/server.py
```

服务将监听 `http://127.0.0.1:8765`。
按 `Ctrl + C` 可随时安全退出。

---

## 🔒 安全边界

- **仅绑定回环地址** `127.0.0.1`，不对局域网暴露。看板会读出 Registry、Git 状态与门禁结果。
- **静态根限定在 `dashboard/`**，仓库根与 `.git/` 不可通过 HTTP 访问。
- **不设置 `Access-Control-Allow-Origin`**，其他站点的页面无法跨域读取 `/api/overview`。
- 服务只读：不提供任何写入、批准、部署或删除接口。
