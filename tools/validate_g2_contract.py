#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G2_FIRST_PERSON_PLAYABLE_BASELINE.md",
    "scripts/validation_playtest.gd",
    "scripts/validation_profile_catalog.gd",
    "scripts/validation_player.gd",
    "tests/g2_first_person_baseline_smoke.gd",
    "tools/g2_first_person_baseline_smoke.py",
    "tools/validate_g2_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G2_FIRST_PERSON_PLAYABLE_BASELINE.md": (
        "WT_VALIDATION_G2_CONTRACT_PASS",
        "WT_VALIDATION_G2_SMOKE_PASS",
        "flat generation profile",
        "scripted jump response",
        "Not claimed",
    ),
    "README.md": (
        "python tools/validate_g2_contract.py",
        "python tools/g2_first_person_baseline_smoke.py",
        "WT_VALIDATION_G2_CONTRACT_PASS",
        "WT_VALIDATION_G2_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G2 - First-person playable baseline",
        "Status: complete",
        "WT_VALIDATION_G2_SMOKE_PASS",
        "## G3 - Terrain generation modes",
        "WT_VALIDATION_G3_SMOKE_PASS",
    ),
    "scripts/validation_playtest.gd": (
        "flat_baseline",
        "ProfileCatalog.generation_profile",
        "first_person",
        "ValidationCrosshair",
    ),
    "scripts/validation_profile_catalog.gd": (
        "GenerationProfile.SourceMode.FLAT",
        "flat_baseline",
        "storage_profile",
    ),
    "scripts/validation_player.gd": (
        "request_test_jump",
        "vertical_velocity",
        "move_and_slide",
    ),
    "tests/g2_first_person_baseline_smoke.gd": (
        "WT_VALIDATION_G2_GODOT_PASS",
        "set_human_input_enabled(false)",
        "flat_baseline",
        "source_mode",
        "FLAT",
        "request_test_jump",
        "walk_motion",
        "jump_height",
    ),
    "tools/g2_first_person_baseline_smoke.py": (
        "WT_VALIDATION_G2_SMOKE_PASS",
        "g2_first_person_baseline_report.json",
        "compose(project)",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G2 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        rel = relative.as_posix()
        if ".git" in relative.parts or rel.startswith("artifacts/"):
            continue
        if path.is_file() and path.suffix in {".gd", ".py"}:
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) > 300:
                errors.append(f"source file exceeds G2 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G2_CONTRACT_PASS "
        "implementation=first_person_flat_baseline "
        "next=g3_terrain_generation_modes"
    )


if __name__ == "__main__":
    main()
