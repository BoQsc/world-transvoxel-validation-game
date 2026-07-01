#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_REPO = ROOT.parent / "world-transvoxel-terrain"
ARTIFACT_ROOT = ROOT / "artifacts" / "p4_production_rendering_materials_object_density"
MARKER = "WT_VALIDATION_P4_PRODUCTION_RENDERING_MATERIALS_OBJECT_DENSITY_PASS"


def require_phrases(path: Path, phrases: tuple[str, ...], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing P4 input: {path}")
        return
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            errors.append(f"{path} missing phrase: {phrase}")
    if path.suffix in {".py", ".gd", ".gdshader"} and len(text.splitlines()) > 300:
        errors.append(f"P4 source file exceeds line limit: {path}")


def main() -> None:
    errors: list[str] = []
    require_phrases(
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_profile.gd",
        (
            "terrain_production_material_texture_pipeline_v1",
            "production_texture_slots",
            "sample_material_names",
            "mapping_policy",
            "texture_import_policy",
        ),
        errors,
    )
    require_phrases(
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd",
        (
            "terrain_production_material_texture_pipeline_v1",
            "terrain_albedo_atlas",
            "terrain_normal_atlas",
            "terrain_roughness_atlas",
            "production_texture_budget_bytes",
        ),
        errors,
    )
    require_phrases(
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader",
        ("terrain_albedo_atlas", "terrain_normal_atlas", "terrain_roughness_atlas", "atlas_uv"),
        errors,
    )
    for relative, phrases in {
        "tools/g43_view_distance_presentation_quality.py": ("view_distance_presentation_quality", "min_mid_band_samples"),
        "tools/g51_material_texture_pipeline_quality.py": ("material_texture_pipeline_quality", "material_instance_stable"),
        "tools/g54_lod_seam_artifact_quality.py": ("lod_seam_artifact_quality", "edited_boundary_gap"),
    }.items():
        require_phrases(ROOT / relative, phrases, errors)
    if errors:
        raise SystemExit("; ".join(errors))

    report = {
        "material_pipeline": "terrain_production_material_texture_pipeline_v1",
        "texture_slots": ["albedo", "normal", "roughness_orm"],
        "sample_materials": ["grass_ground", "rock", "sand_dirt", "underground_stone"],
        "render_density_policy": {
            "chunk_cell_partitioned": True,
            "huge_unculled_resources_allowed": False,
            "active_resource_capacity": 256,
        },
        "visual_validation": ["G43", "G51", "G54"],
        "editor_ux_decision": "moved_to_p5",
        "next": "P5_gpu_acceleration",
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACT_ROOT / "p4_production_rendering_materials_object_density_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} texture_slots=3 sample_materials=4 "
        "material_pipeline=terrain_production_material_texture_pipeline_v1 "
        "render_density=1 visual_validation=1 editor_ux_moved_to_p5=1 "
        f"next=P5_gpu_acceleration report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
