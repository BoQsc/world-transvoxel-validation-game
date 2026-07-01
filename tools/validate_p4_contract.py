#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_REPO = ROOT.parent / "world-transvoxel-terrain"
MARKER = "WT_VALIDATION_P4_CONTRACT_PASS"

REQUIRED_PHRASES = {
    ROOT / "docs/P4_PRODUCTION_TERRAIN_RENDERING_MATERIALS_OBJECT_DENSITY.md": (
        "P4-TERRAIN-TEXTURES",
        "P4-RENDER-DENSITY",
        "P4-VISUAL-VALIDATION",
        "P4-EDITOR-UX",
        "editor_ux_moved_to_p5",
        "WT_VALIDATION_P4_PRODUCTION_RENDERING_MATERIALS_OBJECT_DENSITY_PASS",
    ),
    ROOT / "tools/p4_production_rendering_materials_object_density.py": (
        "terrain_production_material_texture_pipeline_v1",
        "terrain_albedo_atlas",
        "active_resource_capacity",
        "P5_gpu_acceleration",
    ),
    TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_profile.gd": (
        "production_texture_slots",
        "sample_material_names",
        "texture_import_policy",
    ),
    TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd": (
        "PRODUCTION_QUALITY_IMPLEMENTATION",
        "production_texture_budget_bytes",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for path, phrases in REQUIRED_PHRASES.items():
        if not path.is_file():
            errors.append(f"missing P4 file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{path} missing phrase: {phrase}")
        if path.suffix in {".py", ".gd", ".gdshader"} and len(text.splitlines()) > 300:
            errors.append(f"P4 source file exceeds line limit: {path}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=production_rendering_materials_object_density")


if __name__ == "__main__":
    main()
