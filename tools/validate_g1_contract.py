#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G1_HUMAN_VISIBLE_PLAYTEST.md",
    "scripts/validation_playtest.gd",
    "scripts/validation_player.gd",
    "tests/g1_visible_playtest_smoke.gd",
    "tests/g1_visual_capture.gd",
    "tools/g1_visible_playtest_smoke.py",
    "tools/g1_visual_capture.py",
    "tools/validate_g1_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G1_HUMAN_VISIBLE_PLAYTEST.md": (
        "Status: active",
        "WT_VALIDATION_G1_CONTRACT_PASS",
        "WT_VALIDATION_G1_GODOT_PASS",
        "WT_VALIDATION_G1_SMOKE_PASS",
        "WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS",
        "gray rectangle",
        "terrain MeshInstance3D",
    ),
    "README.md": (
        "Do not open the repository-root `project.godot`",
        "python tools/validate_g1_contract.py",
        "python tools/g1_visible_playtest_smoke.py",
        "python tools/g1_visual_capture.py --windowed",
        "WT_VALIDATION_G1_SMOKE_PASS",
        "WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G1 - Human-visible playtest confirmation",
        "Status: active",
        "WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS",
        "gray rectangle",
    ),
    "scripts/validation_playtest.gd": (
        "WT_VALIDATION_PLAYTEST_READY",
        "ValidationStatusOverlay",
        "ValidationMarkers",
        "ValidationPlayer",
        "look_at(_player.global_position",
        "no visible terrain MeshInstance3D",
        "terrain_triangles",
        "player_present",
        "_terrain_mesh_stats",
        "get_validation_summary",
    ),
    "scripts/validation_player.gd": (
        "extends CharacterBody3D",
        "human_input_enabled",
        "set_test_motion_direction",
        "Input.is_key_pressed",
        "move_and_slide",
    ),
    "tests/g1_visible_playtest_smoke.gd": (
        "WT_VALIDATION_G1_GODOT_PASS",
        "terrain_mesh_instances",
        "terrain_triangles",
        "set_human_input_enabled(false)",
        "player_motion",
        "status_text",
    ),
    "tools/g1_visible_playtest_smoke.py": (
        "WT_VALIDATION_G1_SMOKE_PASS",
        "g1_visible_playtest_report.json",
        "compose(project)",
    ),
    "tests/g1_visual_capture.gd": (
        "WT_VALIDATION_G1_VISUAL_CAPTURE_PASS",
        "viewport.get_texture().get_image()",
        "non_gray_samples",
        "center_bright_samples",
        "player_cyan_samples",
        "terrain_triangles",
        "set_human_input_enabled(false)",
    ),
    "tools/g1_visual_capture.py": (
        "WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS",
        "g1_visual_capture_report.json",
        "compose(project)",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G1 file: {relative}")
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
                errors.append(f"source file exceeds G1 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G1_CONTRACT_PASS "
        "implementation=human_visible_playtest_guard "
        "next=human_rerun_confirmation"
    )


if __name__ == "__main__":
    main()
