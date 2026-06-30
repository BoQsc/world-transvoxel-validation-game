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
from g19_compact_2k_on_demand_smoke import PROFILE_ID, PROJECT_WORLD_ROOT, assert_compact_project_budget
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g35_terrain_correctness_artifact_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g35_terrain_correctness_artifact_quality.gd"
MARKER = "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS"
MAX_RUNTIME_SECONDS = 45.0


def parse_marker(marker: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in marker.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def reset_compact_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_compact_runtime_state(project)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(project), "--script", SCRIPT],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=120,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g35.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g35.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G35 terrain correctness artifact quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G35 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G35 marker fields invalid: {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run terrain correctness and artifact quality validation.")
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
    max_backend_error = max(float(result["fields"]["max_backend_height_error"]) for result in results)
    max_neighbor_delta = max(float(result["fields"]["max_neighbor_delta"]) for result in results)
    max_diagonal_delta = max(float(result["fields"]["max_diagonal_pair_delta"]) for result in results)
    min_height = min(float(result["fields"]["min_height"]) for result in results)
    max_height = max(float(result["fields"]["max_height"]) for result in results)
    max_duration = max(float(result["duration_seconds"]) for result in results)
    report_path = ARTIFACT_ROOT / "g35_terrain_correctness_artifact_quality_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "profile": PROFILE_ID,
                "engines": results,
                "max_backend_height_error": max_backend_error,
                "max_neighbor_delta": max_neighbor_delta,
                "max_diagonal_pair_delta": max_diagonal_delta,
                "min_height": min_height,
                "max_height": max_height,
                "max_duration_seconds": max_duration,
                "implementation": "terrain_correctness_artifact_quality",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} map_blocks=2048 "
        f"max_backend_height_error={max_backend_error:.4f} "
        f"max_neighbor_delta={max_neighbor_delta:.3f} "
        f"max_diagonal_pair_delta={max_diagonal_delta:.3f} "
        f"min_height={min_height:.3f} max_height={max_height:.3f} "
        "quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
