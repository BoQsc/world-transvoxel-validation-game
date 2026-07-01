#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G60_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G60_TERRAIN_1_0_RELEASE_CANDIDATE_QUALITY.md",
    "tools/g60_terrain_1_0_release_candidate_quality.py",
    "tools/validate_g60_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G60_TERRAIN_1_0_RELEASE_CANDIDATE_QUALITY.md": (
        "WT_VALIDATION_G60_CONTRACT_PASS",
        "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_PASS",
        "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS",
        "Terrain 1.0 release-candidate quality is reached",
    ),
    "tools/g60_terrain_1_0_release_candidate_quality.py": (
        "validate_g41_contract.py",
        "validate_g59_contract.py",
        "g41_runtime_frame_budget_telemetry_quality.py",
        "g59_versioning_release_contract_quality.py",
        "critical_blockers",
    ),
    "README.md": (
        "G60 is the latest completed terrain quality gate",
        "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS",
        "Terrain 1.0 is reached for this validated scope",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G60",
        "G60 is the Terrain 1.0 finish line",
        "next=post_1_0_backlog",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G60 is the latest completed Terrain 1.0 release-candidate quality gate",
        "Future work after G60 belongs to explicit post-1.0 roadmaps",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "Current claim boundary after G60",
        "G60 release-candidate evidence",
        "Future systems belong to explicit post-1.0 roadmaps",
    ),
    "docs/ROADMAP.md": (
        "## G60 - Terrain 1.0 release candidate quality",
        "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G60 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G60 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".py", ".gd"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G60 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=terrain_1_0_release_candidate_quality")


if __name__ == "__main__":
    main()
