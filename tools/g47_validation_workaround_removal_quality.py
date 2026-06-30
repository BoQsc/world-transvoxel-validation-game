#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import PROFILE_ID, assert_compact_project_budget
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g47_validation_workaround_removal_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g47_validation_workaround_removal_quality.gd"
MARKER = "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS"
TERRAIN_REPO = ROOT.parent / "world-transvoxel-terrain"
MAX_RUNTIME_SECONDS = 90.0
PROHIBITED_LOCAL = (
    "scripts/validation_terrain_materials.gd",
    "scripts/validation_mesh_stats.gd",
    "materials/validation_terrain_palette.gdshader",
    "materials/validation_terrain_palette.gdshader.uid",
)


def parse_marker(marker: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker.split()[1:] if "=" in token)


def static_audit() -> dict[str, object]:
    errors: list[str] = []
    for relative in PROHIBITED_LOCAL:
        if (ROOT / relative).exists():
            errors.append(f"prohibited validation-game workaround remains: {relative}")
    scene = (ROOT / "scenes/validation_playtest.tscn").read_text(encoding="utf-8")
    playtest = (ROOT / "scripts/validation_playtest.gd").read_text(encoding="utf-8")
    if "wt_terrain_material_applicator.gd" not in scene:
        errors.append("validation scene does not use addon material applicator")
    if "wt_terrain_mesh_stats.gd" not in playtest:
        errors.append("validation playtest does not use addon mesh stats")
    runtime_refs = []
    for path in sorted((ROOT / "scripts").glob("*.gd")):
        text = path.read_text(encoding="utf-8")
        if "get_backend_terrain" in text or "get_backend_world_state_name" in text:
            runtime_refs.append(path.relative_to(ROOT).as_posix())
    historical_backend_tests = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "tests").glob("*.gd"))
        if "get_backend_terrain" in path.read_text(encoding="utf-8")
    ]
    addon_required = (
        "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd",
        "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader",
        "addons/world_transvoxel_terrain/debug/wt_terrain_mesh_stats.gd",
    )
    for relative in addon_required:
        if not (TERRAIN_REPO / relative).is_file():
            errors.append(f"missing addon-owned replacement: {relative}")
    if runtime_refs:
        errors.append(f"runtime scripts still use backend internals: {runtime_refs}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {
        "moved_helpers": 2,
        "local_workaround_files": 0,
        "direct_runtime_backend_refs": 0,
        "quarantined_historical_backend_tests": len(historical_backend_tests),
        "historical_backend_tests": historical_backend_tests,
    }


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
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
    (ARTIFACT_ROOT / f"godot-{version}-g47.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g47.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G47 validation workaround removal failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G47 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("local_workaround_files") != "0":
        raise RuntimeError(f"G47 marker fields invalid: {marker_line}")
    if fields.get("material_impl") != "terrain_addon_material_applicator":
        raise RuntimeError(f"G47 material helper was not addon-owned: {marker_line}")
    if fields.get("mesh_stats_impl") != "terrain_addon_mesh_stats":
        raise RuntimeError(f"G47 mesh stats helper was not addon-owned: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "0")) != 25:
            raise RuntimeError(f"G47 active resource field did not settle to 25: {field} in {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run validation workaround removal quality validation.")
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
    report_path = ARTIFACT_ROOT / "g47_validation_workaround_removal_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} moved_helpers=2 "
        "local_workaround_files=0 direct_runtime_backend_refs=0 "
        f"quarantined_historical_backend_tests={audit['quarantined_historical_backend_tests']} "
        f"quality_track=runtime_terrain dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
