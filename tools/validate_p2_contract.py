#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
INTEGRATION_REPO = REPOSITORY_ROOT / "world-transvoxel-integration-game"
MARKER = "WT_VALIDATION_P2_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/P2_PRODUCTION_INTEGRATION_GAME_PROOF.md",
    "tools/p2_production_integration_game_quality.py",
    "tools/p2_production_integration_templates.py",
    "tools/templates/p2_production_integration/project.godot.txt",
    "tools/templates/p2_production_integration/main.tscn.txt",
    "tools/templates/p2_production_integration/main.gd.txt",
    "tools/templates/p2_production_integration/wt_production_player.gd.txt",
    "tools/templates/p2_production_integration/README.md.txt",
    "tools/templates/p2_production_integration/gitignore.txt",
    "tools/validate_p2_contract.py",
]
REQUIRED_PHRASES = {
    "docs/P2_PRODUCTION_INTEGRATION_GAME_PROOF.md": (
        "WT_VALIDATION_P2_CONTRACT_PASS",
        "WT_PRODUCTION_GAME_P2_PASS",
        "WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS",
        "generated_uid_artifacts_removed",
        "world_transvoxel_gameworld",
    ),
    "tools/p2_production_integration_game_quality.py": (
        "world-transvoxel-integration-game",
        "world_transvoxel_gameworld",
        "assert_no_validation_internals",
        "remove_generated_uid_artifacts",
        "project_godot",
    ),
    "tools/p2_production_integration_templates.py": (
        "_read_template",
        "p2_production_integration",
        "main.gd.txt",
    ),
    "tools/templates/p2_production_integration/main.gd.txt": (
        "WT_PRODUCTION_GAME_P2_PASS",
        "FirstPersonCamera",
        "Crosshair",
        "ProfileSelector",
        "TelemetryLabel",
        "world_transvoxel_gameworld",
    ),
    "tools/templates/p2_production_integration/wt_production_player.gd.txt": (
        "submit_edit_input",
        "set_human_input_enabled",
    ),
    "tools/templates/p2_production_integration/project.godot.txt": (
        "res://addons/world_transvoxel_gameworld/plugin.cfg",
        "run/main_scene=\"res://scenes/main.tscn\"",
    ),
    "tools/templates/p2_production_integration/gitignore.txt": (
        "*.uid",
    ),
}
INTEGRATION_PHRASES = {
    "project.godot": (
        "res://addons/world_transvoxel_gameworld/plugin.cfg",
        "run/main_scene=\"res://scenes/main.tscn\"",
    ),
    "README.md": (
        "world_transvoxel_gameworld",
        "P2 production integration game proof",
    ),
    "scripts/main.gd": (
        "WT_PRODUCTION_GAME_P2_PASS",
        "FirstPersonCamera",
        "ProfileSelector",
    ),
    "scripts/wt_production_player.gd": (
        "submit_edit_input",
        "set_human_input_enabled",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing P2 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    if INTEGRATION_REPO.is_dir():
        for relative, phrases in INTEGRATION_PHRASES.items():
            path = INTEGRATION_REPO / relative
            if not path.is_file():
                errors.append(f"missing integration repo file: {relative}")
                continue
            text = path.read_text(encoding="utf-8")
            for phrase in phrases:
                if not normalized_contains(text, phrase):
                    errors.append(f"integration {relative} missing phrase: {phrase}")
        if (INTEGRATION_REPO / "addons" / "world_transvoxel_game_world").exists():
            errors.append("integration repo still contains old world_transvoxel_game_world addon")
        for path in INTEGRATION_REPO.rglob("*.uid"):
            if ".git" not in path.parts:
                errors.append(f"integration repo must not keep generated uid file: {path}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix == ".py" and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 520:
            errors.append(f"P2 source file exceeds line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=production_integration_game_proof")


if __name__ == "__main__":
    main()
