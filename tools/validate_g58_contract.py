#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G58_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G58_DOCUMENTATION_EXAMPLES_QUALITY.md",
    "docs/TERRAIN_ADOPTION_EXAMPLES.md",
    "tools/g58_documentation_examples_quality.py",
    "tools/validate_g58_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G58_DOCUMENTATION_EXAMPLES_QUALITY.md": (
        "WT_VALIDATION_G58_CONTRACT_PASS",
        "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_PASS",
        "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS",
    ),
    "docs/TERRAIN_ADOPTION_EXAMPLES.md": (
        "## Installation",
        "## Profile setup",
        "## Terrain editing",
        "## Storage",
        "## Telemetry",
        "## Troubleshooting",
        "world_transvoxel_game_world",
    ),
    "tools/g58_documentation_examples_quality.py": (
        "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS",
        "TERRAIN_ADOPTION_EXAMPLES.md",
        "world-transvoxel-integration-game",
    ),
    "README.md": (
        "G58 is the latest completed documentation examples quality gate",
        "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS",
        "Next terrain work is G59 versioning release contract quality",
    ),
    "docs/ROADMAP.md": (
        "## G58 - Documentation examples quality",
        "WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G58",
        "The next milestone after G58 is G59",
        "G58 - Documentation examples quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "Current claim boundary after G58",
        "documentation examples evidence",
        "immediate direction after G58 is G59",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G58 is the latest completed documentation examples quality gate",
        "Next terrain work is G59 versioning release contract quality",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G58 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G58 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".py", ".gd"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G58 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=documentation_examples_quality")


if __name__ == "__main__":
    main()
