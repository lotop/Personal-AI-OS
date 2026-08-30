#!/usr/bin/env python3
"""计算 Git tracked working tree 的确定性 SHA-256。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise ValueError("无法读取 Git tracked files")
    return sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)


def calculate(root: Path) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    digest = hashlib.sha256()
    for relative in tracked_paths(root):
        path = root / relative
        if not path.is_file():
            raise ValueError(f"tracked path 缺失或不是普通文件: {relative}")
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        record = {"path": relative, "sha256": file_hash}
        records.append(record)
        digest.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
    return digest.hexdigest(), records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--include-files", action="store_true")
    args = parser.parse_args()
    try:
        tree_sha256, records = calculate(args.root.resolve())
        output = {"tree_sha256": tree_sha256, "tracked_files": len(records)}
        if args.include_files:
            output["files"] = records
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 10


if __name__ == "__main__":
    sys.exit(main())
