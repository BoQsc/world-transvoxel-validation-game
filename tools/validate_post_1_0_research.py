#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_POST_1_0_RESEARCH_PASS"

REQUIRED_PHRASES = {
    "docs/POST_1_0_RESEARCH_AND_ROADMAP.md": (
        "Status: post-1.0 research contract; P1 and P2 complete, P3 next",
        "Terrain 1.0 ended at G60",
        "without appending G61",
        "P1 - Game-world addon extraction and production boundary",
        "Status: complete",
        "WT_VALIDATION_P1_CONTRACT_PASS",
        "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_SMOKE_PASS",
        "world-transvoxel-gameworld",
        "world_transvoxel_gameworld",
        "addons/world_transvoxel_gameworld",
        "public root node: `WtGameWorld`",
        "historical prototype",
        "Do not use `world-transvoxel-core`",
        "P2 - Production integration game proof",
        "WT_VALIDATION_P2_CONTRACT_PASS",
        "WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS",
        "P3 - Scale and coordinate policy beyond compact 2K",
        "Status: next",
        "P4 - Rendering and object-density foundation",
        "P5 - Optional GPU/compute acceleration proof",
        "P6 - Water/lava research prototype",
        "P7 - Vegetation and biome prototype",
        "P8 - Voxel/block building prototype",
        "Start P3",
        "https://docs.godotengine.org/en/stable/tutorials/shaders/compute_shaders.html",
        "https://docs.godotengine.org/en/stable/tutorials/physics/large_world_coordinates.html",
        "https://transvoxel.org/",
        "https://github.com/EricLengyel/Transvoxel",
    ),
    "README.md": (
        "docs/POST_1_0_RESEARCH_AND_ROADMAP.md",
        "WT_VALIDATION_POST_1_0_RESEARCH_PASS",
        "WT_VALIDATION_P1_CONTRACT_PASS",
        "WT_VALIDATION_P2_CONTRACT_PASS",
        "next=P3_scale_coordinate_policy",
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
    print(f"{MARKER} completed=P1_gameworld_addon_extraction,P2_production_integration_game_proof next=P3_scale_coordinate_policy")


if __name__ == "__main__":
    main()
