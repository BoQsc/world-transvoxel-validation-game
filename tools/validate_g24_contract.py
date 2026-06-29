#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE.md",
    "tests/g24_autonomous_large_terrain_acceptance.gd",
    "tests/g24_autonomous_large_terrain_acceptance.gd.uid",
    "tools/g24_autonomous_large_terrain_acceptance.py",
    "tools/validate_g24_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE.md": (
        "WT_VALIDATION_G24_CONTRACT_PASS",
        "WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_PASS",
        "capped active-window regression evidence",
        "2048 by 2048 terrain descriptor",
        "superseded by G25",
    ),
    "tests/g24_autonomous_large_terrain_acceptance.gd": (
        "WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_PASS",
        "MAP_BLOCKS := 2048",
        "EXPECTED_PAGE_COUNT := 16384",
        "ROUTE",
        "root.push_input",
        "MOUSE_BUTTON_LEFT",
        "MOUSE_BUTTON_RIGHT",
        "CAPTURE_ROOT",
        "FileAccess.file_exists",
        "_set_capture_overlays_visible",
        "dense_world_files=0",
    ),
    "tools/g24_autonomous_large_terrain_acceptance.py": (
        "WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "autonomous_large_terrain_acceptance",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G24 is now reclassified as a capped active-window regression",
        "python tools/validate_g24_contract.py",
        "python tools/g24_autonomous_large_terrain_acceptance.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G24 - Autonomous large-terrain acceptance",
        "G24 is superseded by G25",
        "2048 by 2048",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G24 is reclassified as capped active-window regression evidence",
        "does not prove the player can see a full 2048 by 2048 terrain",
        "2048 by 2048",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G24 file: {relative}")
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
                errors.append(f"source file exceeds G24 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G24_CONTRACT_PASS implementation=autonomous_large_terrain_acceptance")


if __name__ == "__main__":
    main()
