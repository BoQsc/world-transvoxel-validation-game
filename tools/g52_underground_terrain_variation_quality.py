#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from compose_validation_project import ROOT, TERRAIN_REPO, WORLD_TRANSVOXEL_REPO, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import PROFILE_ID, PROJECT_WORLD_ROOT, assert_compact_project_budget
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g52_underground_terrain_variation_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g52_underground_terrain_variation_quality.gd"
MARKER = "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS"
FLAT_PROFILE_ID = "flat_baseline"
MAX_RUNTIME_SECONDS = 150.0
NATIVE_CONFIGURATIONS = ("template_debug", "template_release")


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        WORLD_TRANSVOXEL_REPO / "addons/world_transvoxel/src/storage/wt_procedural_world_source.cpp": (
            "WtProceduralTerrainVolumeSource",
            "depth >= 8.0",
            "depth >= 3.0",
            "depth >= 1.0",
        ),
        WORLD_TRANSVOXEL_REPO / "tests/native/test_wt_m5_async_storage.cpp": (
            "procedural underground strata samples mismatch",
            "procedural_strata=1",
        ),
        TERRAIN_REPO / "addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd": (
            "density_volume_vertical_strata_v1",
            "UNDERGROUND_STRATA_MATERIAL_IDS",
            "flat_world_underground_contract",
        ),
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader": (
            "material_1_color",
            "material_7_color",
        ),
        ROOT / "tests/g52_underground_terrain_variation_quality.gd": (
            MARKER,
            "PROCEDURAL_POINTS",
            "FLAT_POINTS",
            "edit_localized=1",
        ),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.is_file():
            errors.append(f"missing G52 input: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing phrase: {phrase}")
        if path.suffix in {".gd", ".py", ".gdshader"} and len(text.splitlines()) > 300:
            errors.append(f"G52 source file exceeds line limit: {path}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "underground_terrain_variation_quality", "profile": PROFILE_ID}


def native_test_path(configuration: str, test_name: str) -> Path:
    scripts_path = str(WORLD_TRANSVOXEL_REPO / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    from wt_script_common import native_test_path as resolve_native_test_path

    return resolve_native_test_path(configuration, test_name)


def run_native_strata_tests() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for configuration in NATIVE_CONFIGURATIONS:
        executable = native_test_path(configuration, "test_wt_m5_async_storage")
        if not executable.is_file():
            raise RuntimeError(f"missing native test executable: {executable}")
        started_at = time.perf_counter()
        result = subprocess.run(
            [str(executable)],
            cwd=WORLD_TRANSVOXEL_REPO,
            check=False,
            text=True,
            capture_output=True,
            errors="replace",
            timeout=120,
        )
        duration_seconds = time.perf_counter() - started_at
        combined = result.stdout + result.stderr
        (ARTIFACT_ROOT / f"native-{configuration}-g52.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (ARTIFACT_ROOT / f"native-{configuration}-g52.stderr.txt").write_text(result.stderr, encoding="utf-8")
        print(combined, end="" if combined.endswith("\n") else "\n")
        if result.returncode != 0 or "M5_ASYNC_STORAGE_PASS" not in combined or "procedural_strata=1" not in combined:
            raise RuntimeError(f"G52 native strata test failed for {configuration}")
        results.append({
            "configuration": configuration,
            "duration_seconds": duration_seconds,
            "marker": next(line for line in combined.splitlines() if line.startswith("M5_ASYNC_STORAGE_PASS")),
        })
    return results


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
        timeout=240,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g52.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g52.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G52 underground terrain variation failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G52 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("flat_profile") != FLAT_PROFILE_ID:
        raise RuntimeError(f"G52 marker profile fields invalid: {marker_line}")
    if fields.get("density_ordered") != "1" or fields.get("edit_localized") != "1":
        raise RuntimeError(f"G52 density/edit fields invalid: {marker_line}")
    if fields.get("strata_materials") != "1,7,4" or fields.get("flat_material") != "7":
        raise RuntimeError(f"G52 material fields invalid: {marker_line}")
    if int(fields.get("strata_samples", "0")) != 3 or int(fields.get("flat_volume_samples", "0")) != 3:
        raise RuntimeError(f"G52 sample coverage invalid: {marker_line}")
    return {
        "engine": version,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G52 underground terrain variation quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    native_results = run_native_strata_tests()
    project = arguments.project.resolve()
    lock = compose(project)
    reset_runtime_state(project)
    engines = discover_engines(arguments.godot)
    runtime_results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        runtime_results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "g52_underground_terrain_variation_quality_report.json"
    report_path.write_text(
        json.dumps({
            "project": str(project),
            "lock": lock,
            "audit": audit,
            "native": native_results,
            "engines": runtime_results,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in runtime_results)
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} flat_profile={FLAT_PROFILE_ID} "
        f"engines={len(runtime_results)} native_configs={len(native_results)} "
        f"strata_materials=1,7,4 edit_localized=1 max_engine_seconds={max_duration:.3f} "
        f"dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
