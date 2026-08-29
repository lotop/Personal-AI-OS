#!/usr/bin/env python3
"""Adapter 部署器测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deploy_adapter import apply_plan, build_plan


class DeploymentTest(unittest.TestCase):
    def make_adapter(self, root: Path) -> Path:
        adapter = root / "adapter"
        adapter.mkdir()
        (adapter / "settings.json").write_text('{"enabled": false}\n', encoding="utf-8")
        (adapter / "manifest.toml").write_text(
            'schema_version = "0.1"\nartifact_class = "GENERATED"\n'
            'maturity_state = "CANDIDATE"\nplatform = "test"\n'
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


if __name__ == "__main__":
    unittest.main()
