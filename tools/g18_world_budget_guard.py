#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "g18_world_budget_guard"
REPORT_PATH = ARTIFACT_ROOT / "g18_world_budget_guard_report.json"
MARKER = "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS"

MAX_PRODUCTION_FILE_BYTES = 100 * 1024 * 1024
TARGET_PRODUCTION_FILE_BYTES = 50 * 1024 * 1024
MAX_PRODUCTION_BASE_WORLD_BYTES = 100 * 1024 * 1024
MAX_LOAD_TO_PLAY_SECONDS = 30

STRESS_ARTIFACT_PATHS = (
    "artifacts/g14_generated_64x64_playable_streaming/source",
    "artifacts/g14_generated_64x64_playable_streaming/worlds",
    "artifacts/g14_generated_64x64_playable_streaming/project/build/g14-generated-fixture",
    "artifacts/g16_generated_128x128_playable_streaming/source",
    "artifacts/g16_generated_128x128_playable_streaming/worlds",
    "artifacts/g16_generated_128x128_playable_streaming/project/build/g16-generated-fixture",
)

REQUIRED_DOC_PHRASES = {
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G18 is the production budget pivot",
        "no normal game path may require raw dense source files",
        "100 MiB hard per-file ceiling",
        "50 MiB target per-file ceiling",
        "30 seconds load-to-play ceiling",
        "G16 and G17 are stress-only evidence, not production terrain architecture",
    ),
    "docs/ROADMAP.md": (
        "## G18 - Production terrain budget pivot",
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
        "deterministic-on-demand generation",
        "compact seed/config plus edit journals",
        "raw dense source files are transient stress artifacts only",
    ),
    "README.md": (
        "python tools/g18_world_budget_guard.py",
        "WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS",
        "G18 production budget pivot",
    ),
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def largest_file(path: Path) -> tuple[str | None, int]:
    if not path.exists():
        return None, 0
    largest: tuple[str | None, int] = (None, 0)
    for file in path.rglob("*"):
        if not file.is_file():
            continue
        size = file.stat().st_size
        if size > largest[1]:
            largest = (relative(file), size)
    return largest


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def check_doc_phrases(errors: list[str]) -> None:
    for doc, phrases in REQUIRED_DOC_PHRASES.items():
        path = ROOT / doc
        if not path.is_file():
            errors.append(f"missing budget document: {doc}")
            continue
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            if phrase not in text and phrase not in normalized:
                errors.append(f"{doc} missing budget phrase: {phrase}")


def tracked_size_summary(errors: list[str]) -> dict[str, object]:
    oversized: list[dict[str, object]] = []
    largest: tuple[str | None, int] = (None, 0)
    for path in tracked_files():
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > largest[1]:
            largest = (relative(path), size)
        if size > MAX_PRODUCTION_FILE_BYTES:
            oversized.append({"path": relative(path), "bytes": size})
    if oversized:
        errors.append(f"tracked repository files exceed the production per-file ceiling: {oversized}")
    return {
        "largest_tracked_file": largest[0],
        "largest_tracked_file_bytes": largest[1],
        "oversized_tracked_files": oversized,
    }


def stress_artifact_summary() -> dict[str, object]:
    summaries: list[dict[str, object]] = []
    largest: tuple[str | None, int] = (None, 0)
    oversized_count = 0
    total = 0
    for rel in STRESS_ARTIFACT_PATHS:
        path = ROOT / rel
        size = directory_size(path)
        total += size
        file_path, file_size = largest_file(path)
        if file_size > largest[1]:
            largest = (file_path, file_size)
        if size > MAX_PRODUCTION_BASE_WORLD_BYTES or file_size > MAX_PRODUCTION_FILE_BYTES:
            oversized_count += 1
        summaries.append(
            {
                "path": rel,
                "present": path.exists(),
                "bytes": size,
                "largest_file": file_path,
                "largest_file_bytes": file_size,
                "stress_only": True,
            }
        )
    return {
        "paths": summaries,
        "total_bytes": total,
        "oversized_stress_artifacts": oversized_count,
        "largest_stress_file": largest[0],
        "largest_stress_file_bytes": largest[1],
    }


def main() -> None:
    errors: list[str] = []
    check_doc_phrases(errors)
    tracked = tracked_size_summary(errors)
    stress = stress_artifact_summary()

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)

    report = {
        "implementation": "production_terrain_budget_pivot",
        "production_ready": False,
        "budgets": {
            "max_production_file_bytes": MAX_PRODUCTION_FILE_BYTES,
            "target_production_file_bytes": TARGET_PRODUCTION_FILE_BYTES,
            "max_production_base_world_bytes": MAX_PRODUCTION_BASE_WORLD_BYTES,
            "max_load_to_play_seconds": MAX_LOAD_TO_PLAY_SECONDS,
        },
        "tracked": tracked,
        "stress_artifacts": stress,
        "required_architecture": (
            "deterministic-on-demand generation or compact seed/config plus edit journals"
        ),
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} production_ready=false "
        f"max_file_mb={MAX_PRODUCTION_FILE_BYTES // (1024 * 1024)} "
        f"target_file_mb={TARGET_PRODUCTION_FILE_BYTES // (1024 * 1024)} "
        f"load_to_play_seconds={MAX_LOAD_TO_PLAY_SECONDS} "
        f"oversized_stress_artifacts={stress['oversized_stress_artifacts']} "
        f"report={REPORT_PATH.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
