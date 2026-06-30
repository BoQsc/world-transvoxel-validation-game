#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    PROFILE_ID,
    PROJECT_WORLD_ROOT,
    assert_compact_project_budget,
)
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g48_native_hot_path_boundary_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g48_native_hot_path_boundary_quality.gd"
MARKER = "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS"
TERRAIN_REPO = ROOT.parent / "world-transvoxel-terrain"
MAX_RUNTIME_SECONDS = 90.0

ADDON_RUNTIME_FILES = (
    "addons/world_transvoxel_terrain/runtime/wt_terrain_world.gd",
    "addons/world_transvoxel_terrain/runtime/wt_terrain_world_backend_ops.gd",
    "addons/world_transvoxel_terrain/runtime/wt_terrain_world_contracts.gd",
    "addons/world_transvoxel_terrain/runtime/wt_terrain_generation_backend.gd",
    "addons/world_transvoxel_terrain/runtime/wt_terrain_edit_bridge.gd",
    "addons/world_transvoxel_terrain/runtime/wt_world_transvoxel_bridge.gd",
    "addons/world_transvoxel_terrain/runtime/wt_terrain_runtime_audit.gd",
    "addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd",
    "addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd",
    "addons/world_transvoxel_terrain/edit/wt_terrain_edit_batch.gd",
    "addons/world_transvoxel_terrain/edit/wt_terrain_edit_operation.gd",
)
VALIDATION_RUNTIME_FILES = (
    "scripts/validation_playtest.gd",
    "scripts/validation_player.gd",
    "scripts/validation_terrain_interactor.gd",
    "scripts/validation_player_viewer_driver.gd",
    "scripts/validation_profile_catalog.gd",
    "scripts/validation_input_capture.gd",
    "scripts/validation_view_helpers.gd",
)
FORBIDDEN_HEAVY_TOKENS = (
    "ArrayMesh",
    "SurfaceTool",
    "Image.create",
    "get_pixel",
    "get_faces",
    "FileAccess.open",
    "store_buffer",
    "PackedFloat32Array",
    "for x in range",
    "for y in range",
    "for z in range",
)


def parse_marker(marker: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def scan_forbidden(root: Path, relatives: tuple[str, ...], forbid_backend: bool) -> list[str]:
    errors: list[str] = []
    for relative in relatives:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing hot-path audit file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_HEAVY_TOKENS:
            if token in text:
                errors.append(f"{relative} contains forbidden hot-path token: {token}")
        if forbid_backend and ("get_backend_terrain" in text or "get_backend_world_state_name" in text):
            errors.append(f"{relative} calls backend internals directly")
    return errors


def static_audit() -> dict[str, object]:
    errors = scan_forbidden(TERRAIN_REPO, ADDON_RUNTIME_FILES, False)
    errors.extend(scan_forbidden(ROOT, VALIDATION_RUNTIME_FILES, True))
    boundary_files = [
        TERRAIN_REPO / "addons/world_transvoxel_terrain/runtime/wt_terrain_world.gd",
        TERRAIN_REPO / "addons/world_transvoxel_terrain/runtime/wt_terrain_world_contracts.gd",
    ]
    boundary_text = "\n".join(path.read_text(encoding="utf-8") for path in boundary_files if path.is_file())
    for phrase in (
        "func get_hot_path_boundary_summary()",
        "terrain_addon_native_hot_path_boundary_v1",
        "world_transvoxel_native_backend",
        "density_volume_cell_loop",
        "terrain_mesh_build_loop",
    ):
        if phrase not in boundary_text:
            errors.append(f"terrain addon hot-path boundary missing phrase: {phrase}")
    if errors:
        raise RuntimeError("; ".join(errors))
    historical_backend_tests = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "tests").glob("*.gd"))
        if "get_backend_terrain" in path.read_text(encoding="utf-8")
    ]
    return {
        "audited_addon_runtime_files": len(ADDON_RUNTIME_FILES),
        "audited_validation_runtime_files": len(VALIDATION_RUNTIME_FILES),
        "hot_path_groups": 5,
        "gdscript_hot_loops": 0,
        "historical_backend_tests": len(historical_backend_tests),
    }


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_runtime_state(project)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(project), "--script", SCRIPT],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g48.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g48.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G48 native hot-path boundary failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G48 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("gdscript_hot_loops") != "0":
        raise RuntimeError(f"G48 marker fields invalid: {marker_line}")
    if fields.get("hot_paths") != "5" or fields.get("native_owned") != "5":
        raise RuntimeError(f"G48 hot-path ownership invalid: {marker_line}")
    if fields.get("edit_committed") != "1" or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G48 edit/budget fields invalid: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "0")) != 25:
            raise RuntimeError(f"G48 active resource field did not settle to 25: {field} in {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run native hot-path boundary quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    pin_scene_profile(project, PROFILE_ID)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "g48_native_hot_path_boundary_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} hot_paths=5 native_owned=5 "
        f"gdscript_hot_loops=0 quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
