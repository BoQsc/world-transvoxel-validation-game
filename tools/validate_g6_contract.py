#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G6_PROFILE_SELECTABLE_PLAYABLE_WORLD.md",
    "scripts/validation_profile_catalog.gd",
    "scripts/validation_mesh_stats.gd",
    "tests/g6_profile_selectable_playable_world_smoke.gd",
    "tools/g6_profile_selectable_playable_world_smoke.py",
    "tools/prepare_human_playtest.py",
    "tools/validate_g6_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G6_PROFILE_SELECTABLE_PLAYABLE_WORLD.md": (
        "WT_VALIDATION_G6_CONTRACT_PASS",
        "WT_VALIDATION_G6_SMOKE_PASS",
        "flat_8x8",
        "mountain_8x8",
        "first-person plus overview captures",
        "human_visual_verification",
        "WT_VALIDATION_HUMAN_PLAYTEST_READY",
        "prepare_human_playtest.py",
    ),
    "scripts/validation_playtest.gd": (
        "configure_playtest_profile",
        "playtest_profile_id",
        "set_manual_camera_view",
        "set_player_visual_visible",
        "_submit_profile_viewers",
    ),
    "scripts/validation_profile_catalog.gd": (
        "available_profile_ids",
        "flat_8x8",
        "mountain_8x8",
        "viewer_positions",
    ),
    "tests/g6_profile_selectable_playable_world_smoke.gd": (
        "WT_VALIDATION_G6_GODOT_PASS",
        "set_human_input_enabled(false)",
        "submit_sphere_edit",
        "colored_samples",
    ),
    "tools/g6_profile_selectable_playable_world_smoke.py": (
        "WT_VALIDATION_G6_SMOKE_PASS",
        "generate_worlds",
        "copy_worlds_into_project",
    ),
    "tools/prepare_human_playtest.py": (
        "WT_VALIDATION_HUMAN_PLAYTEST_READY",
        "pin_scene_profile",
        'playtest_profile_id = &"{profile}"',
        "copy_worlds_into_project",
        "run_project_import",
        "launch_project",
    ),
    "README.md": (
        "python tools/validate_g6_contract.py",
        "python tools/g6_profile_selectable_playable_world_smoke.py --windowed",
        "python tools/prepare_human_playtest.py --profile flat_8x8 --reuse-bake",
        "WT_VALIDATION_G6_CONTRACT_PASS",
        "WT_VALIDATION_G6_SMOKE_PASS",
        "WT_VALIDATION_HUMAN_PLAYTEST_READY",
    ),
    "docs/ROADMAP.md": (
        "## G6 - Profile-selectable playable world",
        "Status: complete",
        "WT_VALIDATION_G6_SMOKE_PASS",
        "prepare_human_playtest.py",
        "Human visual verification",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G6 file: {relative}")
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
                errors.append(f"source file exceeds G6 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G6_CONTRACT_PASS "
        "implementation=profile_selectable_playable_world "
        "next=human_visual_verification"
    )


if __name__ == "__main__":
    main()
