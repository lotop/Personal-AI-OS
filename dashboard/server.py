#!/usr/bin/env python3
"""Personal AI OS 独立可视化中控大屏实时服务 (仅限 dashboard/ 内部，只读访问系统指标)。"""

from __future__ import annotations

import json
import subprocess
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
# 只监听回环地址：看板会读出 Registry 与 Git 状态，不应暴露到局域网。
HOST = "127.0.0.1"
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


def get_release_state() -> dict:
    """真实调用 Release Audit，不展示硬编码门禁状态。"""
    try:
        result = subprocess.run(
            [sys.executable, "05_harness/release_audit.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return {"overall": "UNKNOWN", "gates": []}
        return json.loads(result.stdout)
    except Exception:
        return {"overall": "UNKNOWN", "gates": []}


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 静态根限定在 dashboard/，避免把整个仓库（含 .git）当作可下载目录。
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

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

        # 架构指南页面路由；指南文件不存在时明确 404，不落回目录列举。
        if self.path in ("/guide", "/dashboard/guide"):
            guide_path = DASHBOARD_DIR / "SYSTEM_GUIDE.html"
            if guide_path.is_file():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(guide_path.read_bytes())
            else:
                self.send_error(404, "SYSTEM_GUIDE.html not present")
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
            }

            release_state = get_release_state()
            payload["release_overall"] = release_state.get("overall", "UNKNOWN")
            payload["gates"] = release_state.get("gates", [])

            response_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            self.wfile.write(response_bytes)
            return

        super().do_GET()


def main() -> None:
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    url = f"http://{HOST}:{PORT}"
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
