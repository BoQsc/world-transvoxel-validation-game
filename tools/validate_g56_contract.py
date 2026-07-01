#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G56_CONTRACT_PASS"

REQUIRED_FILES = [
    "addons/world_transvoxel_game_world/plugin.cfg",
    "addons/world_transvoxel_game_world/plugin.gd",
    "addons/world_transvoxel_game_world/wt_game_world_node.gd",
    "docs/G56_GAME_WORLD_ADDON_PROTOTYPE_QUALITY.md",
    "tests/g56_game_world_addon_prototype_quality.gd",
    "tools/g56_game_world_addon_prototype_quality.py",
    "tools/validate_g56_contract.py",
]

REQUIRED_PHRASES = {
    "addons/world_transvoxel_game_world/wt_game_world_node.gd": (
        "ADDON_ID",
        "API_VERSION",
        "setup_standard_world",
        "attach_player",
        "update_player_viewer",
        "submit_sphere_edit",
        "get_game_world_summary",
    ),
    "tests/g56_game_world_addon_prototype_quality.gd": (
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_PASS",
        "WorldTransvoxelGameWorld",
        "player_viewer_updates",
        "submit_sphere_edit",
    ),
    "tools/g56_game_world_addon_prototype_quality.py": (
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS",
        "world_transvoxel_game_world",
        "run_project_import",
    ),
    "tools/compose_validation_project.py": (
        "world_transvoxel_game_world",
    ),
    "docs/G56_GAME_WORLD_ADDON_PROTOTYPE_QUALITY.md": (
        "WT_VALIDATION_G56_CONTRACT_PASS",
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_PASS",
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS",
    ),
    "README.md": (
        "G56 is a completed game-world addon prototype quality gate",
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G56 - Game-world addon prototype quality",
        "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track:",
        "G56 - Game-world addon prototype quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G56 locked the game-world addon prototype boundary",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G56 is a completed game-world addon prototype quality gate",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G56 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G56 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".gd", ".py"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 320:
            errors.append(f"source file exceeds G56 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=game_world_addon_prototype_quality")


if __name__ == "__main__":
    main()
