#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING.md",
    "tools/g23_real_compact_human_playable_streaming.py",
    "tools/validate_g23_contract.py",
    "tests/g23_real_compact_human_playable_streaming.gd",
    "tests/g23_real_compact_human_playable_streaming.gd.uid",
    "scripts/validation_player_viewer_driver.gd",
    "scripts/validation_player_factory.gd",
)

REQUIRED_PHRASES = {
    "docs/G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING.md": (
        "WT_VALIDATION_G23_CONTRACT_PASS",
        "WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_PASS",
        "player-driven playtest",
        "mouse motion changes the first-person camera",
        "player movement drives terrain viewer updates",
        "left click carves",
        "right click constructs/places",
    ),
    "scripts/validation_playtest.gd": (
        "player_driven_viewer_enabled",
        "PlayerViewerDriver",
        "player_viewer_updates",
        "_player_viewer_driver.update_from_player",
    ),
    "scripts/validation_profile_catalog.gd": (
        "Vector3(1032, 24, 1032)",
        "return [Vector3(1032.0, 8.0, 1032.0)]",
        "return 25",
    ),
    "scripts/validation_player_viewer_driver.gd": (
        "update_reference_viewer",
        "_minimum_xz_delta",
        "accepted_updates",
    ),
    "scripts/validation_terrain_interactor.gd": (
        "func _input(event: InputEvent) -> void:",
        "get_viewport().set_input_as_handled()",
    ),
    "tests/g23_real_compact_human_playable_streaming.gd": (
        "WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_PASS",
        "human_input_enabled = true",
        "InputEventMouseMotion",
        "root.push_input",
        "MOUSE_BUTTON_LEFT",
        "MOUSE_BUTTON_RIGHT",
        "player_viewer_updates",
    ),
    "tools/g23_real_compact_human_playable_streaming.py": (
        "WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_SMOKE_PASS",
        "prepare_project",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "real_compact_human_playable_streaming",
    ),
    "README.md": (
        "G23 fixes the failed human handoff",
        "python tools/validate_g23_contract.py",
        "python tools/g23_real_compact_human_playable_streaming.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G23 - Real compact human-playable streaming",
        "player movement drives terrain viewer updates",
        "left click carves",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G23 fixes the failed human handoff",
        "player-driven streaming",
        "real input path",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G23 file: {relative}")
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
                errors.append(f"source file exceeds G23 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G23_CONTRACT_PASS implementation=real_compact_human_playable_streaming")


if __name__ == "__main__":
    main()
