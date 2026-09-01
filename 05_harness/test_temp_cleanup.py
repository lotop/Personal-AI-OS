#!/usr/bin/env python3
"""Temp Cleanup 计划、重验与 Quarantine 测试。"""

from __future__ import annotations

import tempfile
import unittest
import shutil
import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from temp_cleanup import apply_plan, build_plan, discover_candidates


POLICY = {
    "schema_version": "0.1.0-working",
    "enabled": True,
    "dry_run_only": False,
    "destructive_delete": False,
    "plan_ttl_hours": 24,
    "quarantine_root": "99_temp/quarantine",
    "plan_root": "99_temp/plans",
    "retention": {"temp_days": 0, "cache_days": 0, "logs_days": 30},
    "protection": {"require_founder_approval": True},
}
AUTH = "PAOS-GC-AUTH-TEST"


class TempCleanupTest(unittest.TestCase):
    def apply(self, root: Path, plan: dict, policy: dict = POLICY) -> Path:
        plan_path = root / policy["plan_root"] / f"{plan['plan_id']}.json"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return apply_plan(
            root,
            policy,
            plan,
            plan_path=plan_path,
            authorization_ref=AUTH,
        )

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
            record = self.apply(root, plan)
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
                self.apply(root, plan)

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
                self.apply(root, plan)
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
                self.apply(root, plan)
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
                    self.apply(root, plan)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())

    def test_record_write_failure_rolls_back_moved_items(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / ".DS_Store"
            target.write_bytes(b"temp")
            plan = build_plan(root, POLICY)
            plan_path = root / "99_temp/plans" / f"{plan['plan_id']}.json"
            plan_path.parent.mkdir(parents=True)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with patch("temp_cleanup.Path.write_text", side_effect=OSError("record failed")):
                with self.assertRaisesRegex(OSError, "record failed"):
                    apply_plan(root, POLICY, plan, plan_path=plan_path, authorization_ref=AUTH)
            self.assertTrue(target.is_file())

    def test_plan_id_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".DS_Store").write_bytes(b"temp")
            plan = build_plan(root, POLICY)
            plan["plan_id"] = "../escape"
            plan_path = root / "99_temp/plans/escape.json"
            plan_path.parent.mkdir(parents=True)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "plan_id"):
                apply_plan(root, POLICY, plan, plan_path=plan_path, authorization_ref=AUTH)

    def test_plan_filename_must_match_plan_id(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".DS_Store").write_bytes(b"temp")
            plan = build_plan(root, POLICY)
            plan_path = root / "99_temp/plans/wrong.json"
            plan_path.parent.mkdir(parents=True)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "文件名"):
                apply_plan(root, POLICY, plan, plan_path=plan_path, authorization_ref=AUTH)

    def test_founder_authorization_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".DS_Store").write_bytes(b"temp")
            plan = build_plan(root, POLICY)
            plan_path = root / "99_temp/plans" / f"{plan['plan_id']}.json"
            plan_path.parent.mkdir(parents=True)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Founder"):
                apply_plan(root, POLICY, plan, plan_path=plan_path, authorization_ref="")

    def test_retention_excludes_fresh_temp(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".DS_Store").write_bytes(b"fresh")
            policy = {**POLICY, "retention": {"temp_days": 7, "cache_days": 30, "logs_days": 30}}
            self.assertEqual(build_plan(root, policy)["items"], [])

    def test_referenced_99_temp_item_is_held(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            item = root / "99_temp/needed.tmp"
            item.parent.mkdir(parents=True)
            item.write_text("payload", encoding="utf-8")
            (root / "PROJECT.md").write_text("依赖 99_temp/needed.tmp\n", encoding="utf-8")
            plan = build_plan(root, POLICY)
            self.assertTrue(plan["items"][0]["hold"])
            with self.assertRaisesRegex(ValueError, "授权证据"):
                self.apply(root, plan)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unsupported")
    def test_nested_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            item = root / "99_temp/folder"
            item.mkdir(parents=True)
            (root / "outside.txt").write_text("outside", encoding="utf-8")
            os.symlink(root / "outside.txt", item / "link")
            with self.assertRaisesRegex(ValueError, "嵌套 symlink"):
                build_plan(root, POLICY)


if __name__ == "__main__":
    unittest.main()
