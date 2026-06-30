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


ARTIFACT_ROOT = ROOT / "artifacts" / "g43_view_distance_presentation_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g43_view_distance_presentation_quality.gd"
MARKER = "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS"
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


def copy_captures(project: Path, version: str) -> list[str]:
    source = project / "artifacts" / "g43_view_distance_presentation_quality"
    copied: list[str] = []
    if source.is_dir():
        for capture in sorted(source.glob("*.png")):
            target = ARTIFACT_ROOT / f"godot-{version}-{capture.name}"
            target.write_bytes(capture.read_bytes())
            copied.append(str(target))
    return copied


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
    (ARTIFACT_ROOT / f"godot-{version}-g43.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g43.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G43 view distance presentation quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G43 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("full_visual_blocks") != "2048x2048" or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G43 marker fields invalid: {marker_line}")
    if int(fields.get("captures", "0")) < 3:
        raise RuntimeError(f"G43 capture coverage invalid: {marker_line}")
    if int(fields.get("min_colored_samples", "0")) < 800:
        raise RuntimeError(f"G43 colored terrain coverage too small: {marker_line}")
    if int(fields.get("min_horizontal_bins", "0")) < 8 or int(fields.get("min_vertical_bins", "0")) < 3:
        raise RuntimeError(f"G43 image terrain span too small: {marker_line}")
    if int(fields.get("min_mid_band_samples", "0")) < 120:
        raise RuntimeError(f"G43 mid-distance terrain coverage too small: {marker_line}")
    if int(fields.get("max_render_resources", "0")) > 25 or int(fields.get("max_collision_resources", "0")) > 25:
        raise RuntimeError(f"G43 local active resources exceeded budget: {marker_line}")
    if int(fields.get("max_render_fading_resources", "1")) != 0:
        raise RuntimeError(f"G43 render fade/blink resources observed: {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "captures": copy_captures(project, version),
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run view distance presentation quality validation.")
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
    min_colored = min(int(result["fields"]["min_colored_samples"]) for result in results)
    min_h_bins = min(int(result["fields"]["min_horizontal_bins"]) for result in results)
    min_mid = min(int(result["fields"]["min_mid_band_samples"]) for result in results)
    report_path = ARTIFACT_ROOT / "g43_view_distance_presentation_quality_report.json"
    report_path.write_text(json.dumps({
        "project": str(project),
        "lock": lock,
        "profile": PROFILE_ID,
        "engines": results,
        "min_colored_samples": min_colored,
        "min_horizontal_bins": min_h_bins,
        "min_mid_band_samples": min_mid,
        "implementation": "view_distance_presentation_quality",
    }, indent=2) + "\n", encoding="utf-8")
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} captures=3 "
        f"min_colored_samples={min_colored} min_horizontal_bins={min_h_bins} "
        f"min_mid_band_samples={min_mid} quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
