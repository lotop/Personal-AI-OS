#!/usr/bin/env python3
"""Personal AI OS V1.1 仓库最小验证器。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GIT_ENV = {
    **os.environ,
    "HOME": "/dev/null",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "XDG_CONFIG_HOME": "/dev/null",
}

from schema_validation import unsupported_keywords, validate_instance

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 兼容
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        try:
            import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]
        except ModuleNotFoundError as exc:
            raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "00_system",
    "01_templates",
    "02_registry",
    "03_adapters",
    "04_project_factory",
    "05_harness",
    "06_deployment",
    "07_working/specs",
    "07_working/candidates",
    "07_working/reviews",
    "08_history",
    "09_archive",
    "99_temp",
]

REQUIRED_FILES = [
    "README.md",
    "PROJECT.md",
    "AGENTS.md",
    "CLAUDE.md",
    "DECISIONS.md",
    "CHANGELOG.md",
    "SYSTEM.toml",
    ".codex/config.toml",
    ".claude/settings.json",
    ".gemini/settings.json",
    "04_project_factory/FACTORY_SPEC.md",
    "06_deployment/CODEX_DEPLOYMENT.md",
    "06_deployment/CLAUDE_CODE_DEPLOYMENT.md",
    "06_deployment/ANTIGRAVITY_DEPLOYMENT.md",
    "00_system/security/EXTERNAL_DATA_POLICY.md",
    "00_system/compatibility/capabilities.toml",
]

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_toml(path: Path, report: Report) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        report.error(f"TOML 解析失败: {path.relative_to(ROOT)}: {exc}")
        return {}


def validate_required(report: Report) -> None:
    for relative in REQUIRED_DIRS:
        if not (ROOT / relative).is_dir():
            report.error(f"缺少目录: {relative}")
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            report.error(f"缺少文件: {relative}")


def validate_structured_files(report: Report) -> dict[Path, dict]:
    parsed: dict[Path, dict] = {}
    def operational(path: Path) -> bool:
        relative = path.relative_to(ROOT)
        if relative.parts[0] in {".git", "08_history", "09_archive", "99_temp"}:
            return False
        if relative.parts[0] == "07_working" and relative.parts[1:2] != ("candidates",):
            return False
        return True

    for path in sorted(item for item in ROOT.rglob("*.toml") if operational(item)):
        parsed[path] = load_toml(path, report)
    for path in sorted(item for item in ROOT.rglob("*.json") if operational(item)):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            report.error(f"JSON 解析失败: {path.relative_to(ROOT)}: {exc}")
    for path in sorted(item for item in ROOT.rglob("*.py") if operational(item)):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            report.error(f"Python 语法失败: {path.relative_to(ROOT)}: {exc}")
    return parsed


def validate_schema_shapes(report: Report) -> None:
    """Schema 本身只能使用 schema_validation.py 真正实现的关键字。"""
    for path in sorted((ROOT / "00_system/schemas").glob("*.schema.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            report.error(f"Schema 解析失败: {path.relative_to(ROOT)}: {exc}")
            continue
        for error in unsupported_keywords(schema):
            report.error(f"Schema 不受支持 {path.relative_to(ROOT)}: {error}")


def validate_schema_bindings(parsed: dict[Path, dict], report: Report) -> None:
    schema_root = ROOT / "00_system/schemas"
    bindings = parsed.get(schema_root / "bindings.toml", {}).get("bindings", [])
    for binding in bindings:
        schema_path = schema_root / binding["schema"]
        if not schema_path.is_file():
            report.error(f"Schema 不存在: {binding['schema']}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if "path" in binding:
            targets = [ROOT / binding["path"]]
        else:
            targets = sorted(ROOT.glob(binding["path_glob"]))
        for target in targets:
            if not target.is_file():
                report.error(f"Schema 绑定目标不存在: {target.relative_to(ROOT)}")
                continue
            if binding["format"] == "toml":
                instance = parsed.get(target, load_toml(target, report))
            else:
                instance = json.loads(target.read_text(encoding="utf-8"))
            for error in validate_instance(instance, schema):
                report.error(f"Schema 失败 {target.relative_to(ROOT)}: {error}")

    adapter_schema = json.loads((schema_root / "adapter-manifest.schema.json").read_text())
    for target in sorted((ROOT / "03_adapters").glob("*/manifest.toml")):
        instance = parsed.get(target, load_toml(target, report))
        for error in validate_instance(instance, adapter_schema):
            report.error(f"Schema 失败 {target.relative_to(ROOT)}: {error}")


def validate_deployed_adapters(parsed: dict[Path, dict], report: Report) -> None:
    for manifest_path in sorted((ROOT / "03_adapters").glob("*/manifest.toml")):
        manifest = parsed.get(manifest_path, load_toml(manifest_path, report))
        for record in manifest.get("files", []):
            source_rel = Path(record["source"])
            target_rel = Path(record["target"])
            if source_rel.is_absolute() or ".." in source_rel.parts:
                report.error(f"Adapter source 越界: {manifest_path.relative_to(ROOT)}")
                continue
            if target_rel.is_absolute() or ".." in target_rel.parts:
                report.error(f"Adapter target 越界: {manifest_path.relative_to(ROOT)}")
                continue
            source = manifest_path.parent / source_rel
            target = ROOT / target_rel
            if not target.is_file():
                report.error(f"Adapter 尚未部署: {target_rel}")
            elif source.read_bytes() != target.read_bytes():
                report.error(f"已部署 Adapter 漂移: {target_rel}")


def validate_unique_ids(parsed: dict[Path, dict], report: Report) -> None:
    collections = {
        "02_registry/tasks.toml": "tasks",
        "02_registry/projects.toml": "projects",
        "02_registry/agents.toml": "agents",
        "02_registry/hooks.toml": "hooks",
        "00_system/modes/registry.toml": "modes",
        "00_system/compatibility/platforms.toml": "platforms",
    }
    for relative, key in collections.items():
        data = parsed.get(ROOT / relative, {})
        records = data.get(key, [])
        ids = [record.get("id") for record in records]
        if any(value is None for value in ids):
            report.error(f"{relative} 存在缺少 id 的记录")
        if len(ids) != len(set(ids)):
            report.error(f"{relative} 存在重复 id")

    capability_path = ROOT / "00_system/compatibility/capabilities.toml"
    capabilities = parsed.get(capability_path, {}).get("capability_evidence", [])
    identities = [(item.get("id"), item.get("platform")) for item in capabilities]
    if len(identities) != len(set(identities)):
        report.error("capabilities.toml 存在重复 capability/platform")
    for item in capabilities:
        if item.get("runtime_verified") and not item.get("config_loaded"):
            report.error(f"Capability {item.get('id')}/{item.get('platform')} Runtime PASS 但 Config 未加载")
        if not item.get("runtime_verified") and not item.get("blocked_reason"):
            report.error(f"Capability {item.get('id')}/{item.get('platform')} 未验证但缺少 blocked_reason")


def validate_tasks(parsed: dict[Path, dict], report: Report) -> None:
    relative = "02_registry/tasks.toml"
    data = parsed.get(ROOT / relative, {})
    allowed_statuses = set(data.get("allowed_statuses", []))
    for task in data.get("tasks", []):
        task_id = task.get("id", "<unknown>")
        if task.get("status") not in allowed_statuses:
            report.error(f"{task_id} 的 status 非法")
        validation = task.get("validation", [])
        if not isinstance(validation, list) or len(validation) != len(set(validation)):
            report.error(f"{task_id} 的 validation 必须是无重复项列表")


def validate_registry_references(parsed: dict[Path, dict], report: Report) -> None:
    tasks = parsed.get(ROOT / "02_registry/tasks.toml", {}).get("tasks", [])
    task_ids = {item.get("id") for item in tasks}
    skills = parsed.get(ROOT / "02_registry/skills.toml", {}).get("skills", [])
    for skill in skills:
        skill_id = skill.get("id", "<unknown>")
        owner = skill.get("owner")
        if owner not in task_ids:
            report.error(f"Skill {skill_id} owner 未登记为 Task: {owner}")
        skill_rel_path = skill.get("path")
        if not skill_rel_path:
            report.error(f"Skill {skill_id} 缺少 path")
            continue
        skill_file = ROOT / skill_rel_path
        if skill_file.is_symlink():
            report.error(f"Skill {skill_id} 路径不得为 symlink: {skill_rel_path}")
        elif not skill_file.is_file():
            report.error(f"Skill {skill_id} 对应文件不存在: {skill_rel_path}")
        else:
            text = skill_file.read_text(encoding="utf-8")
            if not text.startswith("---"):
                report.error(f"Skill {skill_id} 缺少标准 YAML Frontmatter")
            else:
                parts = text.split("---", 2)
                if len(parts) < 3 or "name:" not in parts[1] or "description:" not in parts[1]:
                    report.error(f"Skill {skill_id} Frontmatter 必须包含 name 与 description")

    hooks = parsed.get(ROOT / "02_registry/hooks.toml", {}).get("hooks", [])
    for hook in hooks:
        owner = hook.get("owner")
        if owner not in task_ids:
            report.error(f"Hook {hook.get('id', '<unknown>')} owner 未登记为 Task: {owner}")
        if hook.get("implementation_status") == "NOT_IMPLEMENTED":
            if hook.get("enabled") is not False or hook.get("config_load") != "NOT_RUN" or hook.get("runtime_test") != "NOT_RUN":
                report.error(f"未实现 Hook 不得启用或声明已加载/运行: {hook.get('id', '<unknown>')}")
        if hook.get("blocking") is False and any("DENY" in effect for effect in hook.get("side_effects", [])):
            report.error(f"Non-blocking Hook 不得声明 DENY 副作用: {hook.get('id', '<unknown>')}")

    runtimes = parsed.get(ROOT / "02_registry/runtimes.toml", {}).get("runtimes", [])
    runtime_versions = {item.get("platform"): item.get("version") for item in runtimes}
    capabilities = parsed.get(
        ROOT / "00_system/compatibility/capabilities.toml", {}
    ).get("capability_evidence", [])
    for capability in capabilities:
        platform = capability.get("platform")
        version = capability.get("version")
        if version and platform in runtime_versions and version != runtime_versions[platform]:
            report.error(
                f"Capability {capability.get('id', '<unknown>')}/{platform} version 与 Runtime Registry 漂移: "
                f"{version} != {runtime_versions[platform]}"
            )


def validate_baseline_consistency(parsed: dict[Path, dict], report: Report) -> None:
    """SYSTEM.toml 的已批准基线必须与 Project Registry 中的本仓库记录一致。"""
    system = parsed.get(ROOT / "SYSTEM.toml", {})
    baseline = system.get("approved_baseline")
    if not baseline:
        return

    version = baseline.get("version")
    tag = baseline.get("git_tag")
    if version and tag and tag != f"v{version}":
        report.error(f"approved_baseline.git_tag 与 version 不一致: {tag} != v{version}")

    projects = parsed.get(ROOT / "02_registry/projects.toml", {}).get("projects", [])
    self_records = [item for item in projects if item.get("repository_ref") == "self"]
    if len(self_records) != 1:
        report.error("projects.toml 必须且只能有一条 repository_ref = \"self\" 记录")
        return

    record = self_records[0]
    if record.get("approved_version") != version:
        report.error(
            f"projects.toml approved_version 与 SYSTEM.toml 基线漂移: "
            f"{record.get('approved_version')} != {version}"
        )
    if record.get("approved_tag") != tag:
        report.error(
            f"projects.toml approved_tag 与 SYSTEM.toml 基线漂移: "
            f"{record.get('approved_tag')} != {tag}"
        )


def validate_lifecycle(parsed: dict[Path, dict], report: Report) -> None:
    data = parsed.get(ROOT / "00_system/lifecycle/states.toml", {})
    classes = set(data.get("artifact_classes", []))
    maturity = set(data.get("maturity_states", []))
    if "SOURCE" not in classes:
        report.error("SOURCE 必须属于 artifact_classes")
    if "SOURCE" in maturity:
        report.error("SOURCE 不得属于 maturity_states")
    if maturity != {"WORKING", "APPROVED", "ARCHIVED"}:
        report.error("maturity_states 必须等于 V1.1 Minimum 状态集合")
    legacy_axes = {"origin_classes", "governance_states", "lifecycle_states", "materialization_classes"}
    if legacy_axes & data.keys():
        report.error("V1.1 Minimum 不再维护四维资产状态")


def validate_template_packs(parsed: dict[Path, dict], report: Report) -> None:
    factory_config = parsed.get(ROOT / "04_project_factory/factory.toml", {})
    pack_kinds = factory_config.get("template_pack_kinds", {})
    approved_digests = factory_config.get("approved_template_pack_digests", {})
    known_pack_ids: set[str] = set()
    approved_pack_ids: set[str] = set()
    for base in (ROOT / "01_templates", ROOT / "07_working/candidates"):
        for manifest_path in sorted(base.glob("*/template.toml")):
            data = parsed.get(manifest_path, load_toml(manifest_path, report))
            pack_id = data.get("pack_id")
            if pack_id:
                known_pack_ids.add(pack_id)
                if pack_id not in pack_kinds:
                    report.error(f"Template Pack 未登记 Factory 用途: {pack_id}")
                elif pack_kinds[pack_id] not in {"PROJECT_SCAFFOLD", "ARTIFACT_LIBRARY"}:
                    report.error(f"Template Pack Factory 用途非法: {pack_id}: {pack_kinds[pack_id]}")
            state = data.get("artifact_state")
            if base.name == "01_templates" and (state != "APPROVED" or not data.get("approval_reference")):
                report.error(f"正式 Template Pack 缺少可验证批准: {manifest_path.relative_to(ROOT)}")
            if base.name == "01_templates" and pack_id:
                approved_pack_ids.add(pack_id)
            if base.name == "candidates" and state != "WORKING":
                report.error(f"Working 区 Template Pack 状态越权: {manifest_path.relative_to(ROOT)}")
            records = data.get("files", [])
            sources = [record.get("source") for record in records]
            # 同一目标路径只有在 primary_types 互斥时才允许重复：
            # 每个项目类型各自产出一份，单次实例化仍只写一个文件。
            claims: dict[str, list[set[str] | None]] = {}
            for record in records:
                destination = record.get("destination")
                allowed = record.get("primary_types")
                claims.setdefault(destination, []).append(
                    set(allowed) if isinstance(allowed, list) else None
                )
            for destination, type_sets in claims.items():
                if len(type_sets) == 1:
                    continue
                if any(item is None for item in type_sets):
                    report.error(
                        f"Template Pack 目标路径重复且存在无类型过滤记录: "
                        f"{manifest_path.relative_to(ROOT)}: {destination}"
                    )
                    continue
                seen: set[str] = set()
                for item in type_sets:
                    assert item is not None
                    if item & seen:
                        report.error(
                            f"Template Pack 目标路径在同一项目类型下重复: "
                            f"{manifest_path.relative_to(ROOT)}: {destination}"
                        )
                        break
                    seen |= item
            entries = sorted(manifest_path.parent.rglob("*"))
            for path in entries:
                relative = path.relative_to(manifest_path.parent)
                if path.is_symlink():
                    report.error(f"Template Pack 不得包含 symlink: {manifest_path.relative_to(ROOT)}: {relative}")
                elif not path.is_dir() and not path.is_file():
                    report.error(f"Template Pack 包含特殊文件: {manifest_path.relative_to(ROOT)}: {relative}")
            actual = {
                str(path.relative_to(manifest_path.parent))
                for path in entries
                if path.is_file() and not path.is_symlink() and path.name != "template.toml"
            }
            undeclared = sorted(actual - set(sources))
            if undeclared:
                report.error(f"Template Pack 存在未登记文件: {manifest_path.relative_to(ROOT)}: {', '.join(undeclared)}")
            for source in sources:
                if not source or not (manifest_path.parent / source).is_file():
                    report.error(f"Template Pack 来源缺失: {manifest_path.relative_to(ROOT)}: {source}")
            if base.name == "01_templates" and pack_id:
                digest = hashlib.sha256()
                for path in entries:
                    if path.is_symlink() or path.is_dir() or not path.is_file():
                        continue
                    relative = path.relative_to(manifest_path.parent).as_posix()
                    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    digest.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
                expected = approved_digests.get(pack_id)
                if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    report.error(f"Approved Template Pack 缺少 Digest 登记: {pack_id}")
                elif digest.hexdigest() != expected:
                    report.error(f"Approved Template Pack Digest 不匹配: {pack_id}")
    unknown_routes = sorted(set(pack_kinds) - known_pack_ids)
    if unknown_routes:
        report.error("Factory 存在无对应 Template Pack 的用途路由: " + ", ".join(unknown_routes))
    extra_digests = sorted(set(approved_digests) - approved_pack_ids)
    if extra_digests:
        report.error("Factory 存在无对应 Approved Pack 的 Digest: " + ", ".join(extra_digests))


def validate_secrets(report: Report) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name == ".DS_Store":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                report.error(f"疑似 Secret: {path.relative_to(ROOT)}")


def validate_work_logs(parsed: dict[Path, dict], report: Report) -> None:
    date_field = re.compile(
        r"^> (?:日期|执行日期|审计日期|生成时间)：`[0-9]{4}-[0-9]{2}-[0-9]{2}`$",
        re.MULTILINE,
    )
    state_field = re.compile(r"^> 状态：`([A-Z_]+)`$", re.MULTILINE)

    # 工作日志既可能是资产（成熟度状态），也可能是 Task Card（任务状态）。
    # 两套词汇表都必须来自已登记的来源，不允许临时发明状态值。
    maturity = set(parsed.get(ROOT / "00_system/lifecycle/states.toml", {}).get("maturity_states", []))
    task_statuses = set(parsed.get(ROOT / "02_registry/tasks.toml", {}).get("allowed_statuses", []))
    allowed = maturity | task_statuses
    if not allowed:
        report.error("无法解析工作日志允许的状态词汇表")
        return

    for path in sorted((ROOT / "07_working/reviews").glob("*.md")):
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:20])
        if not date_field.search(header):
            report.error(f"工作日志缺少日期字段: {path.relative_to(ROOT)}")
        match = state_field.search(header)
        if not match:
            report.error(f"工作日志缺少状态字段: {path.relative_to(ROOT)}")
        elif match.group(1) not in allowed:
            report.error(
                f"工作日志状态不在已登记词汇表中: {path.relative_to(ROOT)}: {match.group(1)}"
            )


def validate_git(report: Report) -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        env=GIT_ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        report.error("当前目录不是可用 Git Repository")
    elif status.stdout.strip():
        report.warn("Git Working Tree 尚未形成干净 Baseline")

    remote = subprocess.run(
        ["git", "remote"], cwd=ROOT, env=GIT_ENV, text=True, capture_output=True, check=False
    )
    if "origin" not in remote.stdout.split():
        report.warn("尚未配置 origin")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="将 Warning 视为失败")
    args = parser.parse_args()

    report = Report()
    validate_required(report)
    parsed = validate_structured_files(report)
    validate_schema_shapes(report)
    validate_schema_bindings(parsed, report)
    validate_deployed_adapters(parsed, report)
    validate_unique_ids(parsed, report)
    validate_tasks(parsed, report)
    validate_registry_references(parsed, report)
    validate_baseline_consistency(parsed, report)
    validate_lifecycle(parsed, report)
    validate_template_packs(parsed, report)
    validate_secrets(report)
    validate_work_logs(parsed, report)
    validate_git(report)

    print(f"ERRORS={len(report.errors)} WARNINGS={len(report.warnings)}")
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"WARN: {message}")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
