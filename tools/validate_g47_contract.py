#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_ROOT = ROOT.parent / "world-transvoxel-terrain"

REQUIRED_FILES = (
    "docs/G47_VALIDATION_WORKAROUND_REMOVAL_QUALITY.md",
    "tests/g47_validation_workaround_removal_quality.gd",
    "tools/g47_validation_workaround_removal_quality.py",
)

REQUIRED_PHRASES = {
    "docs/G47_VALIDATION_WORKAROUND_REMOVAL_QUALITY.md": (
        "WT_VALIDATION_G47_CONTRACT_PASS",
        "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS",
        "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS",
        "Validation workaround removal quality",
        "quarantined historical backend",
    ),
    "tests/g47_validation_workaround_removal_quality.gd": (
        "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS",
        "wt_terrain_material_applicator.gd",
        "terrain_addon_material_applicator",
        "terrain_addon_mesh_stats",
    ),
    "tools/g47_validation_workaround_removal_quality.py": (
        "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS",
        "validation_workaround_removal_quality",
        "direct_runtime_backend_refs=0",
    ),
    "scenes/validation_playtest.tscn": (
        "wt_terrain_material_applicator.gd",
        "ValidationTerrainMaterials",
    ),
    "scripts/validation_playtest.gd": (
        "wt_terrain_mesh_stats.gd",
        "terrain_mesh_stats_implementation",
        "get_world_state_name",
    ),
    "README.md": (
        "G47 is the latest completed validation workaround removal quality gate",
        "python tools/g47_validation_workaround_removal_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G47 - Validation workaround removal quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G47 is the latest completed validation workaround removal quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G47 - Validation workaround removal quality",
        "G48 - Native hot-path boundary quality",
    ),
}

ADDON_REQUIRED = {
    "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd": (
        "class_name WtTerrainMaterialApplicator",
        "terrain_addon_material_applicator",
    ),
    "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader": (
        "shader_type spatial",
        "UV2.x",
    ),
    "addons/world_transvoxel_terrain/debug/wt_terrain_mesh_stats.gd": (
        "class_name WtTerrainMeshStats",
        "terrain_addon_mesh_stats",
    ),
}

PROHIBITED = (
    "scripts/validation_terrain_materials.gd",
    "scripts/validation_mesh_stats.gd",
    "materials/validation_terrain_palette.gdshader",
    "materials/validation_terrain_palette.gdshader.uid",
)


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G47 file: {relative}")
    for relative in PROHIBITED:
        if (ROOT / relative).exists():
            errors.append(f"prohibited validation workaround remains: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative, phrases in ADDON_REQUIRED.items():
        path = TERRAIN_ROOT / relative
        if not path.is_file():
            errors.append(f"missing addon-owned helper: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for script in (ROOT / "scripts").glob("*.gd"):
        text = script.read_text(encoding="utf-8")
        if "get_backend_terrain" in text or "get_backend_world_state_name" in text:
            errors.append(f"runtime script still uses backend internals: {script.relative_to(ROOT)}")
    for rel in (
        "tests/g47_validation_workaround_removal_quality.gd",
        "tools/g47_validation_workaround_removal_quality.py",
        "tools/validate_g47_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G47 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G47_CONTRACT_PASS implementation=validation_workaround_removal_quality")


if __name__ == "__main__":
    main()
