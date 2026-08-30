# Personal AI OS 独立可视化任务看板 (Dashboard)

本目录提供与主系统治理体系解耦的**可视化实时任务控制看板**。

---

## 🌟 核心特性

1. **实时热同步**：直接动态读取 `02_registry/tasks.toml`。一旦任务状态发生变更，看板无需重启，自动实时同步状态。
2. **多 Agent 筛选**：支持按 Codex、Claude Code、Gemini、ChatGPT 等维度实时过滤查看。
3. **完全解耦与独立**：不污染 `00_system/` ~ `06_deployment/` 核心治理结构。

---

## 🚀 启动方式

在终端运行以下一行命令即可自动在默认浏览器中打开看板：

```bash
python3 dashboard/server.py
```

服务将监听 `http://localhost:8765`。
按 `Ctrl + C` 可随时安全退出。
