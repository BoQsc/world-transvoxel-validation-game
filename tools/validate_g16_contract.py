#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G16_GENERATED_128X128_PLAYABLE_STREAMING.md",
    "tools/generated_fixture_source_writer.py",
    "tools/g16_generated_128x128_playable_streaming_smoke.py",
    "tests/g16_generated_128x128_playable_streaming_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "tools/validate_g16_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G16_GENERATED_128X128_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G16_CONTRACT_PASS",
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_PASS",
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS",
        "g16_generated_128x128",
        "128 by 128 dense generated terrain fixture",
        "16384 generated pages",
        "near-2K generated terrain",
        "streamed source writer",
        "9/25/25/25/9 active render/collision resources",
        "MAX_ACTIVE_RESOURCES := 25",
        "1095850340",
        "547925170",
    ),
    "tools/g16_generated_128x128_playable_streaming_smoke.py": (
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID = \"g16_generated_128x128\"",
        "DIMENSIONS = (2053, 65, 2053)",
        "SOURCE_REVISION = 1612800",
        "CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(128) for x in range(128))",
        "EXPECTED_DENSITY_BYTES = 1095850340",
        "EXPECTED_MATERIAL_BYTES = 547925170",
        "write_streamed_height_source",
        "vertical_coverage",
        "\"source_writer\": \"streamed_height_source\"",
        "g16_generated_128x128_playable_streaming_report.json",
    ),
    "tests/g16_generated_128x128_playable_streaming_smoke.gd": (
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID := &\"g16_generated_128x128\"",
        "EXPECTED_PAGE_COUNT := 16384",
        "MAX_ACTIVE_RESOURCES := 25",
        "PATH_SAMPLES",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g16_generated_128x128\"",
        "g16_generated_128x128_dense",
        "res://build/g16-generated-fixture/%s",
        "_is_generated_128x128",
    ),
    "tools/g13_generated_fixture_vertical_coverage_smoke.py": (
        "g16_vertical_coverage",
        "G16_PROFILE_ID",
        "G16_SOURCE_REVISION",
    ),
    "README.md": (
        "python tools/validate_g16_contract.py",
        "python tools/g16_generated_128x128_playable_streaming_smoke.py",
        "WT_VALIDATION_G16_CONTRACT_PASS",
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G16 - Generated 128x128 playable streaming",
        "WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS",
        "16384 generated pages",
        "near-2K generated terrain",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G16 file: {relative}")
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
    print("WT_VALIDATION_G16_CONTRACT_PASS implementation=generated_128x128_playable_streaming")


if __name__ == "__main__":
    main()
