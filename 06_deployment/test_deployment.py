#!/usr/bin/env python3
"""Adapter 部署器测试。"""

from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "05_harness"))

from deploy_adapter import apply_plan, build_plan
from generate_adapters import PROFILE_PATH, build_plan as build_generation_plan, load_profiles, write_outputs


class DeploymentTest(unittest.TestCase):
    def plan(self, manifest: Path, target: Path):
        return build_plan(manifest, target, managed_adapter_root=manifest.parent.parent)

    def apply(self, manifest: dict, plan, backup: Path | None = None, record_root: Path | None = None):
        return apply_plan(
            manifest,
            plan,
            backup,
            authorization_ref="PAOS-020-TEST",
            target_scope="PROJECT",
            record_root=record_root or (plan[0].target_root / ".deployment-records"),
        )

    def make_adapter(self, root: Path) -> Path:
        adapter = root / "adapter"
        adapter.mkdir()
        (adapter / "settings.json").write_text('{"enabled": false}\n', encoding="utf-8")
        (adapter / "manifest.toml").write_text(
            'schema_version = "0.1"\nartifact_class = "GENERATED"\n'
            'maturity_state = "WORKING"\nplatform = "test"\n'
            'generator = "05_harness/generate_adapters.py@0.3"\nsource_files = ["source"]\n'
            '[[files]]\nsource = "settings.json"\ntarget = ".agent/settings.json"\nformat = "json"\n',
            encoding="utf-8",
        )
        return adapter / "manifest.toml"

    def test_create_and_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            data, plan = self.plan(manifest, target)
            self.assertEqual(plan[0].action, "CREATE")
            record = self.apply(data, plan)
            evidence = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual(evidence["files"][0]["source_sha256"], evidence["files"][0]["deployed_sha256"])
            self.assertEqual(evidence["files"][0]["source_mode"], evidence["files"][0]["deployed_mode"])
            _, second = self.plan(manifest, target)
            self.assertEqual(second[0].action, "UNCHANGED")

    def test_replace_requires_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            existing = target / ".agent/settings.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"old": true}\n', encoding="utf-8")
            data, plan = self.plan(manifest, target)
            self.assertEqual(plan[0].action, "REPLACE")
            with self.assertRaises(ValueError):
                self.apply(data, plan)
            backup = root / "backup"
            self.apply(data, plan, backup)
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
                'generator = "05_harness/generate_adapters.py@0.3"\nsource_files = ["source"]\n'
                '[[files]]\nsource = "one.json"\ntarget = ".agent/one.json"\nformat = "json"\n'
                '[[files]]\nsource = "two.json"\ntarget = ".agent/two.json"\nformat = "json"\n',
                encoding="utf-8",
            )
            target = root / "target"
            data, plan = self.plan(adapter / "manifest.toml", target)
            calls = 0

            def fail_second(staged: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected failure")
                staged.replace(destination)

            with patch("deploy_adapter.atomic_replace", side_effect=fail_second):
                with self.assertRaises(OSError):
                    self.apply(data, plan)
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
                self.plan(manifest, target)

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
                self.plan(manifest, root / "target")

    def test_stale_create_plan_does_not_overwrite_new_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            data, plan = self.plan(manifest, target)
            appeared = target / ".agent/settings.json"
            appeared.parent.mkdir(parents=True)
            appeared.write_text('{"user": true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "计划已过期"):
                self.apply(data, plan)
            self.assertEqual(appeared.read_text(encoding="utf-8"), '{"user": true}\n')

    def test_stale_replace_plan_does_not_backup_or_overwrite_changed_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            target = root / "target"
            existing = target / ".agent/settings.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"old": true}\n', encoding="utf-8")
            data, plan = self.plan(manifest, target)
            existing.write_text('{"changed": true}\n', encoding="utf-8")
            backup = root / "backup"
            with self.assertRaisesRegex(ValueError, "计划已过期"):
                self.apply(data, plan, backup)
            self.assertEqual(existing.read_text(encoding="utf-8"), '{"changed": true}\n')
            self.assertFalse(backup.exists())

    def test_apply_requires_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest_path = self.make_adapter(root)
            manifest, plan = self.plan(manifest_path, root / "target")
            with self.assertRaisesRegex(ValueError, "授权"):
                apply_plan(
                    manifest,
                    plan,
                    None,
                    authorization_ref="",
                    target_scope="PROJECT",
                    record_root=root / "records",
                )

    def test_unmanaged_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            other = root / "managed"
            other.mkdir()
            with self.assertRaisesRegex(ValueError, "受管"):
                build_plan(manifest, root / "target", managed_adapter_root=other)

    def test_nested_manifest_below_managed_platform_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = self.make_adapter(root)
            nested = manifest.parent / "nested"
            nested.mkdir()
            moved = nested / "manifest.toml"
            manifest.replace(moved)
            (manifest.parent / "settings.json").replace(nested / "settings.json")
            with self.assertRaisesRegex(ValueError, "受管"):
                build_plan(moved, root / "target", managed_adapter_root=root)

    def test_record_failure_rolls_back_replacement_and_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest_path = self.make_adapter(root)
            target = root / "target"
            existing = target / ".agent/settings.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"old": true}\n', encoding="utf-8")
            manifest, plan = self.plan(manifest_path, target)
            backup = root / "backup"
            with patch("deploy_adapter.Path.write_text", side_effect=OSError("record failed")):
                with self.assertRaisesRegex(OSError, "record failed"):
                    self.apply(manifest, plan, backup, root / "records")
            self.assertEqual(existing.read_text(encoding="utf-8"), '{"old": true}\n')
            self.assertEqual(list(backup.rglob("*")), [])

    def test_generator_rejects_symlink_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            output = root / "outputs"
            target = output / "codex/config.toml"
            target.parent.mkdir(parents=True)
            outside = root / "outside.toml"
            outside.write_text("safe = true\n", encoding="utf-8")
            target.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                write_outputs({target: "safe = false\n"}, output)

    def test_generator_profile_unknown_field_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            profile = Path(raw) / "profile.toml"
            profile.write_text(PROFILE_PATH.read_text(encoding="utf-8") + '\nunknown = "no"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "字段漂移"):
                load_profiles(profile)

    def test_generator_partial_failure_restores_content_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "outputs"
            first = output / "one/config.toml"
            second = output / "two/settings.json"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("old = true\n", encoding="utf-8")
            second.write_text("{}\n", encoding="utf-8")
            first.chmod(0o640)
            calls = 0

            def fail_second(staged: Path, target: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected generator failure")
                staged.replace(target)

            outputs = {first: "new = true\n", second: '{"changed": true}\n'}
            with patch("generate_adapters.replace_generated", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "generator failure"):
                    write_outputs(outputs, output)
            self.assertEqual(first.read_text(encoding="utf-8"), "old = true\n")
            self.assertEqual(first.stat().st_mode & 0o7777, 0o640)
            self.assertEqual(second.read_text(encoding="utf-8"), "{}\n")

    def test_generator_rejects_undeclared_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "outputs"
            target = output / "one/config.toml"
            target.parent.mkdir(parents=True)
            target.write_text("old = true\n", encoding="utf-8")
            extra = output / "one/extra.toml"
            extra.write_text("extra = true\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "未声明"):
                build_generation_plan({target: "old = true\n"})


if __name__ == "__main__":
    unittest.main()
