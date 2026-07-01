#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G57_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G57_SEPARATE_GAME_REPOSITORY_INTEGRATION_QUALITY.md",
    "tools/g57_separate_game_repository_integration_quality.py",
    "tools/validate_g57_contract.py",
]

REQUIRED_PHRASES = {
    "tools/g57_separate_game_repository_integration_quality.py": (
        "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
        "WT_INTEGRATION_GAME_G57_PASS",
        "world-transvoxel-integration-game",
        "assert_no_validation_internals",
        "world_transvoxel_game_world",
        "world_transvoxel_terrain",
        "world_transvoxel",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track:",
        "G57 - Separate game repository integration quality",
    ),
    "docs/G57_SEPARATE_GAME_REPOSITORY_INTEGRATION_QUALITY.md": (
        "WT_VALIDATION_G57_CONTRACT_PASS",
        "WT_INTEGRATION_GAME_G57_PASS",
        "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
    ),
    "README.md": (
        "G57 is a completed separate game repository integration quality gate",
        "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G57 - Separate game repository integration quality",
        "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G57 locked separate game repository integration",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G57 is a completed separate game repository integration quality gate",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G57 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G57 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".py", ".gd"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 460:
            errors.append(f"source file exceeds G57 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=separate_game_repository_integration_quality")


if __name__ == "__main__":
    main()
