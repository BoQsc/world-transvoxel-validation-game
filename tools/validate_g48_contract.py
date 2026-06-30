#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_ROOT = ROOT.parent / "world-transvoxel-terrain"

REQUIRED_FILES = (
    "docs/G48_NATIVE_HOT_PATH_BOUNDARY_QUALITY.md",
    "tests/g48_native_hot_path_boundary_quality.gd",
    "tools/g48_native_hot_path_boundary_quality.py",
)
REQUIRED_PHRASES = {
    "docs/G48_NATIVE_HOT_PATH_BOUNDARY_QUALITY.md": (
        "WT_VALIDATION_G48_CONTRACT_PASS",
        "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS",
        "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS",
        "Native hot-path boundary quality",
        "generation, meshing, streaming, edit application, and storage",
    ),
    "tests/g48_native_hot_path_boundary_quality.gd": (
        "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS",
        "get_hot_path_boundary_summary",
        "world_transvoxel_native_backend",
        "gdscript_hot_loops=0",
        "submit_edit_batch",
    ),
    "tools/g48_native_hot_path_boundary_quality.py": (
        "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS",
        "native_hot_path_boundary_quality",
        "gdscript_hot_loops=0",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G48 is the latest completed native hot-path boundary quality gate",
        "python tools/g48_native_hot_path_boundary_quality.py",
        "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G48 - Native hot-path boundary quality",
        "get_hot_path_boundary_summary",
        "gdscript_hot_loops=0",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G48 is the latest completed native hot-path boundary quality gate",
        "Current state after G48",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G48",
        "The next milestone after G48 is G49",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "Current claim boundary after G48",
        "native hot-path boundary evidence",
        "debug telemetry UI quality",
    ),
}
TERRAIN_REQUIRED = (
    "func get_hot_path_boundary_summary()",
    "terrain_addon_native_hot_path_boundary_v1",
    "world_transvoxel_native_backend",
    "density_volume_cell_loop",
    "terrain_mesh_build_loop",
)
FORBIDDEN_IN_RUNTIME_TEST = ("get_backend_terrain", "get_backend_world_state_name")


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G48 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    boundary_files = [
        TERRAIN_ROOT / "addons/world_transvoxel_terrain/runtime/wt_terrain_world.gd",
        TERRAIN_ROOT / "addons/world_transvoxel_terrain/runtime/wt_terrain_world_contracts.gd",
    ]
    if not all(path.is_file() for path in boundary_files):
        errors.append("missing terrain addon hot-path boundary files")
    text = "\n".join(path.read_text(encoding="utf-8") for path in boundary_files if path.is_file())
    for phrase in TERRAIN_REQUIRED:
        if phrase not in text:
            errors.append(f"terrain addon boundary missing phrase: {phrase}")
    test_text = (ROOT / "tests/g48_native_hot_path_boundary_quality.gd").read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_IN_RUNTIME_TEST:
        if forbidden in test_text:
            errors.append(f"G48 runtime test contains backend-internal call: {forbidden}")
    for rel in (
        "tests/g48_native_hot_path_boundary_quality.gd",
        "tools/g48_native_hot_path_boundary_quality.py",
        "tools/validate_g48_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G48 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G48_CONTRACT_PASS implementation=native_hot_path_boundary_quality")


if __name__ == "__main__":
    main()
