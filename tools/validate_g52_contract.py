#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_ROOT = ROOT.parent / "world-transvoxel"
TERRAIN_ROOT = ROOT.parent / "world-transvoxel-terrain"

REQUIRED_FILES = (
    "docs/G52_UNDERGROUND_TERRAIN_VARIATION_QUALITY.md",
    "tests/g52_underground_terrain_variation_quality.gd",
    "tools/g52_underground_terrain_variation_quality.py",
    "tools/validate_g52_contract.py",
)
REQUIRED_PHRASES = {
    "docs/G52_UNDERGROUND_TERRAIN_VARIATION_QUALITY.md": (
        "WT_VALIDATION_G52_CONTRACT_PASS",
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_PASS",
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS",
        "density_volume_vertical_strata_v1",
        "strata_materials=1,7,4",
        "edit_localized=1",
    ),
    "tests/g52_underground_terrain_variation_quality.gd": (
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_PASS",
        "PROCEDURAL_POINTS",
        "FLAT_POINTS",
        "request_authoritative_samples",
        "edit_localized=1",
    ),
    "tools/g52_underground_terrain_variation_quality.py": (
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS",
        "run_native_strata_tests",
        "procedural_strata=1",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G52 is the latest completed underground terrain variation quality gate",
        "python tools/g52_underground_terrain_variation_quality.py",
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G52 - Underground terrain variation quality",
        "density_volume_vertical_strata_v1",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G52 - Underground terrain variation quality",
        "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "underground density/material variation evidence",
        "G52 locked baseline underground",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G52 is the latest completed underground terrain variation quality gate",
        "underground density/material variation evidence",
    ),
}
WORLD_PHRASES = {
    "addons/world_transvoxel/src/storage/wt_procedural_world_source.cpp": (
        "WtProceduralTerrainVolumeSource",
        "depth >= 8.0",
        "depth >= 3.0",
        "depth >= 1.0",
    ),
    "tests/native/test_wt_m5_async_storage.cpp": (
        "procedural underground strata samples mismatch",
        "procedural_strata=1",
    ),
}
TERRAIN_PHRASES = {
    "addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd": (
        "density_volume_vertical_strata_v1",
        "UNDERGROUND_STRATA_MATERIAL_IDS",
        "flat_world_underground_contract",
    ),
    "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader": (
        "material_1_color",
        "material_7_color",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def check_phrases(root: Path, required: dict[str, tuple[str, ...]], errors: list[str]) -> None:
    for relative, phrases in required.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{path} missing phrase: {phrase}")


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G52 file: {relative}")
    check_phrases(ROOT, REQUIRED_PHRASES, errors)
    check_phrases(WORLD_ROOT, WORLD_PHRASES, errors)
    check_phrases(TERRAIN_ROOT, TERRAIN_PHRASES, errors)
    for path in (
        ROOT / "tests/g52_underground_terrain_variation_quality.gd",
        ROOT / "tools/g52_underground_terrain_variation_quality.py",
        ROOT / "tools/validate_g52_contract.py",
    ):
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G52 line limit: {path}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G52_CONTRACT_PASS implementation=underground_terrain_variation_quality")


if __name__ == "__main__":
    main()
