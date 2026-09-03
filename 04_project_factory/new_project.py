#!/usr/bin/env python3
"""Personal AI OS 项目创建交互向导。

本向导只是已批准工具的交互外壳：参数收集、预检与流程编排在这里，
真正的创建、校验与部署仍然由 `create_project.py` 与 `deploy_adapter.py` 执行。
所有取值范围与校验规则从 Canonical 来源读取或直接复用，不在本文件内复制或分叉。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

FACTORY_DIR = Path(__file__).resolve().parent
OS_ROOT = FACTORY_DIR.parent
TEMPLATES_ROOT = OS_ROOT / "01_templates"
CREATE_SCRIPT = FACTORY_DIR / "create_project.py"
DEPLOY_SCRIPT = OS_ROOT / "06_deployment" / "deploy_adapter.py"
RECORD_DIR = Path("99_temp/deploy_records")

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

# 复用 Canonical 校验规则，避免在向导中形成第二份定义。
sys.path.insert(0, str(FACTORY_DIR))
sys.path.insert(0, str(DEPLOY_SCRIPT.parent))
from create_project import SLUG_PATTERN  # noqa: E402
from deploy_adapter import AUTHORIZATION_PATTERN  # noqa: E402

# 需要注入目标项目的 Adapter。Claude Code 入口由 Project Base Pack 直接生成，不在此列。
ADAPTERS = [
    ("Codex", "03_adapters/codex/manifest.toml"),
    ("Antigravity", "03_adapters/antigravity-cli/manifest.toml"),
]

BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"


def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


COLOR = supports_color()


def paint(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if COLOR else text


def title(text: str) -> None:
    print()
    print(paint(f"── {text} ", BOLD) + paint("─" * max(0, 56 - len(text)), DIM))


def info(text: str) -> None:
    print(paint("  " + text, DIM))


def ok(text: str) -> None:
    print(paint("  ✓ ", GREEN) + text)


def warn(text: str) -> None:
    print(paint("  ! ", YELLOW) + text)


def fail(text: str) -> None:
    print(paint("  ✗ ", RED) + text)


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            raw = input(paint(f"  {prompt}{suffix}: ", CYAN)).strip()
        except EOFError:
            raise KeyboardInterrupt from None
        if raw:
            return raw
        if default is not None:
            return default
        fail("此项不能为空。")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        try:
            raw = input(paint(f"  {prompt} [{hint}]: ", CYAN)).strip().lower()
        except EOFError:
            raise KeyboardInterrupt from None
        if not raw:
            return default
        if raw in {"y", "yes", "是"}:
            return True
        if raw in {"n", "no", "否"}:
            return False
        fail("请输入 y 或 n。")


def choose_one(prompt: str, options: list[str], descriptions: dict[str, str] | None = None) -> str:
    for index, option in enumerate(options, start=1):
        note = f"  {paint(descriptions[option], DIM)}" if descriptions and option in descriptions else ""
        print(f"    {paint(str(index).rjust(2), BOLD)}. {option}{note}")
    while True:
        raw = ask(prompt, default="1")
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        if raw in options:
            return raw
        fail(f"请输入 1-{len(options)} 之间的序号。")


def choose_many(prompt: str, options: list[str]) -> list[str]:
    for index, option in enumerate(options, start=1):
        print(f"    {paint(str(index).rjust(2), BOLD)}. {option}")
    while True:
        raw = ask(prompt, default="")
        if not raw:
            return []
        tokens = [token.strip() for token in raw.replace("，", ",").split(",") if token.strip()]
        picked: list[str] = []
        bad = []
        for token in tokens:
            if token.isdigit() and 1 <= int(token) <= len(options):
                picked.append(options[int(token) - 1])
            elif token in options:
                picked.append(token)
            else:
                bad.append(token)
        if bad:
            fail(f"无法识别：{', '.join(bad)}。用逗号分隔序号，或直接回车表示不选。")
            continue
        return sorted(set(picked))


def load_factory_config() -> dict:
    return tomllib.loads((FACTORY_DIR / "factory.toml").read_text(encoding="utf-8"))


def discover_scaffold_packs(config: dict) -> list[tuple[str, Path, str, str]]:
    """返回 (pack_id, 路径, 版本, 状态)，仅保留用途为 PROJECT_SCAFFOLD 的 Pack。"""
    kinds = config.get("template_pack_kinds", {})
    found = []
    for manifest_path in sorted(TEMPLATES_ROOT.glob("*/template.toml")):
        try:
            manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        pack_id = manifest.get("pack_id")
        if kinds.get(pack_id) != "PROJECT_SCAFFOLD":
            continue
        found.append(
            (pack_id, manifest_path.parent, manifest.get("version", "?"), manifest.get("artifact_state", "?"))
        )
    return found


def check_target(target: Path) -> tuple[bool, str]:
    """镜像 create_project.validate_target 的检查，用于提前给出可读提示。

    真正的强制仍由 create_project.py 执行；此处失败只是让用户少跑一次。
    """
    resolved = target.expanduser().resolve()
    if resolved == OS_ROOT or OS_ROOT in resolved.parents:
        return False, "目标不能位于 Personal AI OS 仓库内部。"
    if resolved.exists() or resolved.is_symlink():
        return False, "目标路径已经存在；工厂不执行隐式合并，请换一个名字或先删除。"
    for parent in (resolved.parent, *resolved.parents):
        if (parent / ".git").exists():
            return False, f"目标不能嵌套在现有 Git 仓库内：{parent}"
    if not resolved.parent.exists():
        return False, f"MISSING_PARENT::{resolved.parent}"
    if not resolved.parent.is_dir():
        return False, f"父路径不是目录：{resolved.parent}"
    return True, ""


def run(command: list[str], cwd: Path) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return result.returncode, result.stdout, result.stderr


def show_command(command: list[str]) -> None:
    rendered = []
    for token in command:
        rendered.append(f'"{token}"' if " " in token else token)
    print(paint("  $ " + " ".join(rendered), DIM))


def collect() -> dict:
    config = load_factory_config()

    title("1/7  模板包")
    packs = discover_scaffold_packs(config)
    approved = [pack for pack in packs if pack[3] == "APPROVED"]
    if not approved:
        fail("没有找到状态为 APPROVED 的 PROJECT_SCAFFOLD 模板包，无法继续。")
        raise SystemExit(1)
    if len(approved) == 1:
        pack_id, pack_path, version, state = approved[0]
        ok(f"使用唯一已批准脚手架模板包：{pack_id} {version}（{state}）")
    else:
        labels = [f"{p[0]} {p[2]}（{p[3]}）" for p in approved]
        picked = choose_one("选择模板包", labels)
        pack_id, pack_path, version, state = approved[labels.index(picked)]

    title("2/7  项目标识")
    info("2-63 位小写字母、数字或连字符，且必须以字母或数字开头。")
    while True:
        project_id = ask("project-id", default="demo-test")
        if SLUG_PATTERN.fullmatch(project_id):
            break
        fail("格式不符合要求（不能有大写、下划线、空格或中文）。")

    title("3/7  基本信息")
    name = ask("项目名称（可用中文）", default=project_id)
    owner = ask("负责人", default=os.environ.get("USER") or "lotop")

    title("4/7  主项目类型")
    primary_type = choose_one("选择序号", list(config["primary_types"]))

    title("5/7  分类标签 overlay（可选）")
    warn("overlay 目前只做取值校验并记入 project.toml 与 .paos-init.json，")
    warn("不会改变生成的任何文件内容。差异化模板尚未实现。")
    info("多选用逗号分隔（如 1,3），直接回车表示不选。")
    overlays = choose_many("选择序号", list(config["allowed_overlays"]))

    title("6/7  目标路径")
    info("请输入绝对路径（可用 ~ 开头）。")
    default_target = str(Path.home() / "Projects" / project_id)
    while True:
        raw_target = ask("目标路径", default=default_target)
        target = Path(raw_target).expanduser()
        if not target.is_absolute():
            # 相对路径会相对当前工作目录解析；从 Personal AI OS 目录启动向导时
            # 极易误判为“建在仓库内部”，这里直接拒绝并说明原因。
            fail("这是相对路径，会相对当前目录解析。请输入以 / 或 ~ 开头的绝对路径。")
            continue
        good, message = check_target(target)
        if message.startswith("MISSING_PARENT::"):
            parent = Path(message.split("::", 1)[1])
            warn(f"父目录不存在：{parent}")
            if not ask_yes_no(f"创建父目录 {parent} ？", default=True):
                fail("工厂不会隐式创建多级父目录，请换一个路径。")
                continue
            parent.mkdir(parents=True, exist_ok=True)
            ok(f"已创建 {parent}")
            # 只重新校验同一个路径，不再重复询问，避免用户以为输错了。
            good, message = check_target(target)
        if good:
            ok(f"路径可用：{target.resolve()}")
            break
        fail(message)

    title("7/7  可选步骤")
    init_git = ask_yes_no("初始化 Git 仓库（git init -b main）？", default=True)
    first_commit = ask_yes_no("创建后自动做首次提交？", default=True) if init_git else False
    deploy = ask_yes_no("为新项目注入 Codex 与 Antigravity 适配器？", default=True)
    authorization_ref = ""
    if deploy:
        # 授权引用规则为大写起始的受限字符集；project-id 是小写，必须转换后使用。
        suggested = f"PAOS-INIT-{project_id.upper()}"
        while True:
            authorization_ref = ask("部署单次授权引用", default=suggested)
            if AUTHORIZATION_PATTERN.fullmatch(authorization_ref):
                break
            fail("授权引用必须以大写字母或数字开头，且只含大写字母、数字与 . _ : - 共 3-128 位。")

    return {
        "pack_id": pack_id,
        "pack_path": pack_path,
        "pack_version": version,
        "project_id": project_id,
        "name": name,
        "owner": owner,
        "primary_type": primary_type,
        "overlays": overlays,
        "target": target,
        "init_git": init_git,
        "first_commit": first_commit,
        "deploy": deploy,
        "authorization_ref": authorization_ref,
    }


def build_create_command(answers: dict, apply: bool) -> list[str]:
    command = [
        sys.executable,
        str(CREATE_SCRIPT),
        "--template-pack",
        str(answers["pack_path"]),
        "--target",
        str(answers["target"]),
        "--project-id",
        answers["project_id"],
        "--name",
        answers["name"],
        "--owner",
        answers["owner"],
        "--primary-type",
        answers["primary_type"],
    ]
    for overlay in answers["overlays"]:
        command += ["--overlay", overlay]
    if answers["init_git"]:
        command.append("--git")
    if apply:
        command.append("--apply")
    return command


def summarize(answers: dict) -> None:
    title("确认")
    rows = [
        ("模板包", f"{answers['pack_id']} {answers['pack_version']}"),
        ("project-id", answers["project_id"]),
        ("项目名称", answers["name"]),
        ("负责人", answers["owner"]),
        ("主项目类型", answers["primary_type"]),
        ("overlay", ", ".join(answers["overlays"]) or "（无）"),
        ("目标路径", str(answers["target"].expanduser())),
        ("Git 初始化", "是" if answers["init_git"] else "否"),
        ("首次提交", "是" if answers["first_commit"] else "否"),
        ("部署适配器", answers["authorization_ref"] if answers["deploy"] else "否"),
    ]
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"  {paint(label.ljust(width), BOLD)}  {value}")


def report_plan(stdout: str) -> None:
    import json

    body = stdout.split("\n", 1)[1] if stdout.startswith("DRY_RUN") else stdout
    try:
        plan = json.loads(body)
    except json.JSONDecodeError:
        info("（无法解析计划 JSON，已跳过摘要）")
        return
    ok(f"模板状态：{plan.get('template_state')}（正式创建只接受 APPROVED）")
    ok(f"模板包 Digest：{plan.get('template_pack_digest', '')[:16]}…")
    ok(f"目标：{plan.get('target')}")
    ok(f"计划写入 {len(plan.get('files', []))} 个文件，项目状态 {plan.get('project_status')}")


PROJECT_VALIDATOR = Path("05_harness/validate_project.py")


def verify(target: Path) -> bool:
    """委托给项目随附的校验器，避免向导维护第二份会漂移的验收清单。"""
    everything_ok = True
    validator = target / PROJECT_VALIDATOR
    if not validator.is_file():
        fail(f"{PROJECT_VALIDATOR}（缺失）：模板包未提供项目校验器")
        return False

    code, stdout, stderr = run([sys.executable, str(PROJECT_VALIDATOR)], target)
    output = (stdout + stderr).strip()
    for line in output.splitlines():
        if line.startswith("ERROR:"):
            fail(line[len("ERROR:") :].strip())
            everything_ok = False
        elif line.startswith("WARN:"):
            warn(line[len("WARN:") :].strip())
        elif line.startswith("ERRORS="):
            (ok if code == 0 else fail)(f"项目自校验 {line}")
    if code != 0 and everything_ok:
        fail("项目自校验未通过")
        everything_ok = False

    framework = target / "00_governance/PROJECT_TYPE_FRAMEWORK.md"
    if framework.is_file():
        header = framework.read_text(encoding="utf-8").splitlines()
        title_line = next((line for line in header if line.startswith("# ")), "")
        ok(f"类型框架：{title_line.lstrip('# ').strip() or framework.name}")
    return everything_ok


def main() -> int:
    print()
    print(paint("  Personal AI OS 项目创建向导", BOLD))
    info("按 Ctrl+C 可随时安全退出；在正式创建之前不会写入任何文件。")

    if not sys.stdin.isatty():
        fail("本向导需要交互式终端运行。")
        return 2

    answers = collect()
    summarize(answers)

    title("预演（Dry Run）")
    command = build_create_command(answers, apply=False)
    show_command(command)
    code, stdout, stderr = run(command, OS_ROOT)
    if code != 0:
        fail("预演失败，未做任何写入：")
        print((stderr or stdout).strip())
        return code
    report_plan(stdout)

    print()
    if not ask_yes_no("以上计划确认无误，开始正式创建？", default=False):
        info("已取消，未写入任何文件。")
        return 0

    title("正式创建")
    command = build_create_command(answers, apply=True)
    show_command(command)
    code, stdout, stderr = run(command, OS_ROOT)
    if code != 0:
        fail("创建失败：")
        print((stderr or stdout).strip())
        return code
    target = answers["target"].expanduser()
    ok(f"项目已创建：{target}")

    if answers["deploy"]:
        title("注入适配器")
        for label, manifest in ADAPTERS:
            command = [
                sys.executable,
                str(DEPLOY_SCRIPT),
                "--manifest",
                manifest,
                "--target",
                str(target),
                "--scope",
                "PROJECT",
                "--authorization-ref",
                answers["authorization_ref"],
                "--record-dir",
                str(RECORD_DIR),
                "--backup-dir",
                f"99_temp/deployment_backups/{answers['project_id']}",
                "--apply",
            ]
            show_command(command)
            code, stdout, stderr = run(command, OS_ROOT)
            if code != 0:
                fail(f"{label} 适配器部署失败：")
                print((stderr or stdout).strip())
                warn(f"项目本体已创建，可手动重试部署，或删除目标目录回滚：rm -rf {target}")
                return code
            ok(f"{label} 适配器已部署")

    title("验收")
    everything_ok = verify(target)
    if answers["deploy"]:
        for relative in (".codex/config.toml", ".gemini/settings.json"):
            if (target / relative).is_file():
                ok(relative)
            else:
                fail(f"{relative}（缺失）")
                everything_ok = False
    if answers["init_git"]:
        if (target / ".git").is_dir():
            ok(".git")
        else:
            fail(".git（缺失）")
            everything_ok = False

    if answers["first_commit"]:
        title("首次提交")
        message = f"chore: initialize project from {answers['pack_id']} {answers['pack_version']}"
        for command in (["git", "add", "-A"], ["git", "commit", "-m", message]):
            code, stdout, stderr = run(command, target)
            if code != 0:
                warn("首次提交失败（项目本体不受影响），可稍后手动提交：")
                print((stderr or stdout).strip())
                break
        else:
            ok(f"已提交：{message}")

    title("完成")
    if everything_ok:
        ok("全部验收项通过。")
    else:
        warn("存在未通过的验收项，请检查上面的 ✗ 条目。")
    print()
    info(f"项目状态为 PROVISIONAL，记录在 {target}/.paos-init.json。")
    info("向导不会写入 02_registry/projects.toml；是否登记进 OS Registry 由你单独决定。")
    info("按 INIT_WORKFLOW.md，先补全 PROJECT.md 的 Objective/Scope 并建立首张 Task Card，再考虑转 ACTIVE。")
    info(f"回滚：rm -rf {target}")
    print()
    return 0 if everything_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("  已中断。")
        sys.exit(130)
