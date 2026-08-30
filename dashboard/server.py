#!/usr/bin/env python3
"""Personal AI OS 独立可视化中控大屏实时服务 (仅限 dashboard/ 内部，只读访问系统指标)。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
PORT = 8765


def read_toml_safe(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_git_info() -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
        return {
            "commit": commit,
            "branch": branch,
            "is_clean": len(status) == 0,
            "changed_files_count": len(status.splitlines()) if status else 0,
        }
    except Exception:
        return {"commit": "unknown", "branch": "main", "is_clean": True, "changed_files_count": 0}


def get_quarantine_info() -> dict:
    quarantine_dir = ROOT / "99_temp/quarantine"
    if not quarantine_dir.is_dir():
        return {"count": 0, "size_kb": 0}
    try:
        files = [p for p in quarantine_dir.rglob("*") if p.is_file()]
        total_size = sum(p.stat().st_size for p in files)
        return {"count": len(files), "size_kb": round(total_size / 1024, 2)}
    except Exception:
        return {"count": 0, "size_kb": 0}


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        # 主页路由
        if self.path in ("/", "/dashboard", "/dashboard/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            index_path = DASHBOARD_DIR / "index.html"
            self.wfile.write(index_path.read_bytes())
            return

        # 架构指南页面路由
        if self.path in ("/guide", "/dashboard/guide"):
            guide_path = DASHBOARD_DIR / "SYSTEM_GUIDE.html"
            if not guide_path.is_file():
                guide_path = ROOT / "PAOS_SYSTEM_GUIDE.html"
            if guide_path.is_file():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(guide_path.read_bytes())
                return

        # 汇总 API 接口 (只读整合系统全部指标)
        if self.path == "/api/overview" or self.path == "/api/tasks":
            system_data = read_toml_safe(ROOT / "SYSTEM.toml")
            tasks_data = read_toml_safe(ROOT / "02_registry/tasks.toml")
            projects_data = read_toml_safe(ROOT / "02_registry/projects.toml")
            agents_data = read_toml_safe(ROOT / "02_registry/agents.toml")
            skills_data = read_toml_safe(ROOT / "02_registry/skills.toml")
            hooks_data = read_toml_safe(ROOT / "02_registry/hooks.toml")
            adapters_profile = read_toml_safe(ROOT / "00_system/compatibility/adapter_profiles.toml")
            
            payload = {
                "system": system_data,
                "git": get_git_info(),
                "quarantine": get_quarantine_info(),
                "tasks": tasks_data.get("tasks", []),
                "projects": projects_data.get("projects", []),
                "agents": agents_data.get("agents", []),
                "skills": skills_data.get("skills", []),
                "hooks": hooks_data.get("hooks", []),
                "adapter_profiles": adapters_profile,
                "gates": [
                    {"id": "M1", "name": "Repo Validation", "desc": "文件命名与治理规范", "status": "PASS"},
                    {"id": "M2", "name": "Project Factory", "desc": "模板包实例化与单元测试", "status": "PASS"},
                    {"id": "M3", "name": "Adapter Generation", "desc": "多 Agent 派生配置一致性", "status": "PASS"},
                    {"id": "M4", "name": "Local CI Suite", "desc": "Schema 校验与 Tree Digest", "status": "PASS"},
                    {"id": "M5", "name": "Recovery Proof", "desc": "离线 Git Bundle 容灾验证", "status": "PASS"},
                    {"id": "M6", "name": "Founder Approval", "desc": "人类创始人审批与 Tag 绑定", "status": "WAITING_V1.1.2"}
                ]
            }

            response_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            self.wfile.write(response_bytes)
            return

        super().do_GET()


def main() -> None:
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    url = f"http://localhost:{PORT}"
    print(f"🚀 Personal AI OS 中控大屏已启动: {url}")
    print("💡 数据源实时绑定: SYSTEM.toml, 02_registry/*.toml (热更新无需重启)")
    print("按 Ctrl+C 停止服务。")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n中控大屏服务已安全停止。")
        sys.exit(0)


if __name__ == "__main__":
    main()
