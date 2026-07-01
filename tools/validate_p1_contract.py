#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
GAMEWORLD_REPO = REPOSITORY_ROOT / "world-transvoxel-gameworld"
MARKER = "WT_VALIDATION_P1_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/P1_GAMEWORLD_ADDON_EXTRACTION_QUALITY.md",
    "tests/p1_gameworld_addon_extraction_quality.gd",
    "tools/p1_gameworld_addon_extraction_quality.py",
    "tools/validate_p1_contract.py",
]
GAMEWORLD_REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "project.godot",
    "addons/world_transvoxel_gameworld/plugin.cfg",
    "addons/world_transvoxel_gameworld/plugin.gd",
    "addons/world_transvoxel_gameworld/wt_game_world_node.gd",
]
REQUIRED_PHRASES = {
    "docs/P1_GAMEWORLD_ADDON_EXTRACTION_QUALITY.md": (
        "WT_VALIDATION_P1_CONTRACT_PASS",
        "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_PASS",
        "world_transvoxel_gameworld",
    ),
    "tests/p1_gameworld_addon_extraction_quality.gd": (
        "res://addons/world_transvoxel_gameworld/wt_game_world_node.gd",
        "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_PASS",
    ),
    "tools/p1_gameworld_addon_extraction_quality.py": (
        "GAMEWORLD_REPO",
        "world_transvoxel_gameworld",
        "assert_no_validation_internals",
    ),
}
GAMEWORLD_PHRASES = {
    "README.md": (
        "world_transvoxel_gameworld",
        "must not contain validation-game scripts",
    ),
    "addons/world_transvoxel_gameworld/plugin.cfg": (
        "World Transvoxel Gameworld",
        "plugin.gd",
    ),
    "addons/world_transvoxel_gameworld/wt_game_world_node.gd": (
        'const ADDON_ID := "world_transvoxel_gameworld"',
        "configure_game_world",
        "submit_sphere_edit",
        "get_game_world_summary",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing P1 file: {relative}")
    for relative in GAMEWORLD_REQUIRED_FILES:
        if not (GAMEWORLD_REPO / relative).is_file():
            errors.append(f"missing gameworld repo file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative, phrases in GAMEWORLD_PHRASES.items():
        path = GAMEWORLD_REPO / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"gameworld {relative} missing phrase: {phrase}")
    for path in (GAMEWORLD_REPO / "addons" / "world_transvoxel_gameworld").rglob("*"):
        if path.is_file() and path.name.endswith(".uid"):
            errors.append(f"gameworld repo must not track uid file: {path}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".py", ".gd"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 360:
            errors.append(f"P1 source file exceeds line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=gameworld_addon_extraction_quality")


if __name__ == "__main__":
    main()
