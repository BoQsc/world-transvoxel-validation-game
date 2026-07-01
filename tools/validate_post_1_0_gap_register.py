#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_POST_1_0_GAP_REGISTER_PASS"

REQUIRED_PHRASES = {
    "docs/POST_1_0_PRODUCTION_GAP_REGISTER.md": (
        "Status: active gap register; P1 and P2 complete, P3 next",
        "A completed baseline gate does not mean",
        "P3-SCALE-COORDINATES",
        "P4-TERRAIN-TEXTURES",
        "P4-RENDER-DENSITY",
        "P4-VISUAL-VALIDATION",
        "P4-EDITOR-UX",
        "P5-GPU-ACCELERATION",
        "P6-WATER-LAVA",
        "P7-VEGETATION-BIOMES",
        "P8-BLOCK-BUILDINGS",
        "POST-STORAGE-MIGRATION",
        "POST-LIFECYCLE-LOADING",
        "POST-INTERACTION-MINING",
        "POST-COLLISION-PHYSICS",
        "POST-LOD-EXPANSION",
        "POST-PERFORMANCE-PRESETS",
        "POST-ERROR-TELEMETRY",
        "POST-PACKAGING-RELEASE",
        "POST-GAMEWORLD-SCOPE",
        "POST-NETWORKING",
        "POST-PLANETS",
        "split-required",
        "Do not claim a production feature is complete because a baseline gate exists",
        "Do not add broad GDScript hot loops",
        "WT_VALIDATION_POST_1_0_GAP_REGISTER_PASS",
    ),
    "docs/POST_1_0_RESEARCH_AND_ROADMAP.md": (
        "docs/POST_1_0_PRODUCTION_GAP_REGISTER.md",
        "source of truth for discovered post-1.0 gaps",
        "P3-SCALE-COORDINATES",
        "P4-TERRAIN-TEXTURES",
    ),
    "README.md": (
        "docs/POST_1_0_PRODUCTION_GAP_REGISTER.md",
        "production gap register",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "POST_1_0_PRODUCTION_GAP_REGISTER.md",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "POST_1_0_PRODUCTION_GAP_REGISTER.md",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "POST_1_0_PRODUCTION_GAP_REGISTER.md",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing gap register dependency: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(f"{MARKER} next=P3_scale_coordinate_policy planned=P4_terrain_rendering_materials_object_density")


if __name__ == "__main__":
    main()
