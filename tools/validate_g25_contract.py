#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G25_FULL_TERRAIN_VISUAL_BASELINE.md",
    "tests/g25_full_terrain_visual_baseline.gd",
    "tests/g25_full_terrain_visual_baseline.gd.uid",
    "tools/g25_full_terrain_visual_baseline.py",
    "tools/validate_g25_contract.py",
    "scenes/validation_playtest.tscn",
)

REQUIRED_PHRASES = {
    "docs/G25_FULL_TERRAIN_VISUAL_BASELINE.md": (
        "WT_VALIDATION_G25_CONTRACT_PASS",
        "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS",
        "full 2048 by 2048 terrain visual coverage",
        "active window is only the local Transvoxel detail layer",
        "No human validation is requested",
    ),
    "scenes/validation_playtest.tscn": (
        "ValidationFullTerrainVisual",
        "wt_terrain_full_map_visual.gd",
    ),
    "tests/g25_full_terrain_visual_baseline.gd": (
        "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS",
        "human_input_enabled = false",
        "EXPECTED_PAGE_COUNT := 16384",
        "MAP_BLOCKS := 2048",
        "active_window_is_detail_layer_only",
        "request_authoritative_samples",
        "full_map_overview.png",
        "dense_world_files=0",
    ),
    "tools/g25_full_terrain_visual_baseline.py": (
        "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_SMOKE_PASS",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "full_terrain_visual_baseline",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G25 replaces G24 as the active large-terrain visibility gate",
        "python tools/validate_g25_contract.py",
        "python tools/g25_full_terrain_visual_baseline.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G25 - Full terrain visual baseline",
        "full 2048 by 2048 terrain visual coverage",
        "local Transvoxel detail layer",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G25 replaces G24 as the active large-terrain visibility gate",
        "full 2048 by 2048 terrain visual coverage",
        "active window is only the local Transvoxel detail layer",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G25 file: {relative}")
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
                errors.append(f"source file exceeds G25 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G25_CONTRACT_PASS implementation=full_terrain_visual_baseline")


if __name__ == "__main__":
    main()
