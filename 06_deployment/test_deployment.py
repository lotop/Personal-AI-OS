#!/usr/bin/env python3
"""Adapter 部署器测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deploy_adapter import apply_plan, build_plan


class DeploymentTest(unittest.TestCase):
    def make_adapter(self, root: Path) -> Path:
        adapter = root / "adapter"
        adapter.mkdir()
        (adapter / "settings.json").write_text('{"enabled": false}\n', encoding="utf-8")
        (adapter / "manifest.toml").write_text(
            'schema_version = "0.1"\nartifact_class = "GENERATED"\n'
            'maturity_state = "WORKING"\nplatform = "test"\n'
            'generator = "test"\nsource_files = ["source"]\n'
            '[[files]]\nsource = "settings.json"\ntarget = ".agent/settings.json"\nformat = "json"\n',
            encoding="utf-8",
        )
        return adapter / "manifest.toml"

    def test_create_and_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            _, plan = build_plan(manifest, target)
            self.assertEqual(plan[0].action, "CREATE")
            apply_plan(plan, None)
            _, second = build_plan(manifest, target)
            self.assertEqual(second[0].action, "UNCHANGED")

    def test_replace_requires_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            existing = target / ".agent/settings.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"old": true}\n', encoding="utf-8")
            _, plan = build_plan(manifest, target)
            self.assertEqual(plan[0].action, "REPLACE")
            with self.assertRaises(ValueError):
                apply_plan(plan, None)
            backup = root / "backup"
            apply_plan(plan, backup)
            self.assertTrue((backup / ".agent/settings.json").is_file())

    def test_partial_failure_rolls_back_created_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "one.json").write_text('{}\n', encoding="utf-8")
            (adapter / "two.json").write_text('{}\n', encoding="utf-8")
            (adapter / "manifest.toml").write_text(
                'schema_version = "0.1"\nartifact_class = "GENERATED"\n'
                'maturity_state = "WORKING"\nplatform = "test"\n'
                'generator = "test"\nsource_files = ["source"]\n'
                '[[files]]\nsource = "one.json"\ntarget = ".agent/one.json"\nformat = "json"\n'
                '[[files]]\nsource = "two.json"\ntarget = ".agent/two.json"\nformat = "json"\n',
                encoding="utf-8",
            )
            target = root / "target"
            _, plan = build_plan(adapter / "manifest.toml", target)
            calls = 0

            def fail_second(staged: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected failure")
                staged.replace(destination)

            with patch("deploy_adapter.atomic_replace", side_effect=fail_second):
                with self.assertRaises(OSError):
                    apply_plan(plan, None)
            self.assertFalse((target / ".agent/one.json").exists())
            self.assertFalse((target / ".agent/two.json").exists())
            self.assertEqual(list(target.rglob("*.paos-stage-*")), [])

    def test_reject_target_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            outside = root / "outside"
            outside.mkdir()
            target.mkdir()
            (target / ".agent").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                build_plan(manifest, target)

    def test_reject_duplicate_manifest_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            with manifest.open("a", encoding="utf-8") as stream:
                stream.write(
                    '[[files]]\nsource = "settings.json"\n'
                    'target = ".agent/settings.json"\nformat = "json"\n'
                )
            with self.assertRaisesRegex(ValueError, "重复目标"):
                build_plan(manifest, root / "target")

    def test_stale_create_plan_does_not_overwrite_new_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            _, plan = build_plan(manifest, target)
            appeared = target / ".agent/settings.json"
            appeared.parent.mkdir(parents=True)
            appeared.write_text('{"user": true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "计划已过期"):
                apply_plan(plan, None)
            self.assertEqual(appeared.read_text(encoding="utf-8"), '{"user": true}\n')

    def test_stale_replace_plan_does_not_backup_or_overwrite_changed_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            existing = target / ".agent/settings.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"old": true}\n', encoding="utf-8")
            _, plan = build_plan(manifest, target)
            existing.write_text('{"changed": true}\n', encoding="utf-8")
            backup = root / "backup"
            with self.assertRaisesRegex(ValueError, "计划已过期"):
                apply_plan(plan, backup)
            self.assertEqual(existing.read_text(encoding="utf-8"), '{"changed": true}\n')
            self.assertFalse(backup.exists())


if __name__ == "__main__":
    unittest.main()
