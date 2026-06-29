#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from compose_validation_project import ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "stress_artifact_cleanup"
REPORT_PATH = ARTIFACT_ROOT / "stress_artifact_cleanup_report.json"
MARKER = "WT_VALIDATION_STRESS_ARTIFACT_CLEANUP_PASS"

CLEANUP_PATHS = (
    "artifacts/g16_generated_128x128_playable_streaming/source",
    "artifacts/g16_generated_128x128_playable_streaming/worlds",
    "artifacts/g16_generated_128x128_playable_streaming/project",
    "artifacts/g14_generated_64x64_playable_streaming/source",
    "artifacts/g14_generated_64x64_playable_streaming/worlds",
    "artifacts/g14_generated_64x64_playable_streaming/project/build/g14-generated-fixture",
)


def safe_resolve(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    root = ROOT.resolve()
    if path == root or root not in path.parents:
        raise RuntimeError(f"refusing cleanup outside repository root: {path}")
    return path


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove ignored large stress artifacts while keeping committed reports and tools."
    )
    parser.add_argument("--execute", action="store_true", help="Actually remove the predefined stress artifact paths.")
    arguments = parser.parse_args()

    entries: list[dict[str, object]] = []
    reclaimable = 0
    removed = 0
    for relative in CLEANUP_PATHS:
        path = safe_resolve(relative)
        size = directory_size(path)
        existed = path.exists()
        reclaimable += size
        if arguments.execute and existed:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += size
        entries.append(
            {
                "path": relative,
                "existed": existed,
                "bytes": size,
                "removed": bool(arguments.execute and existed),
            }
        )

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "executed": bool(arguments.execute),
                "reclaimable_bytes": reclaimable,
                "removed_bytes": removed,
                "paths": entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} executed={str(arguments.execute).lower()} "
        f"reclaimable_mb={reclaimable / 1024 / 1024:.2f} "
        f"removed_mb={removed / 1024 / 1024:.2f} "
        f"report={REPORT_PATH.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
