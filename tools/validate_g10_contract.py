#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING.md",
    "tools/g10_single_viewer_2k_playable_streaming_smoke.py",
    "tests/g10_single_viewer_2k_playable_streaming_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "tools/validate_g10_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G10_CONTRACT_PASS",
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS",
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS",
        "g10_single_viewer_2k",
        "single playable viewer",
        "9/25/25/25/9 active render/collision resources",
        "MAX_ACTIVE_RESOURCES := 25",
        "does not keep all 93 sparse path resources active",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g10_single_viewer_2k\"",
        "g10_single_viewer_2k_path",
        "return [Vector3(8.0, 8.0, 8.0)]",
        "return 9",
        "g8_2000x2000_sparse.wtworld",
    ),
    "tests/g10_single_viewer_2k_playable_streaming_smoke.gd": (
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS",
        "PROFILE_ID := &\"g10_single_viewer_2k\"",
        "MAX_ACTIVE_RESOURCES := 25",
        "PATH_SAMPLES",
        "update_reference_viewer",
        "query_chunk_state",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "tools/g10_single_viewer_2k_playable_streaming_smoke.py": (
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS",
        "prepare_sparse_fixture",
        "compose(project)",
        "g10_single_viewer_2k_playable_streaming_report.json",
    ),
    "README.md": (
        "python tools/validate_g10_contract.py",
        "python tools/g10_single_viewer_2k_playable_streaming_smoke.py",
        "WT_VALIDATION_G10_CONTRACT_PASS",
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G10 - Single-viewer 2K playable streaming",
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS",
        "g10_single_viewer_2k",
        "does not keep all 93 sparse path resources active",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G10 file: {relative}")
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
    print("WT_VALIDATION_G10_CONTRACT_PASS implementation=single_viewer_2k_playable_streaming")


if __name__ == "__main__":
    main()
