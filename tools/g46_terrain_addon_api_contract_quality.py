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


ARTIFACT_ROOT = ROOT / "artifacts" / "g46_terrain_addon_api_contract_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g46_terrain_addon_api_contract_quality.gd"
MARKER = "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS"
MAX_RUNTIME_SECONDS = 90.0


def parse_marker(marker: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in marker.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


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
    (ARTIFACT_ROOT / f"godot-{version}-g46.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g46.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G46 terrain addon API contract quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G46 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("api_version") != "1":
        raise RuntimeError(f"G46 marker profile/API fields invalid: {marker_line}")
    for field in ("lifecycle", "streaming", "edits", "storage", "telemetry", "debug", "edit_committed"):
        if fields.get(field) != "1":
            raise RuntimeError(f"G46 public API field failed: {field} in {marker_line}")
    if int(fields.get("public_methods", "0")) < 22 or int(fields.get("stable_groups", "0")) < 7:
        raise RuntimeError(f"G46 public API coverage too small: {marker_line}")
    if int(fields.get("samples", "0")) < 3 or int(fields.get("world_revision_delta", "0")) < 1:
        raise RuntimeError(f"G46 sample/edit coverage too small: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "0")) != 25:
            raise RuntimeError(f"G46 active resource field did not settle to 25: {field} in {marker_line}")
    if fields.get("direct_backend_calls") != "0" or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G46 boundary field invalid: {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run terrain addon API contract quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

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
    report_path = ARTIFACT_ROOT / "g46_terrain_addon_api_contract_quality_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "profile": PROFILE_ID,
                "engines": results,
                "max_duration_seconds": max(float(result["duration_seconds"]) for result in results),
                "implementation": "terrain_addon_api_contract_quality",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} "
        "api_version=1 public_methods=22 stable_groups=7 direct_backend_calls=0 "
        f"quality_track=runtime_terrain dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
