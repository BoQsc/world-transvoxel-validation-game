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


ARTIFACT_ROOT = ROOT / "artifacts" / "g44_edit_policy_shape_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g44_edit_policy_shape_quality.gd"
MARKER = "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS"
MAX_RUNTIME_SECONDS = 90.0


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
        timeout=180,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g44.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g44.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G44 edit policy and shape quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G44 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G44 marker fields invalid: {marker_line}")
    if fields.get("default_shape") != "sphere" or fields.get("alternate_shape_toggles") != "false":
        raise RuntimeError(f"G44 edit policy invalid: {marker_line}")
    if abs(float(fields.get("dig_radius", "0")) - 1.8) > 0.001 or abs(float(fields.get("place_radius", "0")) - 1.8) > 0.001:
        raise RuntimeError(f"G44 radius policy invalid: {marker_line}")
    if int(fields.get("place_material", "0")) != 4 or int(fields.get("edits", "0")) < 6:
        raise RuntimeError(f"G44 edit/material coverage invalid: {marker_line}")
    if int(fields.get("inside_samples", "0")) < 24 or int(fields.get("outside_unchanged_samples", "0")) < 6:
        raise RuntimeError(f"G44 shape sample coverage invalid: {marker_line}")
    if int(fields.get("max_commit_frames", "999")) > 180 or int(fields.get("max_settle_frames", "999")) > 480:
        raise RuntimeError(f"G44 edit latency exceeded budget: {marker_line}")
    if int(fields.get("edit_replacement_delta", "0")) < int(fields.get("edits", "0")):
        raise RuntimeError(f"G44 edit replacements did not track repeated edits: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "0")) != 25:
            raise RuntimeError(f"G44 active resource field did not settle to 25: {field} in {marker_line}")
    if int(fields.get("max_pending_retirements", "1")) != 0 or int(fields.get("max_render_fading_resources", "1")) != 0:
        raise RuntimeError(f"G44 churn/fade field invalid: {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run edit policy and shape quality validation.")
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
    max_commit = max(int(result["fields"]["max_commit_frames"]) for result in results)
    min_inside = min(int(result["fields"]["inside_samples"]) for result in results)
    min_outside = min(int(result["fields"]["outside_unchanged_samples"]) for result in results)
    report_path = ARTIFACT_ROOT / "g44_edit_policy_shape_quality_report.json"
    report_path.write_text(json.dumps({
        "project": str(project),
        "lock": lock,
        "profile": PROFILE_ID,
        "engines": results,
        "max_commit_frames": max_commit,
        "min_inside_samples": min_inside,
        "min_outside_unchanged_samples": min_outside,
        "implementation": "edit_policy_shape_quality",
    }, indent=2) + "\n", encoding="utf-8")
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} edits=6 "
        f"inside_samples={min_inside} outside_unchanged_samples={min_outside} "
        f"max_commit_frames={max_commit} quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
