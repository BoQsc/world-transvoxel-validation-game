#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE.md",
    "tests/g26_full_terrain_playable_experience.gd",
    "tests/g26_full_terrain_playable_experience.gd.uid",
    "tools/g26_full_terrain_playable_experience.py",
    "tools/validate_g26_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE.md": (
        "WT_VALIDATION_G26_CONTRACT_PASS",
        "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS",
        "first-person full-terrain playable experience",
        "human input is disabled for automation",
        "player-driven viewer updates remain active",
    ),
    "scripts/validation_playtest.gd": (
        "player_driven_viewer_enabled",
        "_player_viewer_driver.update_from_player",
    ),
    "tests/g26_full_terrain_playable_experience.gd": (
        "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS",
        "human_input_enabled = false",
        "ROUTE",
        "set_manual_camera_view",
        "submit_sphere_edit",
        "captures=%d",
        "dense_world_files=0",
    ),
    "tools/g26_full_terrain_playable_experience.py": (
        "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_SMOKE_PASS",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "full_terrain_playable_experience",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G26 is the active first-person full-terrain playable-experience gate",
        "python tools/validate_g26_contract.py",
        "python tools/g26_full_terrain_playable_experience.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G26 - Full terrain playable experience",
        "first-person full-terrain playable experience",
        "human input is disabled for automation",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G26 is the active first-person full-terrain playable-experience gate",
        "player-driven viewer updates remain active",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G26 file: {relative}")
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
        if path.is_file() and path.suffix in {".gd", ".py", ".gdshader"}:
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) > 300:
                errors.append(f"source file exceeds G26 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G26_CONTRACT_PASS implementation=full_terrain_playable_experience")


if __name__ == "__main__":
    main()
