#!/usr/bin/env python3
"""Temp Cleanup 计划、重验与 Quarantine 测试。"""

from __future__ import annotations

import tempfile
import unittest
import shutil
import hashlib
from pathlib import Path
from unittest.mock import patch

from temp_cleanup import apply_plan, build_plan, discover_candidates


POLICY = {
    "schema_version": "0.1.0-working",
    "enabled": True,
    "dry_run_only": False,
    "destructive_delete": False,
    "plan_ttl_hours": 24,
    "quarantine_root": "99_temp/quarantine",
    "plan_root": "99_temp/plans",
}


class TempCleanupTest(unittest.TestCase):
    def test_scope_only_includes_known_ephemeral_items(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "rules.md").write_text("keep\n", encoding="utf-8")
            (root / ".DS_Store").write_bytes(b"temp")
            (root / ".git").mkdir()
            (root / ".git/.DS_Store").write_bytes(b"protected")
            cache = root / "module/__pycache__"
            cache.mkdir(parents=True)
            (cache / "x.pyc").write_bytes(b"cache")
            (root / "99_temp").mkdir()
            (root / "99_temp/.gitkeep").write_text("", encoding="utf-8")
            (root / "99_temp/scratch.tmp").write_text("temp", encoding="utf-8")
            relative = {path.relative_to(root).as_posix() for path, _kind, _reason in discover_candidates(root)}
            self.assertEqual(relative, {".DS_Store", "module/__pycache__", "99_temp/scratch.tmp"})

    def test_apply_moves_items_to_recoverable_quarantine(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".DS_Store").write_bytes(b"temp")
            (root / "99_temp/plans").mkdir(parents=True)
            plan = build_plan(root, POLICY)
            record = apply_plan(root, POLICY, plan)
            self.assertFalse((root / ".DS_Store").exists())
            self.assertTrue((root / "99_temp/quarantine" / plan["plan_id"] / ".DS_Store").is_file())
            self.assertTrue(record.is_file())

    def test_changed_item_makes_plan_stale(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / ".DS_Store"
            target.write_bytes(b"before")
            (root / "99_temp/plans").mkdir(parents=True)
            plan = build_plan(root, POLICY)
            target.write_bytes(b"after")
            with self.assertRaisesRegex(ValueError, "STALE"):
                apply_plan(root, POLICY, plan)

    def test_tampered_plan_cannot_quarantine_canonical_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            canonical = root / "SYSTEM.toml"
            canonical.write_text('system_name = "keep"\n', encoding="utf-8")
            (root / "99_temp/plans").mkdir(parents=True)
            plan = build_plan(root, POLICY)
            plan["items"].append(
                {
                    "path": "SYSTEM.toml",
                    "real_path": str(canonical.resolve()),
                    "artifact_class": "TEMP",
                    "sha256": hashlib.sha256(canonical.read_bytes()).hexdigest(),
                    "reference_scan": "CLEAR_KNOWN_EPHEMERAL_ONLY",
                    "hold": False,
                    "recovery_until": plan["expires_at"],
                    "reason_code": "TEMP_AREA_ITEM",
                }
            )
            with self.assertRaisesRegex(ValueError, "疑似被篡改"):
                apply_plan(root, POLICY, plan)
            self.assertTrue(canonical.is_file())

    def test_tampered_classification_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / ".DS_Store"
            target.write_bytes(b"temp")
            (root / "99_temp/plans").mkdir(parents=True)
            plan = build_plan(root, POLICY)
            plan["items"][0]["reason_code"] = "PYTHON_BYTECODE_CACHE"
            with self.assertRaisesRegex(ValueError, "疑似被篡改"):
                apply_plan(root, POLICY, plan)
            self.assertTrue(target.is_file())

    def test_move_failure_rolls_back_prior_items(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = root / ".DS_Store"
            second = root / "other.pyc"
            first.write_bytes(b"first")
            second.write_bytes(b"second")
            (root / "99_temp/plans").mkdir(parents=True)
            plan = build_plan(root, POLICY)
            real_move = shutil.move
            calls = 0

            def fail_second(source: str, target: str) -> str:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected move failure")
                return real_move(source, target)

            with patch("temp_cleanup.shutil.move", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "injected"):
                    apply_plan(root, POLICY, plan)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())


if __name__ == "__main__":
    unittest.main()
