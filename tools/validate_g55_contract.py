#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G55_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G55_MAP_GENERATOR_BUDGET_QUALITY.md",
    "tests/g55_map_generator_budget_quality.gd",
    "tools/g55_map_generator_budget_quality.py",
    "tools/validate_g55_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G55_MAP_GENERATOR_BUDGET_QUALITY.md": (
        "WT_VALIDATION_G55_CONTRACT_PASS",
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_PASS",
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS",
        "100 MiB hard per-file ceiling",
        "50 MiB target per-file ceiling",
        "30 seconds load-to-play ceiling",
    ),
    "tests/g55_map_generator_budget_quality.gd": (
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_PASS",
        "MAX_LOAD_MS",
        "FORBIDDEN_DENSE_FILES",
        "deterministic_reference",
    ),
    "tools/g55_map_generator_budget_quality.py": (
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS",
        "TARGET_FILE_BYTES",
        "HARD_FILE_BYTES",
        "MAX_LOAD_TO_PLAY_SECONDS",
    ),
    "README.md": (
        "G55 is a completed map generator budget quality gate",
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G55 - Map generator budget quality",
        "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track:",
        "G55 - Map generator budget quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G55 locked map generator budget behavior",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G55 is a completed map generator budget quality gate",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G55 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G55 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".gd", ".py"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G55 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=map_generator_budget_quality")


if __name__ == "__main__":
    main()
