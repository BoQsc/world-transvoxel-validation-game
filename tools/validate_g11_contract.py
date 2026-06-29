#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G11_GENERATED_16X16_PLAYABLE_STREAMING.md",
    "tools/g11_generated_16x16_playable_streaming_smoke.py",
    "tests/g11_generated_16x16_playable_streaming_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "tools/validate_g11_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G11_GENERATED_16X16_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G11_CONTRACT_PASS",
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS",
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS",
        "g11_generated_16x16",
        "16 by 16 dense generated terrain fixture",
        "256 generated pages",
        "9/25/25/25/9 active render/collision resources",
        "MAX_ACTIVE_RESOURCES := 25",
        "does not load all 256 generated pages as active resources",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g11_generated_16x16\"",
        "g11_generated_16x16_dense",
        "res://build/g11-generated-fixture/%s",
        "return [Vector3(8.0, 8.0, 8.0)]",
        "return 9",
    ),
    "tests/g11_generated_16x16_playable_streaming_smoke.gd": (
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID := &\"g11_generated_16x16\"",
        "EXPECTED_PAGE_COUNT := 256",
        "MAX_ACTIVE_RESOURCES := 25",
        "PATH_SAMPLES",
        "query_chunk_state",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "tools/g11_generated_16x16_playable_streaming_smoke.py": (
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS",
        "CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(16) for x in range(16))",
        "wt_bake.py",
        "copy_fixture_into_project",
        "g11_generated_16x16_playable_streaming_report.json",
    ),
    "README.md": (
        "python tools/validate_g11_contract.py",
        "python tools/g11_generated_16x16_playable_streaming_smoke.py",
        "WT_VALIDATION_G11_CONTRACT_PASS",
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G11 - Generated 16x16 playable streaming",
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS",
        "g11_generated_16x16",
        "256 generated pages",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G11 file: {relative}")
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
    print("WT_VALIDATION_G11_CONTRACT_PASS implementation=generated_16x16_playable_streaming")


if __name__ == "__main__":
    main()
