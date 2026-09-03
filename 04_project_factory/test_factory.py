#!/usr/bin/env python3
"""Project Factory 安全边界测试。"""

from __future__ import annotations

import tempfile
import unittest
import sys
import subprocess
import json
from pathlib import Path
from unittest.mock import patch

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

sys.path.insert(0, str(Path(__file__).resolve().parent))

from create_project import (
    PlannedFile,
    build_manifest,
    calculate_pack_digest,
    finalize_staging,
    load_plan,
    render,
    validate_rendered_content,
    validate_target,
    write_project,
)


class ProjectFactoryTest(unittest.TestCase):
    PROJECT_PACK_KINDS = {"test": "PROJECT_SCAFFOLD"}

    def test_render(self) -> None:
        self.assertEqual(render("# {{PROJECT_NAME}}", {"PROJECT_NAME": "Demo"}), "# Demo")

    def test_missing_variable(self) -> None:
        with self.assertRaises(ValueError):
            render("{{MISSING}}", {})

    def test_reject_os_internal_target(self) -> None:
        with self.assertRaises(ValueError):
            validate_target(Path(__file__).resolve().parent / "unsafe")

    def test_manifest_and_path_confinement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# {{PROJECT_NAME}}\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\nrender = true\n',
                encoding="utf-8",
            )
            manifest, files = load_plan(
                pack, root / "output", {"PROJECT_NAME": "Demo"}, self.PROJECT_PACK_KINDS
            )
            self.assertEqual(manifest["pack_id"], "test")
            self.assertEqual(files[0].content, "# Demo\n")

    def test_reject_undeclared_pack_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# Demo\n", encoding="utf-8")
            (pack / "UNDECLARED.md").write_text("unexpected\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "未登记文件"):
                load_plan(pack, root / "output", {}, self.PROJECT_PACK_KINDS)

    def test_reject_approved_pack_without_approval_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# Demo\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "APPROVED"\n'
                'owner = "test"\ncanonical_authority = "FOUNDER_APPROVAL"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "approval_reference"):
                load_plan(pack, root / "output", {}, self.PROJECT_PACK_KINDS)

    def test_end_to_end_provisional_creation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            target = root / "new-project"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# {{PROJECT_NAME}}\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\nrender = true\n',
                encoding="utf-8",
            )
            variables = {
                "PROJECT_ID": "demo-project",
                "PROJECT_NAME": "Demo",
                "OWNER": "Founder",
                "PRIMARY_TYPE": "SOFTWARE_DEVELOPMENT",
            }
            pack_manifest, files = load_plan(pack, target, variables, self.PROJECT_PACK_KINDS)
            init_manifest = build_manifest(
                pack_manifest, target, variables, files, True, "1.2.0", "1.1.4"
            )
            write_project(target, files, init_manifest, init_git=True)
            self.assertTrue((target / "PROJECT.md").is_file())
            self.assertTrue((target / ".paos-init.json").is_file())
            self.assertTrue((target / ".git").is_dir())

    def test_pack_digest_fixed_vector_and_mismatch_rejected(self) -> None:
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        # 固定向量：模板包任何改动都必须在此处显式更新，作为静默漂移的减速带。
        expected = "7937dea28f1f2c7b0504d18617ca0f770a070eed89d94695842cf0bf8fd5179f"
        self.assertEqual(calculate_pack_digest(pack), expected)
        # factory.toml 的登记值必须与实际内容一致，防止改了模板却忘记更新登记。
        factory = tomllib.loads(
            (Path(__file__).resolve().parent / "factory.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            factory["approved_template_pack_digests"]["paos-project-base"], expected
        )
        with tempfile.TemporaryDirectory() as raw:
            variables = {
                "PROJECT_ID": "digest-test",
                "PROJECT_NAME": "Digest Test",
                "OWNER": "Founder",
                "PRIMARY_TYPE": "SOFTWARE_DEVELOPMENT",
            }
            with self.assertRaisesRegex(ValueError, "Digest 不匹配"):
                load_plan(
                    pack,
                    Path(raw) / "output",
                    variables,
                    {"paos-project-base": "PROJECT_SCAFFOLD"},
                    {"paos-project-base": "0" * 64},
                )

    def test_manifest_v02_records_install_baseline_and_candidate(self) -> None:
        target = Path("/tmp/project-candidate")
        source = Path("/tmp/source.md")
        files = [PlannedFile(source, target / "PROJECT.md", "# Demo\n")]
        variables = {
            "PROJECT_ID": "demo-project",
            "PROJECT_NAME": "Demo",
            "OWNER": "Founder",
            "PRIMARY_TYPE": "SOFTWARE_DEVELOPMENT",
        }
        pack_manifest = {
            "pack_id": "test",
            "version": "1.0.0",
            "artifact_state": "APPROVED",
            "approval_reference": "PAOS-TEST",
            "_pack_digest": "abc123",
        }
        manifest = build_manifest(
            pack_manifest, target, variables, files, False, "1.2.0", "1.1.4"
        )
        self.assertEqual(manifest["schema_version"], "0.3.0")
        self.assertEqual(manifest["generator"], "paos-project-factory")
        self.assertEqual(manifest["project_status"], "PROVISIONAL")
        self.assertEqual(manifest["template_state"], "APPROVED")
        self.assertEqual(manifest["template_approval_reference"], "PAOS-TEST")
        self.assertEqual(manifest["template_pack_digest"], "abc123")
        self.assertEqual(manifest["registry_candidate"]["status"], "PROVISIONAL")

    def test_reject_provisional_apply(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            command = [
                sys.executable,
                str(Path(__file__).resolve().parent / "create_project.py"),
                "--template-pack", str(root / "working-pack"),
                "--target", str(root / "candidate"),
                "--project-id", "candidate",
                "--name", "Candidate",
                "--owner", "Founder",
                "--primary-type", "SOFTWARE_DEVELOPMENT",
                "--provisional",
                "--apply",
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertIn("只允许 Dry Run", result.stderr)
            self.assertFalse((root / "candidate").exists())

    def test_reject_missing_target_parent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "missing-parent" / "candidate"
            with self.assertRaisesRegex(ValueError, "父目录必须预先存在"):
                validate_target(target)

    def test_finalize_rejects_target_created_during_generation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            staging = root / ".staging"
            target = root / "candidate"
            staging.mkdir()
            target.mkdir()
            with self.assertRaisesRegex(ValueError, "生成期间出现"):
                finalize_staging(staging, target)
            self.assertTrue(staging.is_dir())
            self.assertTrue(target.is_dir())

    def test_reject_nonempty_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            (target / "existing.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_target(target)

    def test_reject_existing_empty_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(ValueError):
                validate_target(Path(raw))

    def test_git_failure_rolls_back_staging(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "failed-project"
            source = root / "source.md"
            source.write_text("# Demo\n", encoding="utf-8")
            files = [PlannedFile(source, target / "PROJECT.md", "# Demo\n")]
            manifest = {"project_status": "PROVISIONAL"}
            failed = subprocess.CompletedProcess(["git"], 1, "", "injected failure")
            with patch("create_project.subprocess.run", return_value=failed):
                with self.assertRaises(ValueError):
                    write_project(target, files, manifest, init_git=True)
            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".failed-project.paos-staging-*")), [])

    def test_reject_artifact_library_pack(self) -> None:
        pack = Path(__file__).resolve().parents[1] / "01_templates/core-template-pack"
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaisesRegex(ValueError, "不能由 Project Factory 实例化"):
                load_plan(
                    pack,
                    Path(raw) / "output",
                    {},
                    {"paos-core-templates": "ARTIFACT_LIBRARY"},
                )

    def test_reject_unregistered_pack_kind(self) -> None:
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaisesRegex(ValueError, "未在 Factory 配置中登记用途"):
                load_plan(pack, Path(raw) / "output", {}, {})

    def test_reject_invalid_rendered_toml(self) -> None:
        with self.assertRaisesRegex(ValueError, "结构化文件无效"):
            validate_rendered_content(Path("project.toml"), 'name = "Bad " Name"\n')

    def test_factory_rejects_toml_breaking_project_name(self) -> None:
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "invalid-project"
            command = [
                sys.executable,
                str(Path(__file__).resolve().parent / "create_project.py"),
                "--template-pack", str(pack),
                "--target", str(target),
                "--project-id", "invalid-project",
                "--name", 'Bad " Name',
                "--owner", "Founder",
                "--primary-type", "SOFTWARE_DEVELOPMENT",
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertIn("结构化文件无效", result.stderr)
            self.assertFalse(target.exists())

    def test_repository_approved_pack_dry_run_and_apply(self) -> None:
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "candidate-project"
            command = [
                sys.executable,
                str(Path(__file__).resolve().parent / "create_project.py"),
                "--template-pack", str(pack),
                "--target", str(target),
                "--project-id", "candidate-project",
                "--name", "候选项目",
                "--owner", "Founder",
                "--primary-type", "SOFTWARE_DEVELOPMENT",
            ]
            dry_run = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertFalse(target.exists())

            apply_run = subprocess.run(
                command + ["--apply", "--git"], text=True, capture_output=True, check=False
            )
            self.assertEqual(apply_run.returncode, 0, apply_run.stderr)
            for relative in (
                "AGENTS.md",
                "CLAUDE.md",
                ".claude/settings.json",
                "PROJECT.md",
                "project.toml",
                "TASKS.md",
                "SESSION_CLOSE.md",
            ):
                self.assertTrue((target / relative).is_file(), relative)
            self.assertTrue((target / ".git").is_dir())
            self.assertNotIn("{{", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue(
                (target / "CLAUDE.md").read_text(encoding="utf-8").startswith("@AGENTS.md")
            )
            init_manifest = json.loads((target / ".paos-init.json").read_text(encoding="utf-8"))
            self.assertEqual(init_manifest["schema_version"], "0.3.0")
            self.assertEqual(init_manifest["project_status"], "PROVISIONAL")
            self.assertEqual(init_manifest["template_state"], "APPROVED")

    def test_primary_type_filter_emits_only_matching_framework(self) -> None:
        """每个项目只应拿到与自身类型匹配的那一份类型框架。"""
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        factory = tomllib.loads(
            (Path(__file__).resolve().parent / "factory.toml").read_text(encoding="utf-8")
        )
        expected_marker = {
            "SOFTWARE_DEVELOPMENT": "software-development-framework",
            "SOLUTION_RESEARCH": "solution-research-framework",
            "CONTENT_MARKETING": "content-marketing-framework",
            "BRAND_MANAGEMENT": "brand-management-framework",
        }
        self.assertEqual(sorted(factory["primary_types"]), sorted(expected_marker))
        for primary_type, marker in expected_marker.items():
            with tempfile.TemporaryDirectory() as raw:
                target = Path(raw) / "project"
                variables = {
                    "PROJECT_ID": "filter-test",
                    "PROJECT_NAME": "Filter Test",
                    "OWNER": "Founder",
                    "PRIMARY_TYPE": primary_type,
                }
                _, files = load_plan(
                    pack,
                    target,
                    variables,
                    factory["template_pack_kinds"],
                    factory["approved_template_pack_digests"],
                )
                frameworks = [
                    item
                    for item in files
                    if item.destination.name == "PROJECT_TYPE_FRAMEWORK.md"
                ]
                self.assertEqual(len(frameworks), 1, f"{primary_type} 应恰好产出一份类型框架")
                self.assertIn(marker, frameworks[0].content)
                self.assertIn(primary_type, frameworks[0].content)

    def test_unknown_primary_type_gets_no_framework(self) -> None:
        """未登记类型不产出框架；由 CLI 的 primary_types 校验先行拦截。"""
        pack = Path(__file__).resolve().parents[1] / "01_templates/project-base-pack"
        factory = tomllib.loads(
            (Path(__file__).resolve().parent / "factory.toml").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as raw:
            variables = {
                "PROJECT_ID": "filter-test",
                "PROJECT_NAME": "Filter Test",
                "OWNER": "Founder",
                "PRIMARY_TYPE": "NOT_A_REAL_TYPE",
            }
            _, files = load_plan(
                pack,
                Path(raw) / "project",
                variables,
                factory["template_pack_kinds"],
                factory["approved_template_pack_digests"],
            )
            self.assertEqual(
                [item for item in files if item.destination.name == "PROJECT_TYPE_FRAMEWORK.md"],
                [],
            )


if __name__ == "__main__":
    unittest.main()
