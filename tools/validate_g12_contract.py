#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G12_GENERATED_32X32_PLAYABLE_STREAMING.md",
    "tools/g12_generated_32x32_playable_streaming_smoke.py",
    "tests/g12_generated_32x32_playable_streaming_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "tools/validate_g12_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G12_GENERATED_32X32_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G12_CONTRACT_PASS",
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_PASS",
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS",
        "g12_generated_32x32",
        "32 by 32 dense generated terrain fixture",
        "1024 generated pages",
        "9/25/25/25/9 active render/collision resources",
        "MAX_ACTIVE_RESOURCES := 25",
        "does not load all 1024 generated pages as active resources",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g12_generated_32x32\"",
        "g12_generated_32x32_dense",
        "res://build/g12-generated-fixture/%s",
        "return [Vector3(8.0, 8.0, 8.0)]",
        "return 9",
    ),
    "tests/g12_generated_32x32_playable_streaming_smoke.gd": (
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID := &\"g12_generated_32x32\"",
        "EXPECTED_PAGE_COUNT := 1024",
        "MAX_ACTIVE_RESOURCES := 25",
        "PATH_SAMPLES",
        "query_chunk_state",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "tools/g12_generated_32x32_playable_streaming_smoke.py": (
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_PASS",
        "CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(32) for x in range(32))",
        "wt_bake.py",
        "copy_fixture_into_project",
        "g12_generated_32x32_playable_streaming_report.json",
    ),
    "README.md": (
        "python tools/validate_g12_contract.py",
        "python tools/g12_generated_32x32_playable_streaming_smoke.py",
        "WT_VALIDATION_G12_CONTRACT_PASS",
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G12 - Generated 32x32 playable streaming",
        "WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS",
        "g12_generated_32x32",
        "1024 generated pages",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G12 file: {relative}")
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
    print("WT_VALIDATION_G12_CONTRACT_PASS implementation=generated_32x32_playable_streaming")


if __name__ == "__main__":
    main()
