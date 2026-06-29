#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G14_GENERATED_64X64_PLAYABLE_STREAMING.md",
    "tools/generated_fixture_source_writer.py",
    "tools/g14_generated_64x64_playable_streaming_smoke.py",
    "tests/g14_generated_64x64_playable_streaming_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "tools/validate_g14_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G14_GENERATED_64X64_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G14_CONTRACT_PASS",
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS",
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS",
        "g14_generated_64x64",
        "64 by 64 dense generated terrain fixture",
        "4096 generated pages",
        "streamed source writer",
        "9/25/25/25/9 active render/collision resources",
        "MAX_ACTIVE_RESOURCES := 25",
    ),
    "tools/generated_fixture_source_writer.py": (
        "write_streamed_height_source",
        "density_path.open(\"wb\")",
        "material_path.open(\"wb\")",
        "density_file.write(density_row)",
    ),
    "tools/g14_generated_64x64_playable_streaming_smoke.py": (
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID = \"g14_generated_64x64\"",
        "DIMENSIONS = (1029, 65, 1029)",
        "CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(64) for x in range(64))",
        "write_streamed_height_source",
        "vertical_coverage",
        "\"source_writer\": \"streamed_height_source\"",
        "g14_generated_64x64_playable_streaming_report.json",
    ),
    "tests/g14_generated_64x64_playable_streaming_smoke.gd": (
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID := &\"g14_generated_64x64\"",
        "EXPECTED_PAGE_COUNT := 4096",
        "MAX_ACTIVE_RESOURCES := 25",
        "PATH_SAMPLES",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g14_generated_64x64\"",
        "g14_generated_64x64_dense",
        "res://build/g14-generated-fixture/%s",
        "return 9",
    ),
    "README.md": (
        "python tools/validate_g14_contract.py",
        "python tools/g14_generated_64x64_playable_streaming_smoke.py",
        "WT_VALIDATION_G14_CONTRACT_PASS",
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G14 - Generated 64x64 playable streaming",
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS",
        "4096 generated pages",
        "streamed source writer",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G14 file: {relative}")
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
    print("WT_VALIDATION_G14_CONTRACT_PASS implementation=generated_64x64_playable_streaming")


if __name__ == "__main__":
    main()
