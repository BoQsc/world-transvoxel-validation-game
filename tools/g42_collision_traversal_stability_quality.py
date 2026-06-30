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
from g3_generation_modes_smoke import copy_worlds_into_project, generate_worlds
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import PROJECT_WORLD_ROOT, assert_compact_project_budget
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g42_collision_traversal_stability_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g42_collision_traversal_stability_quality.gd"
MARKER = "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS"
MAX_RUNTIME_SECONDS = 90.0
MIN_FLOOR_CONTACT_RATIO = 0.72
MIN_TOTAL_MOTION = 45.0


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
    (ARTIFACT_ROOT / f"godot-{version}-g42.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g42.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G42 collision traversal stability quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G42 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if int(fields.get("profile_cases", "0")) < 3 or int(fields.get("route_segments", "0")) < 6:
        raise RuntimeError(f"G42 route coverage invalid: {marker_line}")
    if int(fields.get("edited_segments", "0")) < 1:
        raise RuntimeError(f"G42 edited traversal coverage invalid: {marker_line}")
    if float(fields.get("total_motion", "0")) < MIN_TOTAL_MOTION:
        raise RuntimeError(f"G42 total motion too small: {marker_line}")
    if float(fields.get("min_floor_contact_ratio", "0")) < MIN_FLOOR_CONTACT_RATIO:
        raise RuntimeError(f"G42 floor contact ratio too low: {marker_line}")
    if int(fields.get("max_off_floor_streak", "999")) > 36:
        raise RuntimeError(f"G42 off-floor streak too long: {marker_line}")
    if float(fields.get("min_player_y", "-999")) < -10.0:
        raise RuntimeError(f"G42 player fell below terrain bounds: {marker_line}")
    if float(fields.get("max_abs_vertical_velocity", "999")) > 90.0:
        raise RuntimeError(f"G42 vertical velocity unstable: {marker_line}")
    if int(fields.get("max_render_fading_resources", "1")) != 0:
        raise RuntimeError(f"G42 render fade/blink resources observed: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "999")) > 64:
            raise RuntimeError(f"G42 active resource field exceeded budget: {field} in {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run collision traversal stability quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    bake_results = generate_worlds()
    lock = compose(project)
    copy_worlds_into_project(project)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    min_floor_ratio = min(float(result["fields"]["min_floor_contact_ratio"]) for result in results)
    min_motion = min(float(result["fields"]["total_motion"]) for result in results)
    min_segments = min(int(result["fields"]["route_segments"]) for result in results)
    report_path = ARTIFACT_ROOT / "g42_collision_traversal_stability_quality_report.json"
    report_path.write_text(json.dumps({
        "project": str(project),
        "lock": lock,
        "bake": bake_results,
        "engines": results,
        "min_floor_contact_ratio": min_floor_ratio,
        "min_total_motion": min_motion,
        "min_route_segments": min_segments,
        "implementation": "collision_traversal_stability_quality",
    }, indent=2) + "\n", encoding="utf-8")
    print(
        f"{SUMMARY_MARKER} engines={len(results)} profile_cases=3 route_segments={min_segments} "
        f"total_motion={min_motion:.3f} min_floor_contact_ratio={min_floor_ratio:.3f} "
        "quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
