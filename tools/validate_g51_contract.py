#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_ROOT = ROOT.parent / "world-transvoxel-terrain"

REQUIRED_FILES = (
    "docs/G51_MATERIAL_TEXTURE_PIPELINE_QUALITY.md",
    "tests/g51_material_texture_pipeline_quality.gd",
    "tools/g51_material_texture_pipeline_quality.py",
    "tools/validate_g51_contract.py",
)
REQUIRED_PHRASES = {
    "docs/G51_MATERIAL_TEXTURE_PIPELINE_QUALITY.md": (
        "WT_VALIDATION_G51_CONTRACT_PASS",
        "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_PASS",
        "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS",
        "Material texture pipeline quality",
        "16 by 16 `RGBA8`, 1024 bytes",
        "material_instance_stable=1",
    ),
    "tests/g51_material_texture_pipeline_quality.gd": (
        "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_PASS",
        "get_material_quality_summary",
        "material_instance_stable=1",
        "request_authoritative_sample",
        "STREAM_SAMPLES",
    ),
    "tools/g51_material_texture_pipeline_quality.py": (
        "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS",
        "material_texture_pipeline_quality",
        "MAX_TEXTURE_BYTES",
        "material_instance_stable",
    ),
    "README.md": (
        "G51 is the latest completed material texture pipeline quality gate",
        "python tools/g51_material_texture_pipeline_quality.py",
        "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G51 - Material texture pipeline quality",
        "terrain_material_texture_pipeline_v1",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G51",
        "The next milestone after G51 is G52",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G51 locked the material texture pipeline",
        "The immediate direction after G51 is G52",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G51 is the latest completed material texture pipeline quality gate",
        "Current state after G51",
    ),
}
ADDON_PHRASES = {
    "addons/world_transvoxel_terrain/material/wt_terrain_material_profile.gd": (
        "terrain_material_profile_contract_v1",
        "texture_bytes",
        "material_ids_csv",
        "deterministic_palette",
    ),
    "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd": (
        "terrain_material_texture_pipeline_v1",
        "get_material_quality_summary",
        "texture_checksum",
        "material_instance_id",
    ),
    "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader": (
        "UV2.x",
        "checker_texture",
        "material_4_color",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G51 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative, phrases in ADDON_PHRASES.items():
        path = TERRAIN_ROOT / relative
        if not path.is_file():
            errors.append(f"missing addon material file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for path in (
        ROOT / "tests/g51_material_texture_pipeline_quality.gd",
        ROOT / "tools/g51_material_texture_pipeline_quality.py",
        ROOT / "tools/validate_g51_contract.py",
        TERRAIN_ROOT / "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd",
    ):
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G51 line limit: {path}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G51_CONTRACT_PASS implementation=material_texture_pipeline_quality")


if __name__ == "__main__":
    main()
