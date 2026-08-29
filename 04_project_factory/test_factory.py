#!/usr/bin/env python3
"""Project Factory 安全边界测试。"""

from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from create_project import build_manifest, load_plan, render, validate_target, write_project


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
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "CANDIDATE"\n'
                '[[files]]\nsource = "PROJECT.md"\ndestination = "PROJECT.md"\nrender = true\n',
                encoding="utf-8",
            )
            manifest, files = load_plan(pack, root / "output", {"PROJECT_NAME": "Demo"})
            self.assertEqual(manifest["pack_id"], "test")
            self.assertEqual(files[0].content, "# Demo\n")

    def test_end_to_end_provisional_creation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            target = root / "new-project"
            pack.mkdir()
            (pack / "PROJECT.md").write_text("# {{PROJECT_NAME}}\n", encoding="utf-8")
            (pack / "template.toml").write_text(
                'pack_id = "test"\nversion = "0.1"\nartifact_state = "CANDIDATE"\n'
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


if __name__ == "__main__":
    unittest.main()
