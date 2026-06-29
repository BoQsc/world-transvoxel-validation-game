#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G19_COMPACT_2K_ON_DEMAND.md",
    "tools/g19_compact_2k_on_demand_smoke.py",
    "tests/g19_compact_2k_on_demand_smoke.gd",
    "tests/g19_compact_2k_on_demand_smoke.gd.uid",
    "tools/validate_g19_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G19_COMPACT_2K_ON_DEMAND.md": (
        "WT_VALIDATION_G19_CONTRACT_PASS",
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS",
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS",
        "G16 and G17 remain stress evidence only",
        "128 by 128 chunks",
        "2048 by 2048 blocks",
        "no dense source directory",
        "no baked world directory",
        "50 MiB per-file target",
        "100 MiB total generated-object-root ceiling",
    ),
    "tools/g19_compact_2k_on_demand_smoke.py": (
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS",
        "MAX_GENERATED_FILE_BYTES = 50 * 1024 * 1024",
        "MAX_GENERATED_TOTAL_BYTES = 100 * 1024 * 1024",
        "FORBIDDEN_ARTIFACT_DIRS",
        "FORBIDDEN_PROJECT_FILES",
        "compact_2k_on_demand_procedural_streaming",
    ),
    "tests/g19_compact_2k_on_demand_smoke.gd": (
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS",
        "PROFILE_ID := &\"g19_compact_2k_on_demand\"",
        "EXPECTED_PAGE_COUNT := 16384",
        "MAX_ACTIVE_RESOURCES := 25",
        "FORBIDDEN_DENSE_FILES",
        "dense_world_files=0",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g19_compact_2k_on_demand\"",
        "g19_compact_2k_on_demand",
        "GenerationProfile.SourceMode.DETERMINISTIC_REFERENCE",
        "world_chunk_count_x = 128",
        "world_chunk_count_z = 128",
        "source_revision = 190019",
        "res://build/g19-compact-on-demand/%s",
        "procedural.wtseed",
    ),
    "README.md": (
        "G19 implements that compact near-2K on-demand path",
        "python tools/validate_g19_contract.py",
        "python tools/g19_compact_2k_on_demand_smoke.py",
        "WT_VALIDATION_G19_CONTRACT_PASS",
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G19 - Compact 2K on-demand procedural streaming",
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS",
        "not a dense `.wtworld` manifest",
        "25 active render",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G19 implements the first compact near-2K on-demand path",
        "deterministic procedural descriptor",
        "no `world.wtworld`",
        "50 MiB target per-file",
        "100 MiB total budget",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G19 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G19_CONTRACT_PASS implementation=compact_2k_on_demand")


if __name__ == "__main__":
    main()
