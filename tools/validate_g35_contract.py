#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G35_TERRAIN_CORRECTNESS_ARTIFACT_QUALITY.md",
    "tests/g35_terrain_correctness_artifact_quality.gd",
    "tools/g35_terrain_correctness_artifact_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G35_TERRAIN_CORRECTNESS_ARTIFACT_QUALITY.md": (
        "WT_VALIDATION_G35_CONTRACT_PASS",
        "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS",
        "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS",
        "terrain correctness and artifact detection",
    ),
    "tests/g35_terrain_correctness_artifact_quality.gd": (
        "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS",
        "MAX_BACKEND_HEIGHT_ERROR",
        "MAX_NEIGHBOR_HEIGHT_DELTA",
        "MAX_DIAGONAL_PAIR_DELTA",
        "_audit_backend_agreement",
    ),
    "tools/g35_terrain_correctness_artifact_quality.py": (
        "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS",
        "terrain_correctness_artifact_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G35 is the active terrain correctness and artifact detection quality gate",
        "python tools/g35_terrain_correctness_artifact_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G35 - Terrain correctness artifact quality",
        "terrain correctness and artifact detection",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G35 is the active terrain correctness and artifact detection quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G35 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            if phrase not in text and phrase not in normalized:
                errors.append(f"{relative} missing phrase: {phrase}")
    for rel in (
        "tests/g35_terrain_correctness_artifact_quality.gd",
        "tools/g35_terrain_correctness_artifact_quality.py",
        "tools/validate_g35_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 320:
            errors.append(f"source file exceeds G35 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G35_CONTRACT_PASS implementation=terrain_correctness_artifact_quality")


if __name__ == "__main__":
    main()
