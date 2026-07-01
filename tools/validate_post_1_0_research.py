#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_POST_1_0_RESEARCH_PASS"

REQUIRED_PHRASES = {
    "docs/POST_1_0_RESEARCH_AND_ROADMAP.md": (
        "Status: post-1.0 research contract",
        "Terrain 1.0 ended at G60",
        "without appending G61",
        "P1 - Game-world addon extraction and production boundary",
        "world-transvoxel-gameworld",
        "Do not use `world-transvoxel-core`",
        "P2 - Production integration game proof",
        "P3 - Scale and coordinate policy beyond compact 2K",
        "P4 - Rendering and object-density foundation",
        "P5 - Optional GPU/compute acceleration proof",
        "P6 - Water/lava research prototype",
        "P7 - Vegetation and biome prototype",
        "P8 - Voxel/block building prototype",
        "Start P1",
        "https://docs.godotengine.org/en/stable/tutorials/shaders/compute_shaders.html",
        "https://docs.godotengine.org/en/stable/tutorials/physics/large_world_coordinates.html",
        "https://transvoxel.org/",
        "https://github.com/EricLengyel/Transvoxel",
    ),
    "README.md": (
        "docs/POST_1_0_RESEARCH_AND_ROADMAP.md",
        "WT_VALIDATION_POST_1_0_RESEARCH_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "docs/POST_1_0_RESEARCH_AND_ROADMAP.md",
        "post-1.0 roadmap",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing post-1.0 research file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(f"{MARKER} next=P1_game_world_addon_extraction")


if __name__ == "__main__":
    main()
