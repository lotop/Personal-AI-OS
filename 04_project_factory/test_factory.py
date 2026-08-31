#!/usr/bin/env python3
"""Project Factory 安全边界测试。"""

from __future__ import annotations

import tempfile
import unittest
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from create_project import (
    PlannedFile,
    build_manifest,
    load_plan,
    render,
    validate_rendered_content,
    validate_target,
    write_project,
)


class ProjectFactoryTest(unittest.TestCase):
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
                'pack_id = "test"\npack_kind = "PROJECT_SCAFFOLD"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\nrender = true\n',
                encoding="utf-8",
            )
            manifest, files = load_plan(pack, root / "output", {"PROJECT_NAME": "Demo"})
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
                'pack_id = "test"\npack_kind = "PROJECT_SCAFFOLD"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "未登记文件"):
                load_plan(pack, root / "output", {})

    def test_reject_approved_pack_without_approval_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# Demo\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\npack_kind = "PROJECT_SCAFFOLD"\nversion = "0.1"\nartifact_state = "APPROVED"\n'
                'owner = "test"\ncanonical_authority = "FOUNDER_APPROVAL"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "approval_reference"):
                load_plan(pack, root / "output", {})

    def test_end_to_end_provisional_creation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            target = root / "new-project"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# {{PROJECT_NAME}}\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\npack_kind = "PROJECT_SCAFFOLD"\nversion = "0.1"\nartifact_state = "WORKING"\n'
                'owner = "test"\ncanonical_authority = "NONE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\nrender = true\n',
                encoding="utf-8",
            )
            variables = {
                "PROJECT_ID": "demo-project",
                "PROJECT_NAME": "Demo",
                "OWNER": "Founder",
                "PRIMARY_TYPE": "SOFTWARE_PRODUCT",
                "OVERLAYS": "ai,software",
            }
            pack_manifest, files = load_plan(pack, target, variables)
            init_manifest = build_manifest(pack_manifest, target, variables, files, True)
            write_project(target, files, init_manifest, init_git=True)
            self.assertTrue((target / "PROJECT.md").is_file())
            self.assertTrue((target / ".paos-init.json").is_file())
            self.assertTrue((target / ".git").is_dir())

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
                load_plan(pack, Path(raw) / "output", {})

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
                "--primary-type", "SOFTWARE_PRODUCT",
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
                "--primary-type", "SOFTWARE_PRODUCT",
                "--overlay", "ai",
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


if __name__ == "__main__":
    unittest.main()
