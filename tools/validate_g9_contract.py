#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G9_SPARSE_2K_PLAYABLE_PROFILE.md",
    "tools/g9_sparse_2k_playable_profile_smoke.py",
    "tests/g9_sparse_2k_playable_profile_smoke.gd",
    "scripts/validation_profile_catalog.gd",
    "scripts/validation_playtest.gd",
    "tools/validate_g9_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G9_SPARSE_2K_PLAYABLE_PROFILE.md": (
        "WT_VALIDATION_G9_CONTRACT_PASS",
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS",
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS",
        "g8_sparse_2k",
        "g8_2000x2000_sparse.wtworld",
        "2000 blocks by 2000 blocks",
        "93 active sparse path resources",
        "render_fading_resources == 0",
        "does not claim a fully generated visible 2000×2000 terrain surface",
    ),
    "scripts/validation_profile_catalog.gd": (
        "&\"g8_sparse_2k\"",
        "g8_2000x2000_sparse.wtworld",
        "g8_sparse_2k_path",
        "return 93",
        "Vector3(1991.0, 8.0, 1991.0)",
    ),
    "scripts/validation_playtest.gd": (
        "ProfileCatalog.fixture_label",
        "\"fixture_label\"",
    ),
    "tests/g9_sparse_2k_playable_profile_smoke.gd": (
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS",
        "PROFILE_ID := &\"g8_sparse_2k\"",
        "EXPECTED_RESOURCES := 93",
        "MIN_TRIANGLES := 30000",
        "render_fading_resources",
        "submit_sphere_edit",
    ),
    "tools/g9_sparse_2k_playable_profile_smoke.py": (
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS",
        "prepare_sparse_fixture",
        "compose(project)",
        "g9_sparse_2k_playable_profile_report.json",
    ),
    "README.md": (
        "python tools/validate_g9_contract.py",
        "python tools/g9_sparse_2k_playable_profile_smoke.py",
        "WT_VALIDATION_G9_CONTRACT_PASS",
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G9 - Sparse 2K playable profile",
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS",
        "g8_sparse_2k",
        "93 active sparse path resources",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G9 file: {relative}")
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
    print("WT_VALIDATION_G9_CONTRACT_PASS implementation=sparse_2k_playable_profile")


if __name__ == "__main__":
    main()
