#!/usr/bin/env python3
"""计算 Git tracked working tree 的确定性 SHA-256。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


ALGORITHM_VERSION = "0.2"


def tracked_entries(root: Path) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "ls-files", "-s", "-z"], cwd=root, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise ValueError("无法读取 Git tracked files")
    entries = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        metadata, path_raw = raw.split(b"\t", 1)
        mode, _object_id, stage = metadata.decode("ascii").split()
        if stage != "0":
            raise ValueError("存在未合并的 Git index entry")
        entries.append((path_raw.decode("utf-8"), mode))
    return sorted(entries)


def _digest_records(records: list[dict[str, str]], algorithm: str) -> str:
    digest = hashlib.sha256()
    if algorithm == "0.2":
        digest.update(b"paos-tree-digest-v0.2\n")
        for record in records:
            digest.update(record["path"].encode("utf-8") + b"\0")
            digest.update(record["mode"].encode("ascii") + b"\0")
            digest.update(record["object_kind"].encode("ascii") + b"\0")
            digest.update(record["sha256"].encode("ascii") + b"\n")
    elif algorithm == "0.1":
        for record in records:
            digest.update(record["path"].encode("utf-8") + b"\0")
            digest.update(record["sha256"].encode("ascii") + b"\n")
    else:
        raise ValueError(f"不支持的 Tree Digest Version: {algorithm}")
    return digest.hexdigest()


def calculate(root: Path, algorithm: str = ALGORITHM_VERSION) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    for relative, index_mode in tracked_entries(root):
        path = root / relative
        try:
            info = path.lstat()
        except OSError as exc:
            raise ValueError(f"tracked path 缺失: {relative}") from exc
        if stat.S_ISLNK(info.st_mode):
            actual_mode = "120000"
            object_kind = "symlink"
            content = os.readlink(path).encode("utf-8")
        elif stat.S_ISREG(info.st_mode):
            actual_mode = "100755" if info.st_mode & 0o111 else "100644"
            object_kind = "blob"
            content = path.read_bytes()
        else:
            raise ValueError(f"tracked path 类型不受支持: {relative}")
        if actual_mode != index_mode:
            raise ValueError(f"tracked path mode 与 Git index 不一致: {relative}: {actual_mode} != {index_mode}")
        record = {
            "path": relative,
            "mode": actual_mode,
            "object_kind": object_kind,
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        records.append(record)
    return _digest_records(records, algorithm), records


def calculate_commit(
    root: Path, commit: str, algorithm: str = ALGORITHM_VERSION
) -> tuple[str, list[dict[str, str]]]:
    listing = subprocess.run(
        ["git", "ls-tree", "-rz", "--full-tree", commit],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if listing.returncode != 0:
        raise ValueError("无法读取 evidence commit tree")
    records: list[dict[str, str]] = []
    for raw in listing.stdout.split(b"\0"):
        if not raw:
            continue
        metadata, path_raw = raw.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split()
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"不支持的 Git tree object: {mode} {kind}")
        blob = subprocess.run(
            ["git", "cat-file", "blob", object_id],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if blob.returncode != 0:
            raise ValueError("无法读取 evidence commit blob")
        records.append(
            {
                "path": path_raw.decode("utf-8"),
                "mode": mode,
                "object_kind": "symlink" if mode == "120000" else "blob",
                "sha256": hashlib.sha256(blob.stdout).hexdigest(),
            }
        )
    return _digest_records(sorted(records, key=lambda item: item["path"]), algorithm), records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--include-files", action="store_true")
    args = parser.parse_args()
    try:
        tree_sha256, records = calculate(args.root.resolve())
        output = {
            "algorithm_version": ALGORITHM_VERSION,
            "tree_sha256": tree_sha256,
            "tracked_files": len(records),
        }
        if args.include_files:
            output["files"] = records
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 10


if __name__ == "__main__":
    sys.exit(main())
