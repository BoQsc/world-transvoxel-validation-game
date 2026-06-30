#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G50_TERRAIN_PROFILE_STANDARD_QUALITY.md",
    "scripts/validation_profile_standard_contract.gd",
    "tests/g50_terrain_profile_standard_quality.gd",
    "tools/g50_terrain_profile_standard_quality.py",
    "tools/validate_g50_contract.py",
)
REQUIRED_PHRASES = {
    "docs/G50_TERRAIN_PROFILE_STANDARD_QUALITY.md": (
        "WT_VALIDATION_G50_CONTRACT_PASS",
        "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_PASS",
        "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS",
        "Terrain profile standard quality",
        "g50_seeded_procedural_2k",
        "seed: `50050`",
        "50 MiB target",
        "100 MiB ceiling",
    ),
    "scripts/validation_profile_catalog.gd": (
        "g50_seeded_procedural_2k",
        "g50-seeded-procedural",
        "50050",
        "procedural.wtseed",
    ),
    "scripts/validation_profile_standard_contract.gd": (
        "terrain_profile_standard_contract_v1",
        "flat_baseline",
        "mountain_8x8",
        "g19_compact_2k_on_demand",
        "g50_seeded_procedural_2k",
        "MAX_LOAD_TO_PLAY_SECONDS",
    ),
    "tests/g50_terrain_profile_standard_quality.gd": (
        "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_PASS",
        "flat_resources",
        "mountain_resources",
        "compact_resources",
        "seeded_resources",
        "max_profile_load_ms",
    ),
    "tools/g50_terrain_profile_standard_quality.py": (
        "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS",
        "generate_worlds",
        "assert_profile_budgets",
        "MAX_LOAD_TO_PLAY_SECONDS",
    ),
    "README.md": (
        "G50 is the latest completed terrain profile standard quality gate",
        "python tools/g50_terrain_profile_standard_quality.py",
        "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G50 - Terrain profile standard quality",
        "g50_seeded_procedural_2k",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G50",
        "The next milestone after G50 is G51",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G50 locked the terrain profile standard",
        "The immediate direction after G50 is G51",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G50 is the latest completed terrain profile standard quality gate",
        "Current state after G50",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G50 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for rel in (
        "scripts/validation_profile_catalog.gd",
        "scripts/validation_profile_standard_contract.gd",
        "tests/g50_terrain_profile_standard_quality.gd",
        "tools/g50_terrain_profile_standard_quality.py",
        "tools/validate_g50_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G50 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G50_CONTRACT_PASS implementation=terrain_profile_standard_quality")


if __name__ == "__main__":
    main()
